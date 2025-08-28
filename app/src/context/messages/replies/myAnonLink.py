import os

def get_message(referral_id: str | None, display_name: str | None) -> str:
	if not referral_id:
		return "لینک ناشناس شما هنوز ایجاد نشده است. کمی بعد دوباره تلاش کنید."

	bot_username = os.getenv("TELEGRAM_BOT_USERNAME")
	if not bot_username:
		return "خطا در تنظیمات بات. لطفاً با مدیر تماس بگیرید."

	name = display_name or "دوست"
	telegram_link = f"https://telegram.me/{bot_username}?start=inv_{referral_id}"

	return (
		f"سلام {name} هستم ✋\n\n"
		"لینک زیر رو لمس کن و هر حرفی که تو دلت هست یا هر انتقادی که نسبت به من داری رو با خیال راحت بنویس و بفرست. بدون اینکه از اسمت باخبر بشم پیامت به من می‌رسه. خودتم می‌تونی امتحان کنی و از بقیه بخوای راحت و ناشناس بهت پیام بفرستن، حرفای خیلی جالبی می‌شنوی! 😉\n\n"
		"👇👇\n"
		f"{telegram_link}"
	)


