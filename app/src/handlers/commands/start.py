from typing import Optional


async def handle_start(
	user_id: int,
	chat_id: int,
	username: Optional[str],
	message_id: int,
	first_name: Optional[str],
	last_name: Optional[str],
	language_code: Optional[str],
) -> dict:
	# Validate required inputs before delegating
	if not all([
		user_id,
		chat_id,
		message_id,
	]):
		raise ValueError("Missing required identifiers (user_id/chat_id/message_id)")

	# Normalize optional fields to empty strings
	_username = username or ""
	_first_name = first_name or ""
	_last_name = last_name or ""
	_lang = language_code or ""

	from src.controllers.cmdStartController import handle_cmd_start

	result = handle_cmd_start(
		user_id=user_id,
		chat_id=chat_id,
		username=_username,
		message_id=message_id,
		first_name=_first_name,
		last_name=_last_name,
		language_code=_lang,
	)
	return {"text": result.get("text", "")}


