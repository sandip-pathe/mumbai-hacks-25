"""
Azure OpenAI and Document Intelligence client
Handles LLM calls, embeddings, and PDF parsing
"""
from openai import AzureOpenAI
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
from config import settings
import logging
from typing import List, Dict, Optional
import asyncio

logger = logging.getLogger(__name__)


class AzureAIClient:
    """Unified client for Azure OpenAI and Document Intelligence"""
    
    def __init__(self):
        # Azure OpenAI Client
        self.openai_client = AzureOpenAI(
            api_key=settings.AZURE_OPENAI_KEY,
            api_version=settings.AZURE_OPENAI_API_VERSION,
            azure_endpoint=settings.AZURE_OPENAI_ENDPOINT
        )
        
        # Document Intelligence Client
        self.doc_intel_client = DocumentAnalysisClient(
            endpoint=settings.AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT,
            credential=AzureKeyCredential(settings.AZURE_DOCUMENT_INTELLIGENCE_KEY)
        )
        
        logger.info("✅ Azure AI clients initialized")
    
    
    async def generate_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> str:
        """
        Generate chat completion using Azure OpenAI GPT-4o
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated text response
        """
        try:
            response = await asyncio.to_thread(
                self.openai_client.chat.completions.create,
                model=settings.AZURE_OPENAI_DEPLOYMENT_NAME,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"❌ Azure OpenAI completion failed: {e}")
            raise
    
    
    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings using Azure OpenAI text-embedding-3-small
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            List of embedding vectors
        """
        try:
            response = await asyncio.to_thread(
                self.openai_client.embeddings.create,
                model=settings.AZURE_OPENAI_EMBEDDING_DEPLOYMENT,
                input=texts
            )
            return [item.embedding for item in response.data]
            
        except Exception as e:
            logger.error(f"❌ Embedding generation failed: {e}")
            raise
    
    
    async def parse_pdf_with_document_intelligence(
        self,
        pdf_path: str
    ) -> Dict[str, any]:
        """
        Parse PDF using Azure Document Intelligence (Form Recognizer)
        Extracts text, tables, key-value pairs
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Dict with 'text', 'tables', 'key_value_pairs'
        """
        try:
            with open(pdf_path, "rb") as pdf_file:
                poller = await asyncio.to_thread(
                    self.doc_intel_client.begin_analyze_document,
                    "prebuilt-document",
                    pdf_file
                )
                result = await asyncio.to_thread(poller.result)
            
            # Extract full text
            full_text = result.content
            
            # Extract tables
            tables = []
            for table in result.tables:
                table_data = {
                    "row_count": table.row_count,
                    "column_count": table.column_count,
                    "cells": [
                        {
                            "row": cell.row_index,
                            "col": cell.column_index,
                            "text": cell.content
                        }
                        for cell in table.cells
                    ]
                }
                tables.append(table_data)
            
            # Extract key-value pairs
            key_value_pairs = {}
            if result.key_value_pairs:
                for kv in result.key_value_pairs:
                    if kv.key and kv.value:
                        key_value_pairs[kv.key.content] = kv.value.content
            
            logger.info(f"✅ PDF parsed: {len(full_text)} chars, {len(tables)} tables")
            
            return {
                "text": full_text,
                "tables": tables,
                "key_value_pairs": key_value_pairs,
                "page_count": len(result.pages)
            }
            
        except Exception as e:
            logger.error(f"❌ Document Intelligence parsing failed: {e}")
            raise
    
    
    async def analyze_circular_content(
        self,
        circular_text: str,
        policy_content: str
    ) -> Dict[str, any]:
        """
        Use GPT-4o to analyze circular against existing policy
        Identifies conflicts, updates, new requirements
        
        Args:
            circular_text: Text from new RBI circular
            policy_content: Existing company policy text
            
        Returns:
            Analysis with diff_type, severity, description, recommendation
        """
        prompt = f"""You are a fintech compliance expert analyzing a new RBI circular.

**New RBI Circular:**
{circular_text[:4000]}

**Existing Company Policy:**
{policy_content[:2000]}

Analyze the circular and identify:
1. Any new requirements not covered by existing policy
2. Changes to existing thresholds or limits
3. Direct conflicts with current policy
4. Compliance gaps

Respond in JSON format:
{{
    "has_impact": true/false,
    "diff_type": "new_requirement|updated_threshold|conflicting|no_impact",
    "severity": "critical|high|medium|low",
    "affected_section": "section reference",
    "description": "detailed description of the change",
    "recommendation": "specific action to take"
}}
"""
        
        try:
            messages = [
                {"role": "system", "content": "You are a compliance analysis expert."},
                {"role": "user", "content": prompt}
            ]
            
            response_text = await self.generate_completion(messages, temperature=0.3)
            
            # Parse JSON response (simple extraction)
            import json
            # Remove markdown code fences if present
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0]
            
            analysis = json.loads(response_text.strip())
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Circular analysis failed: {e}")
            return {
                "has_impact": False,
                "diff_type": "error",
                "severity": "low",
                "description": f"Analysis failed: {str(e)}",
                "recommendation": "Manual review required"
            }


# Global client instance
azure_client = AzureAIClient()
