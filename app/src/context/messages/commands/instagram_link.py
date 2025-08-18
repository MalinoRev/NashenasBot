import os

def format_link(link: str) -> str:
	return link



def get_link(referral_id: str | None) -> str:
	if not referral_id:
		return ""
	bot_username = os.getenv("TELEGRAM_BOT_USERNAME")
	if not bot_username:
		return ""
	return f"https://telegram.me/{bot_username}?start={referral_id}"


