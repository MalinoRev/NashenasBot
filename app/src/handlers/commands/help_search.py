from src.context.messages.commands.help_search import get_message


async def handle_help_search() -> dict:
	return {"text": get_message()}
