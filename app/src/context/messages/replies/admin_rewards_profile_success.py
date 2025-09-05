def get_message(new_amount: int) -> str:
	return f"✅ پاداش تکمیل پروفایل با موفقیت به {new_amount:,} سکه تغییر یافت."


def get_invalid_amount_message() -> str:
	return (
		"❌ **مقدار نامعتبر!**\n\n"
		"لطفاً یک عدد معتبر بین 0 تا 100,000 وارد کنید.\n\n"
		"🔹 **فرمت صحیح**: فقط عدد (مثال: 500)\n"
		"🔹 **محدوده مجاز**: 0 تا 100,000"
	)
