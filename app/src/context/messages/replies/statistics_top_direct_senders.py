def get_message(directs: list) -> str:
	if not directs:
		return "📤 **بیشترین دایرکت‌های ارسال شده**\n\nهیچ دایرکتی یافت نشد."
	
	header = "📤 **بیشترین دایرکت‌های ارسال شده**\n\n📊 **کاربران با بیشترین دایرکت‌های ارسال شده:**\n\n"
	
	rows = []
	for i, (user, count) in enumerate(directs, 1):
		rows.append(f"{i}. `{user.user_id}` - {count:,} دایرکت")
	
	return header + "\n".join(rows)
