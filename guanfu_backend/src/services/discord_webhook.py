import httpx
from ..config import settings
import json


async def send_discord_message(content: str, embed_data: dict | None = None):
    """
    Sends a message to a Discord webhook.

    Args:
        content: The main text content of the message.
        embed_data: Optional dictionary to be sent as a formatted JSON embed.
    """
    if not settings.DISCORD_WEBHOOK_URL:
        return

    message = {"content": content}

    if embed_data:
        message["embeds"] = [
            {
                "description": f"```json\n{json.dumps(embed_data, indent=2, ensure_ascii=False)}\n```",
                "color": 5814783,  # A nice blue color
            }
        ]

    async with httpx.AsyncClient() as client:
        try:
            await client.post(settings.DISCORD_WEBHOOK_URL, json=message)
        except httpx.RequestError as e:
            # In a real app, you'd want to log this error.
            print(f"Error sending Discord webhook: {e}")
