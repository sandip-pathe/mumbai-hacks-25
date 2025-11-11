"""
Advisory Agent
RAG-based chatbot for compliance queries
Answers questions using embedded circular and policy knowledge
"""
import logging
from typing import Dict, Any, List
from utils.azure_client import azure_client
from utils.chroma_store import chroma_store

logger = logging.getLogger(__name__)


class AdvisoryAgent:
    """
    Agent that answers compliance questions using RAG
    Queries Chroma vector store and generates responses with GPT-4o
    """
    
    def __init__(self):
        self.name = "AdvisoryAgent"
    
    async def answer_query(self, user_query: str) -> Dict[str, Any]:
        """
        Answer user query using RAG
        
        Args:
            user_query: Natural language question
            
        Returns:
            Dict with 'answer', 'sources', 'confidence'
        """
        try:
            logger.info(f"💬 {self.name} processing query: {user_query[:100]}")
            
            # Step 1: Retrieve relevant chunks from Chroma
            circular_results = await chroma_store.query_circulars(user_query, top_k=5)
            policy_results = await chroma_store.query_policies(user_query, top_k=3)
            
            # Step 2: Build context from retrieved chunks
            context_parts = []
            sources = []
            
            for result in circular_results:
                context_parts.append(f"[RBI Circular: {result['metadata'].get('title', 'Unknown')}]\n{result['document']}")
                sources.append({
                    "type": "circular",
                    "title": result['metadata'].get('title', 'Unknown'),
                    "date": result['metadata'].get('date', 'Unknown')
                })
            
            for result in policy_results:
                context_parts.append(f"[Company Policy: {result['metadata'].get('policy_name', 'Unknown')}]\n{result['document']}")
                sources.append({
                    "type": "policy",
                    "name": result['metadata'].get('policy_name', 'Unknown')
                })
            
            context = "\n\n---\n\n".join(context_parts[:5])  # Limit context
            
            # Step 3: Generate answer using GPT-4o
            system_prompt = """You are a fintech compliance expert assistant. 
            Answer user questions based ONLY on the provided context from RBI circulars and company policies.
            If the context doesn't contain enough information, say so clearly.
            Be precise, cite specific sections, and provide actionable insights."""
            
            user_prompt = f"""**Context:**
{context}

**User Question:**
{user_query}

**Answer:**"""
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            answer = await azure_client.generate_completion(messages, temperature=0.3, max_tokens=800)
            
            # Calculate confidence (simple heuristic based on retrieval distances)
            avg_distance = sum(r['distance'] for r in circular_results + policy_results) / len(circular_results + policy_results) if circular_results or policy_results else 1.0
            confidence = max(0, min(100, int((1 - avg_distance) * 100)))
            
            logger.info(f"✅ {self.name} answered query (confidence: {confidence}%)")
            
            return {
                "answer": answer,
                "sources": sources[:5],
                "confidence": confidence,
                "chunks_retrieved": len(circular_results) + len(policy_results)
            }
            
        except Exception as e:
            logger.error(f"❌ {self.name} query failed: {e}")
            return {
                "answer": "I encountered an error processing your query. Please try again.",
                "sources": [],
                "confidence": 0,
                "error": str(e)
            }