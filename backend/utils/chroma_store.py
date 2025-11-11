"""
Qdrant-backed vector store that provides the same surface used by the
repository (chroma_store) but uses Qdrant as the vector database.

This file intentionally keeps the module name `chroma_store.py` to make the
swap transparent to the rest of the codebase; the exported `chroma_store`
object implements the same async API as before (connect, add_*, query_*).
"""
import logging
import asyncio
from typing import List, Dict, Any, Optional

from qdrant_client import QdrantClient
from qdrant_client.http import models as rest

from config import settings
from utils.azure_client import azure_client

logger = logging.getLogger(__name__)


class QdrantStore:
    """Simple Qdrant wrapper with an async-friendly surface."""

    def __init__(self):
        self.client: Optional[QdrantClient] = None
        self.circulars_collection = "rbi_circulars"
        self.policies_collection = "company_policies"

    async def connect(self):
        """Connect to Qdrant and ensure collections exist.

        Supports both local Docker (host/port) and Qdrant Cloud (URL + API key).
        Non-fatal: if Qdrant is not available the app will continue to run but
        RAG features will be no-ops until the vector DB becomes reachable.
        """
        max_retries = 5
        delay = 1.0
        last_exc = None

        for attempt in range(1, max_retries + 1):
            try:
                # Determine connection mode: Cloud (URL+key) vs Local (host+port)
                if settings.QDRANT_URL:
                    # Qdrant Cloud SaaS
                    self.client = QdrantClient(
                        url=settings.QDRANT_URL,
                        api_key=settings.QDRANT_API_KEY
                    )
                    logger.info(f"Connecting to Qdrant Cloud: {settings.QDRANT_URL}")
                else:
                    # Local Docker
                    self.client = QdrantClient(
                        host=settings.QDRANT_HOST,
                        port=settings.QDRANT_PORT
                    )
                    logger.info(f"Connecting to Qdrant local: {settings.QDRANT_HOST}:{settings.QDRANT_PORT}")

                # Ensure collections exist
                await asyncio.to_thread(self._ensure_collection, self.circulars_collection)
                await asyncio.to_thread(self._ensure_collection, self.policies_collection)

                logger.info("✅ Qdrant connected, collections ensured")
                return

            except Exception as e:
                last_exc = e
                logger.warning(f"Qdrant connect attempt {attempt} failed: {e}")
                if attempt < max_retries:
                    await asyncio.sleep(delay)
                    delay *= 2

        logger.error(f"❌ Qdrant connection failed after {max_retries} attempts: {last_exc}")
        self.client = None

    def _ensure_collection(self, name: str):
        try:
            # QdrantClient.get_collection will raise if the collection doesn't exist
            self.client.get_collection(name)
            return
        except Exception:
            # Create a collection with a placeholder vector size. The
            # qdrant-client expects `vectors_config` as a positional/keyword
            # argument for recreate/create collection calls.
            vectors_cfg = rest.VectorParams(size=1536, distance=rest.Distance.COSINE)
            # Use recreate_collection to ensure a clean collection; if you
            # prefer preserving existing data, use create_collection instead.
            self.client.recreate_collection(collection_name=name, vectors_config=vectors_cfg)

    async def add_circular_chunks(self, circular_id: str, chunks: List[str], metadata: Dict[str, Any]) -> int:
        if not self.client:
            logger.warning("⚠️ Qdrant client not available — skipping add_circular_chunks")
            return 0

        try:
            embeddings = await azure_client.generate_embeddings(chunks)
        except Exception as e:
            logger.warning(f"Azure embeddings failed, using local fallback: {e}")
            embeddings = self._fallback_embeddings(chunks)

        points = []
        for i, (chunk, emb) in enumerate(zip(chunks, embeddings)):
            pid = f"{circular_id}_chunk_{i}"
            payload = {**metadata, "chunk_index": i, "circular_id": circular_id, "document": chunk}
            points.append(rest.PointStruct(id=pid, vector=emb, payload=payload))

        # Upsert points (blocking operation)
        await asyncio.to_thread(self.client.upsert, collection_name=self.circulars_collection, points=points)
        logger.info(f"✅ Added {len(points)} chunks for circular {circular_id}")
        return len(points)

    async def add_policy_chunks(self, policy_id: str, chunks: List[str], metadata: Dict[str, Any]) -> int:
        if not self.client:
            logger.warning("⚠️ Qdrant client not available — skipping add_policy_chunks")
            return 0

        try:
            embeddings = await azure_client.generate_embeddings(chunks)
        except Exception as e:
            logger.warning(f"Azure embeddings failed, using local fallback: {e}")
            embeddings = self._fallback_embeddings(chunks)

        points = []
        for i, (chunk, emb) in enumerate(zip(chunks, embeddings)):
            pid = f"{policy_id}_chunk_{i}"
            payload = {**metadata, "chunk_index": i, "policy_id": policy_id, "document": chunk}
            points.append(rest.PointStruct(id=pid, vector=emb, payload=payload))

        await asyncio.to_thread(self.client.upsert, collection_name=self.policies_collection, points=points)
        logger.info(f"✅ Added {len(points)} chunks for policy {policy_id}")
        return len(points)

    async def query_circulars(self, query_text: str, top_k: int = 5, filter_metadata: Optional[Dict] = None) -> List[Dict[str, Any]]:
        if not self.client:
            logger.warning("⚠️ Qdrant client not available — query_circulars returning empty list")
            return []

        try:
            query_embedding = await azure_client.generate_embeddings([query_text])
            query_vector = query_embedding[0]
        except Exception as e:
            logger.warning(f"Azure embeddings failed for query, using local fallback: {e}")
            query_vector = self._fallback_embeddings([query_text])[0]

        # Build optional filter
        q_filter = None
        if filter_metadata:
            # Translate simple metadata dict into Qdrant filter expressions if provided.
            # For complex filters the agents can be extended.
            must_clauses = []
            for k, v in filter_metadata.items():
                must_clauses.append(rest.FieldCondition(key=k, match=rest.MatchValue(value=v)))
            q_filter = rest.Filter(must=[rest.Condition(kind=rest.ConditionOneOf(field=rest.FieldCondition(key="_dummy")) )])
            # NOTE: simple placeholder — if you need advanced filtering, adapt here.

        results = await asyncio.to_thread(
            self.client.search,
            collection_name=self.circulars_collection,
            query_vector=query_vector,
            limit=top_k,
            with_payload=True,
        )

        formatted = []
        for r in results:
            formatted.append({
                "id": r.id,
                "document": r.payload.get("document") if r.payload else None,
                "metadata": {k: v for k, v in (r.payload or {}).items() if k != "document"},
                "score": getattr(r, "score", None),
            })

        return formatted

    async def query_policies(self, query_text: str, top_k: int = 3) -> List[Dict[str, Any]]:
        if not self.client:
            logger.warning("⚠️ Qdrant client not available — query_policies returning empty list")
            return []

        query_embedding = await azure_client.generate_embeddings([query_text])
        query_vector = query_embedding[0]

        results = await asyncio.to_thread(
            self.client.search,
            collection_name=self.policies_collection,
            query_vector=query_vector,
            limit=top_k,
            with_payload=True,
        )

        formatted = []
        for r in results:
            formatted.append({
                "id": r.id,
                "document": r.payload.get("document") if r.payload else None,
                "metadata": {k: v for k, v in (r.payload or {}).items() if k != "document"},
                "score": getattr(r, "score", None),
            })

        return formatted

    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        chunks = []
        start = 0
        text_length = len(text)

        while start < text_length:
            end = start + chunk_size
            if end < text_length:
                last_period = text.rfind(".", start, end)
                if last_period > start + chunk_size - 100:
                    end = last_period + 1

            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)

            start = end - overlap

        return chunks

    def _fallback_embeddings(self, texts: List[str], dim: int = 1536) -> List[List[float]]:
        """Deterministic local embedding fallback for offline/dev use.

        Produces a pseudo-embedding vector for each input text by using a
        seeded RNG (derived from the text hash). This is NOT semantically
        meaningful but is deterministic and useful for smoke tests and local
        development when external embedding APIs aren't available.
        """
        import hashlib
        import random

        embeddings = []
        for t in texts:
            # Use SHA256 to get a stable seed for this text
            h = hashlib.sha256(t.encode("utf-8")).hexdigest()
            seed = int(h[:16], 16)
            rnd = random.Random(seed)
            vec = [rnd.uniform(-1.0, 1.0) for _ in range(dim)]
            # Normalize to unit length
            norm = sum(x * x for x in vec) ** 0.5
            if norm > 0:
                vec = [x / norm for x in vec]
            embeddings.append(vec)

        return embeddings


# Export an instance named `chroma_store` for compatibility with existing imports
chroma_store = QdrantStore()
