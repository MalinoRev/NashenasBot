from typing import Optional


def format_profile_caption(
	name: str,
	gender_text: str,
	state_name: str,
	city_name: str,
	age: str,
	like_count: int,
	unique_id: str,
	filtered_age_text: Optional[str] = None,
) -> str:
	filtered = filtered_age_text or "- همه میتوانند به شما درخواست چت دهند."
	return (
		f"• نام: {name}\n"
		f"• جنسیت: {gender_text}\n"
		f"• استان: {state_name}\n"
		f"• شهر: {city_name}\n"
		f"• سن: {age}\n\n"
		f"• تعداد لایک ها: {like_count}\n\n"
		"هم اکنون 👀 آنلایـــن (🗣)\n\n"
		f"\n🆔 آیدی : /user_{unique_id}\n\n"
		"تنظیم حالت سایلنت : /silent\n\n"
		"حذف اکانت ربات : /deleted_account\n\n"
		f"{filtered}"
	)



