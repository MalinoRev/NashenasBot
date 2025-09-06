async def get_message(name: str | None = None) -> str:
	user = name or "دوست"
	try:
		from src.services.bot_settings_service import get_bot_name
		brand = await get_bot_name()
	except Exception:
		brand = "ربات"
	return (
		f"سلام {user} عزیز ✋️\n\n"
		f"به 《{brand} 🤖》 خوش اومدی ، توی این ربات می تونی افراد #نزدیک ات رو پیدا کنی و باهاشون آشنا شی و یا به یه نفر بصورت #ناشناس وصل شی و باهاش #چت کنی ❗️\n\n"
		"- استفاده از این ربات رایگانه و اطلاعات تلگرام شما مثل اسم،عکس پروفایل یا موقعیت GPS کاملا محرمانه هست😎"
	)



