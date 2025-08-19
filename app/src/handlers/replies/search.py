from src.context.messages.replies.search import get_message
from src.context.keyboards.inline.search import build_keyboard


async def handle_search() -> dict:
	return {"text": get_message(), "reply_markup": build_keyboard()}


