import asyncio


def get_message() -> str:
	async def _fetch():
		from src.services.bot_settings_service import get_bot_name
		return await get_bot_name()
	try:
		brand = asyncio.get_event_loop().run_until_complete(_fetch())  # type: ignore[arg-type]
	except Exception:
		brand = "ربات"
	return (
		"✅اطلاعات شما ثبت شد.\n\n"
		f"به خانواده بزرگ《{brand} 🤖》 خوش اومدی بهت توصیه میکنم اول از همه با لمس کردن 《🤔 راهنما》   با ربات آشنا شی\n\n"
		"از منوی پایین👇 انتخاب کن"
	)


