def format_message(kind: str, page: int) -> str:
	# Header only; the recipients list and the footer will be appended by the caller
	return (
		"📝 پیش‌نمایش ارسال دایرکت به لیست\n\n"
		"این پیام به فهرست نتایج انتخاب‌شده ارسال خواهد شد.\n\n"
		f"نوع جستجو: {kind} | صفحه: {page}"
	)


