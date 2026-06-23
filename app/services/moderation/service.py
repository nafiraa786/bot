from app.services.ai.openai_service import ai_service
from app.db.models import ApprovalQueue, ApprovalStatus
from app.db.base import AsyncSessionLocal

class ModerationService:
    @staticmethod
    async def check_content(content: str) -> dict:
        """Checks content for safety and requires_approval."""
        return await ai_service.analyze_sentiment_and_safety(content)

    @staticmethod
    async def queue_for_approval(conversation_id: int, content: str, reason: str):
        async with AsyncSessionLocal() as db:
            item = ApprovalQueue(
                conversation_id=conversation_id,
                content=content,
                reason=reason,
                status=ApprovalStatus.PENDING
            )
            db.add(item)
            await db.commit()
            return item.id

moderation_service = ModerationService()
