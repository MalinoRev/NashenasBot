from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def build_keyboard(kind: str, page: int, gender: str | None = None, has_next: bool = True, **kwargs) -> InlineKeyboardMarkup:
	"""
	Builds a pagination keyboard with Prev/Next buttons.
	Params encoded into callback_data for stateless paging.

	kind: one of [same_province, same_age, new_users, no_chats, popular, recent_chats, nearby, by_location]
	gender: one of [boys, girls, all] or None when not applicable
	kwargs for kind-specific params:
	  - nearby: max_km (int)
	"""

	def encode(page_target: int) -> str:
		parts: list[str] = ["search_page", kind]
		if kind == "nearby":
			max_km = kwargs.get("max_km")
			parts.extend([str(max_km), str(gender or "all"), str(page_target)])
		elif kind == "by_location":
			parts.extend([str(gender or "all"), str(page_target)])
		else:
			# generic gendered kinds
			if gender is not None:
				parts.extend([str(gender), str(page_target)])
			else:
				parts.append(str(page_target))
		return ":".join(parts)

	prev_page = page - 1
	next_page = page + 1

	buttons = [
		[
			InlineKeyboardButton(text="صفحه بعدی ➡️", callback_data=encode(next_page)),
			InlineKeyboardButton(text="⬅️ صفحه قبلی", callback_data=encode(prev_page)),
		]
	]
	return InlineKeyboardMarkup(inline_keyboard=buttons)


