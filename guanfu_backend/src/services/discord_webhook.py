import httpx
from ..config import settings
import json

async def send_to_discord(payload: dict):
    """
    Sends a message to the Discord webhook.

    Args:
        payload: The JSON payload to send to Discord.
    """
    if not settings.DISCORD_WEBHOOK_URL:
        return

    # Discord webhooks expect a 'content' key.
    # We'll format the payload for better readability.
    message = {
        "content": "New POST request received:",
        "embeds": [
            {
                "description": f"```json\n{json.dumps(payload, indent=2, ensure_ascii=False)}\n```",
                "color": 5814783  # A nice blue color
            }
        ]
    }

    async with httpx.AsyncClient() as client:
        try:
            await client.post(settings.DISCORD_WEBHOOK_URL, json=message)
        except httpx.RequestError as e:
            # In a real app, you'd want to log this error.
            print(f"Error sending Discord webhook: {e}")
