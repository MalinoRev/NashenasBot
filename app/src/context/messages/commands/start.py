import asyncio


def get_message(name: str | None = None) -> str:
	person = name or "دوست"
	async def _fetch():
		from src.services.bot_settings_service import get_bot_name, get_channel_slug
		return await get_bot_name(), await get_channel_slug()
	try:
		brand, channel_slug = asyncio.get_event_loop().run_until_complete(_fetch())  # type: ignore[arg-type]
	except Exception:
		brand, channel_slug = "ربات", ""
	channel_link = f"https://t.me/{channel_slug}" if channel_slug else "https://t.me"
	return (
		f"خب ، حالا چه کاری برات انجام بدم؟\n\n"
		f"[کانال رسمی  {brand}  🤖 (اخبار،آپدیت ها و ترفند ها) ]({channel_link})\n\n"
		"از منوی پایین👇 انتخاب کن"
	)



