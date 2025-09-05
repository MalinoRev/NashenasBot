def get_message(unban_price: int, delete_account_price: int, vip_rank_price: int, vip_rank_time_days: int) -> str:
	return (
		"💳 <b>مدیریت تعرفه‌ها و محصولات</b>\n\n"
		"ℹ️ تعرفه‌ها اکنون در <b>دیتابیس</b> ذخیره می‌شوند و از داخل ربات قابل مدیریت هستند.\n\n"
		"💰 <b>مقادیر فعلی (تومان):</b>\n"
		f"🗑️ حذف حساب کاربری: <b>{delete_account_price:,}</b>\n"
		f"🔓 رفع بن: <b>{unban_price:,}</b>\n"
		f"👑 خرید رتبه VIP: <b>{vip_rank_price:,}</b>\n"
		f"⏰ مدت اعتبار VIP: <b>{vip_rank_time_days}</b> روز\n\n"
		"🔧 <b>برای تغییر هر تعرفه، دکمه مربوطه را انتخاب کنید:</b>"
	)
