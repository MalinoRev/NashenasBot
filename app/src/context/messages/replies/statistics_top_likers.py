def get_message(likes: list) -> str:
	if not likes:
		return "👍 **بیشترین لایک کننده‌ها**\n\nهیچ لایک کننده‌ای یافت نشد."
	
	header = "👍 **بیشترین لایک کننده‌ها**\n\n📊 **کاربران با بیشترین لایک‌های ارسال شده:**\n\n"
	
	rows = []
	for i, (user, count) in enumerate(likes, 1):
		rows.append(f"{i}. `{user.user_id}` - {count:,} لایک")
	
	return header + "\n".join(rows)
