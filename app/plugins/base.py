from typing import Any, Dict, Optional

class BasePlugin:
    name: str = "Base"
    description: str = ""

    async def execute(self, user_text: str, context: Dict[str, Any]) -> Optional[str]:
        """Returns a string to be added to the context, or None."""
        raise NotImplementedError
