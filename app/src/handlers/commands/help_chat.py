from pathlib import Path
from src.context.messages.commands.help_chat import get_caption


async def handle_help_chat() -> dict:
	photo_path = str(
		Path(__file__).resolve().parents[2] / "context" / "resources" / "images" / "help_chat.jpg"
	)
	return {
		"photo_path": photo_path,
		"caption": get_caption(),
	}
