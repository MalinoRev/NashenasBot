async def get_message() -> str:
	# Fetch current values from database
	from src.services.bot_settings_service import (
		get_bot_name, 
		get_cache_channel_id, 
		get_channel_slug, 
		get_support_username
	)
	
	try:
		bot_name, cache_channel_id, main_channel, support_username = await get_bot_name(), await get_cache_channel_id(), await get_channel_slug(), await get_support_username()
	except Exception:
		bot_name, cache_channel_id, main_channel, support_username = "NashenasBot", None, None, None
	
	# Format values for display
	cache_display = str(cache_channel_id) if cache_channel_id else "تنظیم نشده"
	main_channel_display = f"@{main_channel}" if main_channel else "تنظیم نشده"
	support_display = f"@{support_username}" if support_username else "تنظیم نشده"
	
	return (
		"🎨 **تنظیمات برند، کانال و ...**\n\n"
		"در این بخش می‌توانید اطلاعات برند و کانال‌های ربات را تنظیم کنید.\n\n"
		"🔹 **تنظیمات فعلی:**\n"
		f"📝 نام ربات: {bot_name}\n"
		f"💾 کانال کش: {cache_display}\n"
		f"📝 کانال اصلی: {main_channel_display}\n"
		f"📝 کانال پشتیبانی: {support_display}\n\n"
		"برای ویرایش هر مورد از دکمه‌های زیر استفاده کنید:"
	)
