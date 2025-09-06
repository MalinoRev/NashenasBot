from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def build_keyboard(page: int, has_next: bool, page_size: int = 10, filter_type: str = "all") -> InlineKeyboardMarkup:
	# Encode direction with current page so handler can detect boundaries without double-fetch
	filter_labels = {
		"all": "🔍 نمایش همه",
		"paid": "🔍 پرداخت شده ها", 
		"unpaid": "🔍 پرداخت نشده ها"
	}
	filter_label = filter_labels.get(filter_type, "🔍 نمایش همه")
	
	buttons = [
		[
			InlineKeyboardButton(text=filter_label, callback_data=f"financial:filter_toggle:{filter_type}:{page}"),
		],
		[
			InlineKeyboardButton(text="صفحه بعدی ⬅️", callback_data=f"financial_page:transactions:next:{page}:{filter_type}"),
			InlineKeyboardButton(text="➡️ صفحه قبلی", callback_data=f"financial_page:transactions:prev:{page}:{filter_type}"),
		],
	]
	return InlineKeyboardMarkup(inline_keyboard=buttons)


