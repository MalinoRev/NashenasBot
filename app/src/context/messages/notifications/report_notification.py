def get_message(reporter_name: str, reporter_id: int, target_name: str, target_id: int, target_unique_id: str, category: str, reason: str) -> str:
	# Escape HTML special characters in user input
	reporter_name = reporter_name.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
	target_name = target_name.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
	category = category.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
	reason = reason.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
	
	return (
		"🚨 <b>گزارش جدید دریافت شد</b>\n\n"
		f"👤 <b>گزارش‌دهنده:</b> {reporter_name} (ID: {reporter_id})\n"
		f"🎯 <b>گزارش‌شده:</b> {target_name} (ID: {target_id})\n"
		f"🔗 <b>پروفایل:</b> /user_{target_unique_id}\n"
		f"📂 <b>دسته‌بندی:</b> {category}\n"
		f"📝 <b>دلیل:</b> {reason}\n\n"
		"لطفاً گزارش را بررسی و تصمیم‌گیری کنید:"
	)

