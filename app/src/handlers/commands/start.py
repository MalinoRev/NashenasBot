from typing import Optional


async def handle_start(user_id: int, chat_id: int, username: Optional[str]) -> dict:
	# Business logic goes here (e.g., create user record, etc.)
	greeting = "Welcome! Bot is up and running."
	if username:
		greeting = f"Welcome, @{username}! Bot is up and running."
	return {"text": greeting}


