import asyncio
import random
from telegram import Update, constants
from telegram.ext import ContextTypes
from app.core.config import settings

class TelegramBotUtils:
    @staticmethod
    async def simulate_typing(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
        """Simulates human-like typing delay based on message length."""
        chat_id = update.effective_chat.id
        await context.bot.send_chat_action(chat_id=chat_id, action=constants.ChatAction.TYPING)

        # Calculate delay: ~0.05s per character, but within bounds
        delay = min(max(len(text) * 0.05, settings.MIN_TYPING_DELAY), settings.MAX_TYPING_DELAY)
        # Add some randomness
        delay *= random.uniform(0.8, 1.2)

        await asyncio.sleep(delay)

    @staticmethod
    def chunk_message(text: str, limit: int = 4000) -> list[str]:
        """Splits a long message into smaller chunks."""
        return [text[i:i + limit] for i in range(0, len(text), limit)]

    @staticmethod
    async def send_smart_reply(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
        """Sends a message with typing simulation and chunking."""
        chunks = TelegramBotUtils.chunk_message(text, settings.MESSAGE_CHUNK_SIZE)
        for chunk in chunks:
            await TelegramBotUtils.simulate_typing(update, context, chunk)
            await update.message.reply_text(chunk)
            # Occasional pause between messages if multiple chunks
            if len(chunks) > 1:
                await asyncio.sleep(random.uniform(0.5, 1.5))
