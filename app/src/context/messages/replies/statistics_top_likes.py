def get_message(likes: list) -> str:
	if not likes:
		return "❤️ **بیشترین لایک‌ها**\n\nهیچ لایکی یافت نشد."
	
	header = "❤️ **بیشترین لایک‌ها**\n\n📊 **کاربران با بیشترین لایک‌های دریافت شده:**\n\n"
	
	rows = []
	for i, (user, count) in enumerate(likes, 1):
		rows.append(f"{i}. `{user.user_id}` - {count:,} لایک")
	
	return header + "\n".join(rows)
