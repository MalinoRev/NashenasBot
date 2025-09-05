import asyncio


def get_message() -> str:
	return (
		"🔹 من اینجام که کمکت کنم! برای دریافت راهنمایی در مورد هر موضوع، کافیه دستور آبی رنگی که مقابل اون سوال هست رو لمس کنی:\n\n"
		"🔸 - ‏ چگونه بصورت ناشناس چت کنم؟ /help_chat\n\n"
		"🔸 -‏ سکه یا امتیاز چیست؟ /help_credit\n\n"
		"🔸 - ‏ چگونه افراد نزدیکمو پیدا کنم؟ /help_gps\n\n"
		"🔸 - ‏ پروفایل چیست؟ /help_profile\n\n"
		"🔸 - ‏ چگونه درخواست چت بفرستم؟ /help_pchat\n\n"
		"🔸 - ‏ پیام دایرکت چیست؟ /help_direct\n\n"
		"🔸 -‏ چگونه با میان بر ها کار کنم؟ /help_shortcuts\n\n"
		"🔸 - ‏ 🚫 قوانین استفاده از ربات /help_terms\n\n"
		"🔸 - اطلاع رسانی آنلاین شدن مخاطب /help_onw\n\n"
		"🔸 - اطلاع رسانی اتمام چت مخاطب /help_chw\n\n"
		"🔸 - مخاطبین چیست ؟ /help_contacts\n\n"
		"🔸 - آموزش حذف پیام در چت /help_deleteMessage\n\n"
		"🔸 - چگونه بصورت پیشرفته بین کاربران جستجو کنم ؟ /help_search\n\n"
		"🔸 - چگونه اکانت ربات را حذف کنم ؟ /deleted_account\n\n"
		f"👨‍💻 ارتباط با پشتیبانی ربات : @{_get_support()}"
	)


def _get_support() -> str:
	async def _fetch():
		from src.services.bot_settings_service import get_support_username
		return await get_support_username()
	try:
		val = asyncio.get_event_loop().run_until_complete(_fetch())  # type: ignore[arg-type]
		return val or 'support'
	except Exception:
		return 'support'
