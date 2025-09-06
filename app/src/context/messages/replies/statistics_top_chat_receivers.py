def get_message(chats: list) -> str:
	if not chats:
		return "💬 **بیشترین چت‌های دریافت شده**\n\nهیچ چتی یافت نشد."
	
	header = "💬 **بیشترین چت‌های دریافت شده**\n\n📊 **کاربران با بیشترین چت‌های دریافت شده:**\n\n"
	
	rows = []
	for i, (user, count) in enumerate(chats, 1):
		rows.append(f"{i}. `{user.user_id}` - {count:,} چت")
	
	return header + "\n".join(rows)
