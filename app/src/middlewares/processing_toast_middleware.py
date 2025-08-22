from typing import Any, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message

from src.context.messages.system.processing import get_message as get_processing_message


class ProcessingToastMiddleware(BaseMiddleware):
	async def __call__(
		self,
		handler: Callable[[Any, Dict[str, Any]], Any],
		event: Message | CallbackQuery,
		data: Dict[str, Any],
	) -> Any:
		# For most callback queries, immediately show a toast to improve UX.
		# Skip for pagination callbacks so handlers can show boundary alerts.
		if isinstance(event, CallbackQuery):
			data_str = getattr(event, "data", "") or ""
			if not data_str.startswith("search_page:"):
				try:
					await event.answer(get_processing_message(), show_alert=False)
				except Exception:
					# Non-fatal; proceed anyway
					pass
		return await handler(event, data)
