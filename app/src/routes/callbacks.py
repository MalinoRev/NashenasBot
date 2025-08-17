from aiogram import Router
from aiogram.types import CallbackQuery


router = Router(name="callbacks")


@router.callback_query()
async def handle_any_callback(callback: CallbackQuery) -> None:
	data = callback.data or ""
	if data == "random_match:random":
		from src.handlers.callbacks.random_match import handle_random_match_callback
		await handle_random_match_callback(callback)
		return
	if data == "random_match:male":
		from src.handlers.callbacks.random_match_male import handle_random_match_male_callback
		await handle_random_match_male_callback(callback)
		return
	if data == "random_match:female":
		from src.handlers.callbacks.random_match_female import handle_random_match_female_callback
		await handle_random_match_female_callback(callback)
		return
	if data == "random_match:nearby":
		from src.handlers.callbacks.random_match_nearby import handle_random_match_nearby_callback
		await handle_random_match_nearby_callback(callback)
		return
	if data == "random_match:state":
		from src.handlers.callbacks.random_match_state import handle_random_match_state_callback
		await handle_random_match_state_callback(callback)
		return
	if data == "nearby_distance:5":
		from src.context.messages.callbacks.nearby_distance_5 import get_message as get_msg
		from src.context.keyboards.inline.nearby_gender_5 import build_keyboard as build_kb
		try:
			await callback.message.delete()
		except Exception:
			pass
		await callback.message.answer(get_msg(), reply_markup=build_kb())
		await callback.answer()
		return
	if data == "nearby_distance:10":
		from src.context.messages.callbacks.nearby_distance_10 import get_message as get_msg
		from src.context.keyboards.inline.nearby_gender_10 import build_keyboard as build_kb
		try:
			await callback.message.delete()
		except Exception:
			pass
		await callback.message.answer(get_msg(), reply_markup=build_kb())
		await callback.answer()
		return
	if data == "nearby_distance:30":
		from src.context.messages.callbacks.nearby_distance_30 import get_message as get_msg
		from src.context.keyboards.inline.nearby_gender_30 import build_keyboard as build_kb
		try:
			await callback.message.delete()
		except Exception:
			pass
		await callback.message.answer(get_msg(), reply_markup=build_kb())
		await callback.answer()
		return
	if data == "nearby_distance:60":
		from src.context.messages.callbacks.nearby_distance_60 import get_message as get_msg
		from src.context.keyboards.inline.nearby_gender_60 import build_keyboard as build_kb
		try:
			await callback.message.delete()
		except Exception:
			pass
		await callback.message.answer(get_msg(), reply_markup=build_kb())
		await callback.answer()
		return
	if data == "nearby_distance:100":
		from src.context.messages.callbacks.nearby_distance_100 import get_message as get_msg
		from src.context.keyboards.inline.nearby_gender_100 import build_keyboard as build_kb
		try:
			await callback.message.delete()
		except Exception:
			pass
		await callback.message.answer(get_msg(), reply_markup=build_kb())
		await callback.answer()
		return
	if data.startswith("nearby_gender_5:"):
		from src.handlers.callbacks.nearby_gender_5 import handle_nearby_gender_5_callback
		await handle_nearby_gender_5_callback(callback)
		return
	if data.startswith("nearby_gender_10:"):
		from src.handlers.callbacks.nearby_gender_10 import handle_nearby_gender_10_callback
		await handle_nearby_gender_10_callback(callback)
		return
	if data.startswith("nearby_gender_30:"):
		from src.handlers.callbacks.nearby_gender_30 import handle_nearby_gender_30_callback
		await handle_nearby_gender_30_callback(callback)
		return
	if data.startswith("nearby_gender_60:"):
		from src.handlers.callbacks.nearby_gender_60 import handle_nearby_gender_60_callback
		await handle_nearby_gender_60_callback(callback)
		return
	if data.startswith("nearby_gender_100:"):
		from src.handlers.callbacks.nearby_gender_100 import handle_nearby_gender_100_callback
		await handle_nearby_gender_100_callback(callback)
		return
	if data == "nearby:request_location":
		from src.handlers.callbacks.nearby_request_location import handle_nearby_request_location
		await handle_nearby_request_location(callback)
		return
	if data == "profile:view_location":
		from src.handlers.callbacks.profile_view_location import handle_profile_view_location
		await handle_profile_view_location(callback)
		return
	if data == "profile:like_toggle":
		from src.handlers.callbacks.profile_like_toggle import handle_profile_like_toggle
		await handle_profile_like_toggle(callback)
		return
	if data == "profile:view_likers":
		from src.handlers.callbacks.profile_view_likers import handle_profile_view_likers
		await handle_profile_view_likers(callback)
		return
	if data == "profile:blocks":
		from src.handlers.callbacks.profile_view_blocks import handle_profile_view_blocks
		await handle_profile_view_blocks(callback)
		return
	if data == "profile:contacts":
		from src.handlers.callbacks.profile_view_contacts import handle_profile_view_contacts
		await handle_profile_view_contacts(callback)
		return
	if data == "profile:advanced_settings":
		from src.handlers.callbacks.profile_advanced_settings import handle_profile_advanced_settings
		await handle_profile_advanced_settings(callback)
		return
	await callback.answer()
	await callback.message.answer("Callback received, but not implemented yet.")


