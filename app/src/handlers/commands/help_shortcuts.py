from src.context.messages.commands.help_shortcuts import get_message


async def handle_help_shortcuts() -> dict:
	return {"text": get_message()}
