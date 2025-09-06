from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def build_keyboard() -> InlineKeyboardMarkup:
	buttons = [
		[
			InlineKeyboardButton(text="💳 بیشترین تراکنش‌های موفق", callback_data="statistics:top_successful_transactions"),
		],
		[
			InlineKeyboardButton(text="💰 بیشترین مبلغ تراکنش‌ها", callback_data="statistics:top_transaction_amounts"),
		],
		[
			InlineKeyboardButton(text="👫 بیشترین کاربران دعوت شده", callback_data="statistics:top_referrers"),
		],
		[
			InlineKeyboardButton(text="🪙 بیشترین سکه‌های مصرف شده", callback_data="statistics:top_coin_spenders"),
		],
		[
			InlineKeyboardButton(text="📤 بیشترین دایرکت‌های ارسال شده", callback_data="statistics:top_direct_senders"),
		],
		[
			InlineKeyboardButton(text="📥 بیشترین دایرکت‌های دریافت شده", callback_data="statistics:top_direct_receivers"),
		],
		[
			InlineKeyboardButton(text="💬 بیشترین چت‌های ارسال شده", callback_data="statistics:top_chat_senders"),
		],
		[
			InlineKeyboardButton(text="💬 بیشترین چت‌های دریافت شده", callback_data="statistics:top_chat_receivers"),
		],
		[
			InlineKeyboardButton(text="❤️ بیشترین لایک‌ها", callback_data="statistics:top_likes"),
		],
		[
			InlineKeyboardButton(text="👤 بیشترین لایک کننده‌ها", callback_data="statistics:top_likers"),
		],
		[
			InlineKeyboardButton(text="🔙 بازگشت", callback_data="statistics:back"),
		],
	]
	return InlineKeyboardMarkup(inline_keyboard=buttons)
