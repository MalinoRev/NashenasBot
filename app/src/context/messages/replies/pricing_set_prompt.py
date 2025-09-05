def get_message(field_name: str, current_value: int, field_type: str = "price") -> str:
	"""Get prompt message for setting pricing field."""
	if field_type == "price":
		return (
			f"💰 <b>تنظیم {field_name}</b>\n\n"
			f"مقدار فعلی: <b>{current_value:,} تومان</b>\n\n"
			"لطفاً مقدار جدید را وارد کنید:\n"
			"🔹 محدوده مجاز: 0 تا 1,000,000 تومان\n"
			"🔹 فرمت: فقط عدد (مثال: 50000)\n\n"
			"برای لغو عملیات از دکمه بازگشت استفاده کنید."
		)
	else:  # time
		return (
			f"⏰ <b>تنظیم {field_name}</b>\n\n"
			f"مقدار فعلی: <b>{current_value} روز</b>\n\n"
			"لطفاً مقدار جدید را وارد کنید:\n"
			"🔹 محدوده مجاز: 1 تا 365 روز\n"
			"🔹 فرمت: فقط عدد (مثال: 30)\n\n"
			"برای لغو عملیات از دکمه بازگشت استفاده کنید."
		)
