from app.plugins.base import BasePlugin
from datetime import datetime
from typing import Any, Dict, Optional

class TimePlugin(BasePlugin):
    name = "Time/Date"
    description = "Provides current time and date context"

    async def execute(self, user_text: str, context: Dict[str, Any]) -> Optional[str]:
        if any(word in user_text.lower() for word in ["time", "date", "day", "today"]):
            now = datetime.now()
            return f"The current time is {now.strftime('%H:%M')} and the date is {now.strftime('%Y-%m-%d')}."
        return None
