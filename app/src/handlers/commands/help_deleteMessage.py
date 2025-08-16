from src.context.messages.commands.help_deleteMessage import get_message


async def handle_help_delete_message() -> dict:
	return {"text": get_message()}
