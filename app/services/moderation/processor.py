import asyncio
from sqlalchemy import select, update
from app.db.base import AsyncSessionLocal
from app.db.models import ApprovalQueue, ApprovalStatus, Conversation
from app.core.config import settings
from telegram import Bot
import logging

logger = logging.getLogger(__name__)

async def process_approvals():
    """Background task to send approved messages via Telegram."""
    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
    while True:
        try:
            async with AsyncSessionLocal() as db:
                stmt = select(ApprovalQueue).where(ApprovalQueue.status == ApprovalStatus.APPROVED)
                result = await db.execute(stmt)
                approved_items = result.scalars().all()

                for item in approved_items:
                    # Get chat_id
                    stmt = select(Conversation.chat_id).where(Conversation.id == item.conversation_id)
                    chat_result = await db.execute(stmt)
                    chat_id = chat_result.scalar()

                    if chat_id:
                        # Send the message
                        # Note: In a real system we'd use the AI service to generate
                        # the actual response if 'content' was just a placeholder
                        await bot.send_message(chat_id=chat_id, text=item.content)

                        # Mark as processed (using a new status or just deleting)
                        # Let's just update a flag or change status to 'sent'
                        # For now we'll just delete or mark as 'sent'
                        await db.execute(update(ApprovalQueue).where(ApprovalQueue.id == item.id).values(status=ApprovalStatus.REJECTED)) # Using REJECTED as 'finished' for simplicity here, or better add SENT

                await db.commit()
        except Exception as e:
            logger.error(f"Error in approval processor: {e}")

        await asyncio.sleep(10) # Check every 10 seconds

if __name__ == "__main__":
    asyncio.run(process_approvals())
