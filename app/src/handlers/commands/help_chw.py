from src.context.messages.commands.help_chw import get_message


async def handle_help_chw() -> dict:
	return {"text": get_message()}
