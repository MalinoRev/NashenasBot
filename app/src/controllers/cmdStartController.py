from typing import Dict


def handle_cmd_start(
	user_id: int,
	chat_id: int,
	username: str,
	message_id: int,
	first_name: str,
	last_name: str,
	language_code: str,
) -> Dict[str, str]:
	# Business logic placeholder: create/load user, update last_activity, etc.
	greeting = "Welcome! Bot is up and running."
	if username:
		greeting = f"Welcome, @{username}! Bot is up and running."
	elif first_name or last_name:
		full_name = (first_name or "").strip() + (" " + last_name if last_name else "")
		greeting = f"Welcome, {full_name.strip()}! Bot is up and running."

	return {"text": greeting}


