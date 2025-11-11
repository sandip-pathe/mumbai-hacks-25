"""
Model Context Protocol (MCP) tool definitions.
Standardized tool calling for LangGraph agents.
"""
from typing import List, Dict, Any, Optional
import logging
from utils.chroma_store import chroma_store
from utils.azure_client import azure_client
from utils.slack_notifier import slack_notifier
from utils.pdf_parser import parse_pdf_with_pdfplumber
from utils.neon_client import neon_client
import asyncio

logger = logging.getLogger(__name__)

class MCPToolRegistry:
    """Registry of MCP-compatible tools for agents."""
    
    def __init__(self):
        self.tools: Dict[str, Dict[str, Any]] = {}
        self._register_tools()
    
    def _register_tools(self):
        """Register all available tools."""
        
        # Vector DB tools
        self.register(
            name="query_vector_db",
            description="Search Qdrant for relevant policy or circular chunks",
            parameters={
                "query": {"type": "string", "description": "Search query text"},
                "collection": {"type": "string", "description": "Collection name (rbi_circulars or company_policies)"},
                "limit": {"type": "integer", "description": "Max results", "default": 5}
            },
            function=self.query_vector_db
        )
        
        # Embedding tools
        self.register(
            name="embed_text",
            description="Generate embeddings for text using Azure OpenAI",
            parameters={
                "text": {"type": "string", "description": "Text to embed"}
            },
            function=self.embed_text
        )
        
        # Scoring tools
        self.register(
            name="calculate_compliance_score",
            description="Calculate compliance score based on policy diffs",
            parameters={
                "diffs": {"type": "array", "description": "List of policy diff dicts"}
            },
            function=self.calculate_compliance_score
        )
        
        # Notification tools
        self.register(
            name="send_slack_alert",
            description="Send a compliance alert to Slack",
            parameters={
                "message": {"type": "string", "description": "Alert message"},
                "severity": {"type": "string", "description": "Alert severity (info/warning/critical)", "default": "info"}
            },
            function=self.send_slack_alert
        )
        
        # PDF tools
        self.register(
            name="parse_pdf",
            description="Extract text from PDF file",
            parameters={
                "file_path": {"type": "string", "description": "Path to PDF file"}
            },
            function=self.parse_pdf
        )
        
        # Database tools
        self.register(
            name="store_agent_log",
            description="Store agent execution log in database",
            parameters={
                "agent_name": {"type": "string", "description": "Agent identifier"},
                "action": {"type": "string", "description": "Action performed"},
                "status": {"type": "string", "description": "Status (success/error)"},
                "metadata": {"type": "object", "description": "Additional metadata", "default": {}}
            },
            function=self.store_agent_log
        )
    
    def register(self, name: str, description: str, parameters: Dict, function):
        """Register a new tool."""
        self.tools[name] = {
            "name": name,
            "description": description,
            "parameters": parameters,
            "function": function
        }
        logger.info(f"✅ Registered MCP tool: {name}")
    
    async def call_tool(self, name: str, **kwargs) -> Any:
        """Call a registered tool by name."""
        if name not in self.tools:
            raise ValueError(f"Tool '{name}' not found in registry")
        
        tool = self.tools[name]
        function = tool["function"]
        
        try:
            logger.info(f"🔧 Calling MCP tool: {name} with args: {kwargs}")
            result = await function(**kwargs)
            logger.info(f"✅ MCP tool {name} completed successfully")
            return result
        except Exception as e:
            logger.error(f"❌ MCP tool {name} failed: {e}")
            raise
    
    def get_tool_specs(self) -> List[Dict[str, Any]]:
        """Get all tool specifications for LLM function calling."""
        return [
            {
                "name": tool["name"],
                "description": tool["description"],
                "parameters": {
                    "type": "object",
                    "properties": tool["parameters"],
                    "required": [
                        k for k, v in tool["parameters"].items() 
                        if v.get("default") is None
                    ]
                }
            }
            for tool in self.tools.values()
        ]
    
    # Tool implementations
    
    async def query_vector_db(
        self, 
        query: str, 
        collection: str = "company_policies",
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Search vector database for relevant chunks."""
        if collection == "rbi_circulars":
            results = await chroma_store.query_circulars(query, limit)
        else:
            results = await chroma_store.query_policies(query, limit)
        return results
    
    async def embed_text(self, text: str) -> List[float]:
        """Generate embeddings for text."""
        embeddings = await azure_client.generate_embeddings([text])
        return embeddings[0] if embeddings else []
    
    async def calculate_compliance_score(self, diffs: List[Dict[str, Any]]) -> float:
        """
        Calculate compliance score based on policy diffs.
        Simple algorithm: score = 1.0 - (num_critical_diffs * 0.2) - (num_warnings * 0.1)
        """
        if not diffs:
            return 1.0
        
        critical_count = sum(1 for d in diffs if d.get("severity") == "critical")
        warning_count = sum(1 for d in diffs if d.get("severity") == "warning")
        
        score = 1.0 - (critical_count * 0.2) - (warning_count * 0.1)
        return max(0.0, min(1.0, score))  # Clamp to [0, 1]
    
    async def send_slack_alert(
        self, 
        message: str, 
        severity: str = "info"
    ) -> bool:
        """Send alert to Slack."""
        emoji = {
            "info": "ℹ️",
            "warning": "⚠️",
            "critical": "🚨"
        }.get(severity, "📢")
        
        title = f"{emoji} Compliance Alert"
        success = await slack_notifier.send_notification(
            title=title,
            message=message,
            severity=severity if severity in ["critical", "high", "medium", "low", "info"] else "info"
        )
        return success
    
    async def parse_pdf(self, file_path: str) -> str:
        """Extract text from PDF."""
        result = await parse_pdf_with_pdfplumber(file_path)
        return result.get("text", "")
    
    async def store_agent_log(
        self,
        agent_name: str,
        action: str,
        status: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[int]:
        """Store agent execution log."""
        import json
        from datetime import datetime
        
        log_data = {
            "agent_name": agent_name,
            "action": action,
            "status": status,
            "metadata": json.dumps(metadata or {}),
            "started_at": datetime.utcnow().isoformat(),
            "completed_at": datetime.utcnow().isoformat()
        }
        
        # Use Neon Data API to insert (fallback to None if not configured)
        try:
            log_id = await neon_client.insert("agent_logs", log_data)
            return log_id
        except Exception as e:
            logger.warning(f"Could not store agent log via Neon API: {e}")
            return None

# Singleton instance
mcp_tools = MCPToolRegistry()
