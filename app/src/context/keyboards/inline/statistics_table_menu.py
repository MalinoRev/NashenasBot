from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def build_keyboard() -> InlineKeyboardMarkup:
	buttons = [
		[
			InlineKeyboardButton(text="👥 آمار کاربران جدید", callback_data="statistics:new_users"),
		],
		[
			InlineKeyboardButton(text="💬 آمار چت‌های باز شده", callback_data="statistics:chats_opened"),
		],
		[
			InlineKeyboardButton(text="📩 آمار دایرکت‌های ارسال شده", callback_data="statistics:directs_sent"),
		],
		[
			InlineKeyboardButton(text="💳 آمار تراکنش‌های باز شده", callback_data="statistics:transactions_opened"),
		],
		[
			InlineKeyboardButton(text="🪙 آمار سکه‌های مصرف شده", callback_data="statistics:coins_spent"),
		],
		[
			InlineKeyboardButton(text="👫 آمار کاربران معرفی شده", callback_data="statistics:referrals"),
		],
		[
			InlineKeyboardButton(text="🔙 بازگشت", callback_data="statistics:back"),
		],
	]
	return InlineKeyboardMarkup(inline_keyboard=buttons)
