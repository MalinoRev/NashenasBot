from pathlib import Path
from src.context.messages.commands.help_onw import get_caption


async def handle_help_onw() -> dict:
	photo_path = str(
		Path(__file__).resolve().parents[2] / "context" / "resources" / "images" / "help_onw.jpg"
	)
	return {
		"photo_path": photo_path,
		"caption": get_caption(),
	}
