from pathlib import Path
from src.context.messages.commands.help_pchat import get_caption


async def handle_help_pchat() -> dict:
	photo_path = str(
		Path(__file__).resolve().parents[2] / "context" / "resources" / "images" / "help_pchat.jpg"
	)
	return {
		"photo_path": photo_path,
		"caption": get_caption(),
	}
