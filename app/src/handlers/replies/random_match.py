from src.context.messages.replies.randomMatchPrompt import get_message
from src.context.keyboards.inline.randomMatch import build_keyboard


async def handle_random_match() -> dict:
	return {
		"text": get_message(),
		"reply_markup": build_keyboard(),
	}
