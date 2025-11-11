"""
LangGraph workflow orchestration with MCP tool integration.
Defines the multi-agent compliance automation state machine.
"""
from typing import TypedDict, Annotated, List, Dict, Any, Literal
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from graph.mcp_tools import mcp_tools
from utils.azure_client import azure_client
from utils.chroma_store import chroma_store
from utils.redis_client import redis_client, CHANNEL_POLICY_UPDATED, CHANNEL_SCORE_UPDATED
from config import settings
import logging
import json

logger = logging.getLogger(__name__)

# Define state schema
class ComplianceWorkflowState(TypedDict):
    """State shared across all agents in the workflow."""
    circular_id: str
    circular_text: str
    chunks: List[str]
    embeddings: List[List[float]]
    relevant_policies: List[Dict[str, Any]]
    diffs: List[Dict[str, Any]]
    compliance_score: float
    alert_sent: bool
    error: str

# Agent node implementations

async def regulatory_watch_node(state: ComplianceWorkflowState) -> Dict[str, Any]:
    """
    Regulatory Watch Agent: Parse PDF, chunk text, generate embeddings.
    """
    logger.info(f"[Regulatory Watch] Processing circular: {state['circular_id']}")
    
    try:
        # Get text from state (assumed already extracted)
        text = state.get("circular_text", "")
        
        if not text:
            logger.warning("[Regulatory Watch] No circular text provided")
            return {"error": "No circular text"}
        
        # Chunk text
        chunks = chroma_store.chunk_text(text)
        logger.info(f"[Regulatory Watch] Created {len(chunks)} chunks")
        
        # Generate embeddings using MCP tool (batch first 5 for demo)
        embeddings = []
        for chunk in chunks[:5]:
            try:
                embedding = await mcp_tools.call_tool("embed_text", text=chunk)
                embeddings.append(embedding)
            except Exception as e:
                logger.error(f"[Regulatory Watch] Embedding failed for chunk: {e}")
        
        # Store in Qdrant
        if embeddings:
            await chroma_store.add_circular_chunks(
                state["circular_id"], 
                chunks[:5],
                embeddings
            )
            logger.info(f"[Regulatory Watch] Stored {len(embeddings)} embeddings in Qdrant")
        
        # Log action using MCP
        await mcp_tools.call_tool(
            "store_agent_log",
            agent_name="regulatory_watch",
            action="parse_and_embed",
            status="success",
            metadata={"circular_id": state["circular_id"], "chunk_count": len(chunks)}
        )
        
        return {
            "chunks": chunks,
            "embeddings": embeddings,
            "error": ""
        }
    
    except Exception as e:
        logger.error(f"[Regulatory Watch] Error: {e}")
        return {"error": str(e)}

async def policy_automation_node(state: ComplianceWorkflowState) -> Dict[str, Any]:
    """
    Policy Automation Agent: Compare circular against company policies using RAG.
    """
    logger.info(f"[Policy Automation] Comparing circular: {state['circular_id']}")
    
    try:
        # Query vector DB for relevant policies using MCP tool
        query_text = state.get("circular_text", "")[:500]  # Use first 500 chars
        policies = await mcp_tools.call_tool(
            "query_vector_db",
            query=query_text,
            collection="company_policies",
            limit=5
        )
        
        logger.info(f"[Policy Automation] Found {len(policies)} relevant policies")
        
        # Use LLM to identify diffs
        if policies:
            prompt = f"""
Compare the following RBI circular against our company policies and identify gaps or compliance issues.

RBI Circular Summary:
{query_text}

Relevant Company Policies:
{json.dumps([p.get('document', '')[:200] for p in policies], indent=2)}

Return a JSON array of compliance gaps with this exact format:
[{{"gap": "description of the gap", "severity": "critical|warning|info", "affected_policy": "policy name"}}]

If no gaps found, return an empty array: []
"""
            
            response = await azure_client.generate_completion([
                {"role": "system", "content": "You are a compliance analyst. Always return valid JSON."},
                {"role": "user", "content": prompt}
            ])
            
            # Try to parse LLM response as JSON
            try:
                diffs = json.loads(response)
                if not isinstance(diffs, list):
                    diffs = [{"gap": response, "severity": "warning", "affected_policy": "unknown"}]
            except json.JSONDecodeError:
                # Fallback: create single diff from text response
                diffs = [{"gap": response[:500], "severity": "warning", "affected_policy": "unknown"}]
        else:
            diffs = []
            logger.info("[Policy Automation] No relevant policies found, no diffs generated")
        
        # Publish event to Redis
        await redis_client.publish(
            CHANNEL_POLICY_UPDATED,
            {"circular_id": state["circular_id"], "diff_count": len(diffs)}
        )
        
        # Log action
        await mcp_tools.call_tool(
            "store_agent_log",
            agent_name="policy_automation",
            action="compare_policies",
            status="success",
            metadata={"diff_count": len(diffs), "policies_queried": len(policies)}
        )
        
        return {
            "relevant_policies": policies,
            "diffs": diffs,
            "error": ""
        }
    
    except Exception as e:
        logger.error(f"[Policy Automation] Error: {e}")
        return {"error": str(e)}

async def audit_prep_node(state: ComplianceWorkflowState) -> Dict[str, Any]:
    """
    Audit Prep Agent: Calculate compliance score based on diffs.
    """
    logger.info("[Audit Prep] Calculating compliance score")
    
    try:
        # Calculate score using MCP tool
        score = await mcp_tools.call_tool(
            "calculate_compliance_score",
            diffs=state.get("diffs", [])
        )
        
        logger.info(f"[Audit Prep] Calculated score: {score:.2%}")
        
        # Store score in database via Neon Data API
        from utils.neon_client import neon_client
        from datetime import datetime
        
        try:
            await neon_client.insert("compliance_scores", {
                "score": score,
                "circular_id": state["circular_id"],
                "timestamp": datetime.utcnow().isoformat()
            })
        except Exception as db_error:
            logger.warning(f"[Audit Prep] Could not store score in DB: {db_error}")
        
        # Publish event to Redis
        await redis_client.publish(
            CHANNEL_SCORE_UPDATED,
            {"circular_id": state["circular_id"], "score": score}
        )
        
        # Log action
        await mcp_tools.call_tool(
            "store_agent_log",
            agent_name="audit_prep",
            action="calculate_score",
            status="success",
            metadata={"score": score, "diff_count": len(state.get("diffs", []))}
        )
        
        return {
            "compliance_score": score,
            "error": ""
        }
    
    except Exception as e:
        logger.error(f"[Audit Prep] Error: {e}")
        return {"error": str(e)}

async def alert_node(state: ComplianceWorkflowState) -> Dict[str, Any]:
    """
    Alert Node: Send Slack notification if score is low.
    """
    logger.info("[Alert] Sending compliance alert")
    
    try:
        score = state.get("compliance_score", 1.0)
        severity = "critical" if score < 0.7 else "warning"
        
        message = f"Compliance score for circular {state['circular_id']} is {score:.1%}. Review required."
        
        # Add diff summary if available
        diffs = state.get("diffs", [])
        if diffs:
            critical = sum(1 for d in diffs if d.get("severity") == "critical")
            warnings = sum(1 for d in diffs if d.get("severity") == "warning")
            message += f"\n\n{critical} critical issues, {warnings} warnings detected."
        
        # Send alert using MCP tool
        success = await mcp_tools.call_tool(
            "send_slack_alert",
            message=message,
            severity=severity
        )
        
        logger.info(f"[Alert] Alert sent: {success}")
        
        return {
            "alert_sent": success,
            "error": ""
        }
    
    except Exception as e:
        logger.error(f"[Alert] Error: {e}")
        return {"error": str(e)}

# Conditional edge function
def should_send_alert(state: ComplianceWorkflowState) -> Literal["alert", "skip"]:
    """Decide whether to send alert based on score."""
    score = state.get("compliance_score", 1.0)
    if score < 0.8:
        logger.info(f"[Router] Score {score:.1%} < 80%, routing to alert")
        return "alert"
    else:
        logger.info(f"[Router] Score {score:.1%} >= 80%, skipping alert")
        return "skip"

# Build the workflow graph
def build_compliance_workflow() -> StateGraph:
    """Construct the LangGraph workflow."""
    
    workflow = StateGraph(ComplianceWorkflowState)
    
    # Add nodes
    workflow.add_node("regulatory_watch", regulatory_watch_node)
    workflow.add_node("policy_automation", policy_automation_node)
    workflow.add_node("audit_prep", audit_prep_node)
    workflow.add_node("alert", alert_node)
    
    # Define edges
    workflow.set_entry_point("regulatory_watch")
    workflow.add_edge("regulatory_watch", "policy_automation")
    workflow.add_edge("policy_automation", "audit_prep")
    
    # Conditional edge: alert or skip
    workflow.add_conditional_edges(
        "audit_prep",
        should_send_alert,
        {
            "alert": "alert",
            "skip": END
        }
    )
    workflow.add_edge("alert", END)
    
    # Compile with checkpointer (use memory for now, can swap to Neon-backed later)
    if settings.LANGGRAPH_CHECKPOINT_ENABLED:
        checkpointer = MemorySaver()
        graph = workflow.compile(checkpointer=checkpointer)
        logger.info("✅ LangGraph compliance workflow compiled with checkpointing")
    else:
        graph = workflow.compile()
        logger.info("✅ LangGraph compliance workflow compiled (no checkpointing)")
    
    return graph

# Singleton workflow instance
compliance_workflow = build_compliance_workflow()

# Convenience function to run workflow
async def run_compliance_workflow(circular_id: str, circular_text: str) -> Dict[str, Any]:
    """
    Run the full compliance workflow for a circular.
    
    Args:
        circular_id: Unique ID of the circular
        circular_text: Full text content of the circular
    
    Returns:
        Final state after workflow completion
    """
    initial_state: ComplianceWorkflowState = {
        "circular_id": circular_id,
        "circular_text": circular_text,
        "chunks": [],
        "embeddings": [],
        "relevant_policies": [],
        "diffs": [],
        "compliance_score": 0.0,
        "alert_sent": False,
        "error": ""
    }
    
    logger.info(f"🚀 Starting compliance workflow for circular: {circular_id}")
    
    try:
        # Run graph (async invoke)
        final_state = await compliance_workflow.ainvoke(initial_state)
        
        logger.info(f"✅ Workflow completed for {circular_id}")
        logger.info(f"   - Score: {final_state.get('compliance_score', 0):.1%}")
        logger.info(f"   - Diffs: {len(final_state.get('diffs', []))}")
        logger.info(f"   - Alert sent: {final_state.get('alert_sent', False)}")
        
        return final_state
    
    except Exception as e:
        logger.error(f"❌ Workflow failed for {circular_id}: {e}")
        raise
