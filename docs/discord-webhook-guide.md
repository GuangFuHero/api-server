# Developer Guide: Discord Webhook Integration

This guide explains how to use the automated Discord notification feature in this project.

## 1. Introduction

To improve visibility on data creation, the system is integrated with a Discord webhook. This feature automatically sends a notification to a designated Discord channel whenever new data is created via most `POST` APIs.

This is achieved using a global middleware that intercepts outgoing requests.

## 2. How to Use

There are two ways to trigger the webhook: automatically (for most cases) and manually (for special cases).

### Method 1: Automatic Triggering (Default Behavior)

For any developer adding a new `POST` endpoint to the API, this functionality is **enabled by default**. You do not need to write any extra code to activate it.

The `DiscordWebhookMiddleware` in `src/main.py` automatically intercepts any `POST` request with a JSON body and sends its content to the Discord channel.

**Example:**

If you create a new router for `products` like this, it will automatically trigger the webhook:

```python
# src/routers/products.py

@router.post("/")
def create_product(product: ProductCreate):
    # ... your logic to save the product ...
    return new_product
```

#### How to Opt-Out

If you have a specific `POST` API that should **not** trigger a Discord notification, you can exclude it:

1.  Open `src/main.py`.
2.  Find the `DiscordWebhookMiddleware` class.
3.  Add your endpoint's path to the `excluded_paths` list.

```python
# src/main.py

class DiscordWebhookMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # ...
        # Add the path you want to exclude here
        excluded_paths = ["/line/callback", "/your/excluded/path"]
        if request.url.path in excluded_paths:
            return await call_next(request)
        # ...
```

### Method 2: Manual Triggering (Advanced)

If you want to send a notification from a non-`POST` request (e.g., a `GET` or `PATCH`), or if you want to send a custom-formatted message from a background task, you can call the webhook service function directly.

**Steps:**

1.  **Import the function** at the top of your file:

    ```python
    from ..services.discord_webhook import send_to_discord
    ```

2.  **Call the function** with `await` and provide a Python dictionary (`dict`) as the payload. The dictionary will be converted to JSON and sent.

    ```python
    # Example: Sending a custom notification from a GET endpoint

    @router.get("/{item_id}")
    async def get_special_item(item_id: str):
        item = db.get(item_id)

        # Manually trigger a custom notification
        await send_to_discord({
            "message": "A high-priority item was accessed.",
            "item_id": item_id,
            "timestamp": datetime.now().isoformat()
        })

        return item
    ```

## 3. Testing the Webhook

A dedicated test endpoint exists to verify that the connection to Discord is working correctly.

-   **Endpoint**: `POST /test/discord`

This endpoint directly calls the `send_to_discord` service.

You can use the following `curl` command to test it:

```bash
curl -X POST http://localhost:8000/test/discord -H "Content-Type: application/json" -d '{
  "user": "test-developer",
  "message": "Verifying the Discord webhook connection."
}'
```

If the request is successful, a formatted message with the JSON payload will appear in the designated Discord channel.
