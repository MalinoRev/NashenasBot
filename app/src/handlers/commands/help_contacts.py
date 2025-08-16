from src.context.messages.commands.help_contacts import get_message


async def handle_help_contacts() -> dict:
	return {"text": get_message()}
