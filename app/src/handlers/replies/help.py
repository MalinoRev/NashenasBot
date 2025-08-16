from src.context.messages.replies.help import get_message


async def handle_help() -> dict:
	return {"text": get_message()}
