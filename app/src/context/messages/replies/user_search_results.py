def get_no_results_message() -> str:
	return "❌ هیچ کاربری با این مشخصات یافت نشد."


def get_user_details(user, is_banned: bool = False) -> str:
	"""Format user details for display"""
	status = "🚫 مسدود شده" if is_banned else "✅ فعال"
	created = user.created_at.strftime("%Y-%m-%d %H:%M")
	
	return f"""👤 <b>اطلاعات کاربر</b>

🆔 آیدی کاربر: {user.user_id}
📛 نام کاربری: {user.tg_name}
📅 تاریخ عضویت: {created}
{status}
👤 پروفایل: /user_{user.unique_id}"""
