import os


def get_message(name: str | None = None) -> str:
	person = name or "دوست"
	brand = os.getenv("BOT_BRAND_NAME", "ربات")
	channel_slug = os.getenv("BOT_CHANNEL_SLUG", "")
	channel_link = f"https://t.me/{channel_slug}" if channel_slug else "https://t.me"
	return (
		f"خب ، حالا چه کاری برات انجام بدم؟\n\n"
		f"[کانال رسمی  {brand}  🤖 (اخبار،آپدیت ها و ترفند ها) ]({channel_link})\n\n"
		"از منوی پایین👇 انتخاب کن"
	)



