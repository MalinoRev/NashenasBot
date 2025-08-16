import os
from sqlalchemy import select, func
from pathlib import Path

from src.core.database import get_session
from src.databases.users import User
from src.context.messages.replies.invite import get_message
from src.context.messages.replies.inviteImage import get_caption


async def handle_invite(telegram_user_id: int) -> dict:
	# Fetch user to get referral_id and compute referral count
	referral_id = ""
	user_referral_count = 0
	async with get_session() as session:
		user: User | None = await session.scalar(select(User).where(User.user_id == telegram_user_id))
		if user and getattr(user, "referral_id", None):
			referral_id = user.referral_id
			# Count users whose referraled_by equals current user's DB id
			user_referral_count = await session.scalar(
				select(func.count()).select_from(User).where(User.referraled_by == user.id)
			) or 0

	bot_username = os.getenv("TELEGRAM_BOT_USERNAME", "")
	# Build absolute path to image (located under /app/src/context/resources/images)
	image_path = str(
		Path(__file__).resolve().parents[2] / "context" / "resources" / "images" / "invite.jpg"
	)
	caption = get_caption(bot_username or "Melogapbot", referral_id or "")

	# Return a structured payload for the route to send photo + caption, then a text
	return {
		"photo_path": image_path,
		"caption": caption,
		"text": get_message(user_referral_count),
	}
