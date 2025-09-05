def get_user_not_found_message() -> str:
	return "❌ کاربر یافت نشد. لطفاً آیدی عددی صحیح را وارد کنید."


def get_already_support_message() -> str:
	return "❌ این کاربر قبلاً پشتیبان است."


def get_message(user_name: str, user_id: int) -> str:
	return (
		"➕ **اضافه کردن پشتیبان**\n\n"
		f"نام کاربر: **{user_name}**\n"
		f"آیدی عددی: `{user_id}`\n\n"
		"آیا تایید می‌کنید؟"
	)


