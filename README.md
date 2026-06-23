# Production-Ready Telegram AI Assistant

This is a sophisticated AI assistant bot built with FastAPI, Telegram, and OpenAI. It features human-like behavior, long-term memory using pgvector, and an admin dashboard for moderation and persona management.

## Tech Stack
- **Backend:** Python FastAPI
- **Telegram:** python-telegram-bot
- **AI:** OpenAI GPT-4 Turbo
- **Database:** PostgreSQL + pgvector
- **Cache/Queue:** Redis
- **Deployment:** Docker

## Features
- **Persona System:** Custom tone, style, and identity.
- **Memory System:** Long-term conversation history and semantic retrieval.
- **Human-like Behavior:** Simulated typing delays and variable response timing.
- **Approval Mode:** Queue sensitive replies for manual approval.
- **Admin Dashboard:** Manage users, settings, and approvals.

## Setup Instructions

1. **Clone the repository**
2. **Create a `.env` file** based on `.env.example`:
   ```bash
   cp .env.example .env
   ```
   Fill in your `TELEGRAM_BOT_TOKEN` and `OPENAI_API_KEY`.

3. **Run with Docker Compose:**
   ```bash
   docker-compose up --build
   ```

4. **Initialize the database:**
   ```bash
   docker-compose exec api python -m app.db.init_db
   ```

5. **Access the Admin Dashboard:**
   Open `http://localhost:8000` in your browser.

## Project Structure
- `app/api/`: FastAPI endpoints and dashboard logic.
- `app/db/`: Database models and connection setup.
- `app/services/ai/`: OpenAI integration and persona management.
- `app/services/telegram/`: Telegram bot handlers and utils.
- `app/services/memory/`: Semantic memory engine using pgvector.
- `app/services/moderation/`: Content safety and approval logic.
- `app/templates/`: Jinja2 templates for the admin dashboard.

## License
MIT
