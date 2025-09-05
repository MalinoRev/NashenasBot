def get_success_message(field_name: str, new_value: int, field_type: str = "price") -> str:
	"""Get success message for setting pricing field."""
	if field_type == "price":
		return (
			f"✅ <b>{field_name} با موفقیت تغییر کرد!</b>\n\n"
			f"مقدار جدید: <b>{new_value:,} تومان</b>\n\n"
			"تغییرات فوری اعمال شدند."
		)
	else:  # time
		return (
			f"✅ <b>{field_name} با موفقیت تغییر کرد!</b>\n\n"
			f"مقدار جدید: <b>{new_value} روز</b>\n\n"
			"تغییرات فوری اعمال شدند."
		)


def get_invalid_message(field_type: str = "price") -> str:
	"""Get invalid input message."""
	if field_type == "price":
		return (
			"❌ <b>مقدار نامعتبر!</b>\n\n"
			"لطفاً یک عدد صحیح بین 0 تا 1,000,000 وارد کنید.\n"
			"مثال: 50000"
		)
	else:  # time
		return (
			"❌ <b>مقدار نامعتبر!</b>\n\n"
			"لطفاً یک عدد صحیح بین 1 تا 365 وارد کنید.\n"
			"مثال: 30"
		)
