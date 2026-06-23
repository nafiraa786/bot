from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    CallbackQueryHandler
)
from app.core.config import settings
from app.services.telegram.utils import TelegramBotUtils
from app.services.ai.openai_service import ai_service
from app.db.base import AsyncSessionLocal
from app.db.models import User, Conversation, Message, PersonaSettings
from sqlalchemy import select
import logging

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! I am your AI assistant. How can I help you today?")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    user_text = update.message.text
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id

    async with AsyncSessionLocal() as db:
        # Get or create user
        stmt = select(User).where(User.telegram_id == user_id)
        result = await db.execute(stmt)
        user = result.scalars().first()

        if not user:
            user = User(
                telegram_id=user_id,
                username=update.effective_user.username,
                first_name=update.effective_user.first_name,
                last_name=update.effective_user.last_name
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)

        # Get or create conversation
        stmt = select(Conversation).where(Conversation.chat_id == chat_id)
        result = await db.execute(stmt)
        conversation = result.scalars().first()

        if not conversation:
            conversation = Conversation(user_id=user.id, chat_id=chat_id, type=update.effective_chat.type)
            db.add(conversation)
            await db.commit()
            await db.refresh(conversation)

        # Save user message
        msg = Message(conversation_id=conversation.id, sender_type="user", content=user_text)
        db.add(msg)

        # Get active persona
        stmt = select(PersonaSettings).where(PersonaSettings.is_active == True)
        result = await db.execute(stmt)
        persona = result.scalars().first()

        if not persona:
            # Fallback persona if none exists
            persona = PersonaSettings(
                name="Assistant",
                tone="helpful and friendly",
                style="conversational",
                system_prompt="You are a helpful assistant."
            )

        # Construct context (simplified for now, will enhance with memory later)
        # TODO: Add memory retrieval

        # Retrieve memories
        from app.services.memory.engine import memory_engine
        memories = await memory_engine.retrieve_memories(user.id, user_text)
        memory_context = "Relevant information you remember about this user:\n" + "\n".join(memories) if memories else ""

        # Basic context from recent messages
        stmt = select(Message).where(Message.conversation_id == conversation.id).order_by(Message.created_at.desc()).limit(10)
        result = await db.execute(stmt)
        recent_messages = result.scalars().all()
        history = []
        for m in reversed(recent_messages):
            role = "user" if m.sender_type == "user" else "assistant"
            history.append({"role": role, "content": m.content})

        from app.services.ai.persona import persona_manager
        system_prompt = persona_manager.construct_system_prompt(persona)
        if memory_context:
            system_prompt += f"\n\n{memory_context}"

        # AI Safety & Moderation check
        moderation = await ai_service.analyze_sentiment_and_safety(user_text)

        if moderation.get("requires_approval"):
            # Queue for approval
            from app.db.models import ApprovalQueue, ApprovalStatus
            queue_item = ApprovalQueue(
                conversation_id=conversation.id,
                content="[Bot would reply to]: " + user_text, # Simplification
                reason=moderation.get("reason", "Sensitive topic")
            )
            db.add(queue_item)
            await db.commit()

            # Notify Admin
            if settings.ADMIN_CHAT_ID:
                await context.bot.send_message(
                    chat_id=settings.ADMIN_CHAT_ID,
                    text=f"🚨 *Approval Required*\n\nUser: {user.username or user.first_name}\nReason: {moderation.get('reason')}\nContent: {user_text}",
                    parse_mode='Markdown'
                )

            await update.message.reply_text("I've received your message. I'll get back to you shortly.")
            return

        # Get AI Response
        ai_response = await ai_service.get_chat_response(history, system_prompt)

        # Save bot message
        bot_msg = Message(conversation_id=conversation.id, sender_type="bot", content=ai_response)
        db.add(bot_msg)
        await db.commit()

        # Send reply
        await TelegramBotUtils.send_smart_reply(update, context, ai_response)

        # Background task to extract memories
        asyncio.create_task(memory_engine.extract_and_store_memories(user.id, user_text))

def setup_bot():
    application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    return application

if __name__ == "__main__":
    app = setup_bot()
    app.run_polling()
