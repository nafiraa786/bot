from sqlalchemy import select, text
from app.db.base import AsyncSessionLocal
from app.db.models import Memory, User
from app.services.ai.openai_service import ai_service
from typing import List, Dict
import json

class MemoryEngine:
    @staticmethod
    async def store_memory(user_id: int, content: str, category: str = "factual"):
        embedding = await ai_service.get_embeddings(content)
        async with AsyncSessionLocal() as db:
            memory = Memory(
                user_id=user_id,
                content=content,
                embedding=embedding,
                category=category
            )
            db.add(memory)
            await db.commit()

    @staticmethod
    async def retrieve_memories(user_id: int, query: str, limit: int = 5) -> List[str]:
        query_embedding = await ai_service.get_embeddings(query)

        async with AsyncSessionLocal() as db:
            # Using pgvector's cosine distance operator <=>
            stmt = select(Memory.content).where(Memory.user_id == user_id).order_by(
                Memory.embedding.cosine_distance(query_embedding)
            ).limit(limit)

            result = await db.execute(stmt)
            return [row for row in result.scalars().all()]

    @staticmethod
    async def extract_and_store_memories(user_id: int, text: str):
        """Extracts potential memories from text and stores them."""
        prompt = (
            "Extract key factual memories, preferences, or relationship details from the following user message. "
            "Return a list of short descriptive sentences. If nothing important, return an empty list. "
            f"Message: {text}"
        )
        response = await ai_service.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": "You are a memory extraction assistant. Output JSON list of strings."},
                      {"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        data = json.loads(response.choices[0].message.content)
        memories = data.get("memories", [])
        for m in memories:
            await MemoryEngine.store_memory(user_id, m)

memory_engine = MemoryEngine()
