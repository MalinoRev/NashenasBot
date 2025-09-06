def get_message(referrers: list) -> str:
	if not referrers:
		return "👥 **بیشترین کاربران معرفی شده**\n\nهیچ کاربر معرفی کننده‌ای یافت نشد."
	
	header = "👥 **بیشترین کاربران معرفی شده**\n\n📊 **کاربران با بیشترین تعداد معرفی:**\n\n"
	
	rows = []
	for i, (user, count) in enumerate(referrers, 1):
		rows.append(f"{i}. `{user.user_id}` - {count:,} کاربر معرفی شده")
	
	return header + "\n".join(rows)
