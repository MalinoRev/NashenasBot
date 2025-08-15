import os
from typing import Optional

from fastapi import FastAPI, Header, HTTPException, Request


app = FastAPI(title="Nashenas Bot Webhook")


def get_webhook_secret() -> Optional[str]:
    return os.getenv("TELEGRAM_WEBHOOK_SECRET")


@app.get("/healthz")
async def healthcheck() -> dict:
    return {"status": "ok"}


@app.post("/webhook")
async def telegram_webhook(
    request: Request,
    x_telegram_bot_api_secret_token: Optional[str] = Header(None),
) -> dict:
    secret = get_webhook_secret()
    if secret:
        if not x_telegram_bot_api_secret_token or x_telegram_bot_api_secret_token != secret:
            raise HTTPException(status_code=403, detail="Invalid webhook secret token")

    # Minimal placeholder: accept and acknowledge the update
    # Real handling will be implemented by aiogram dispatcher later
    _ = await request.json()
    return {"ok": True}



