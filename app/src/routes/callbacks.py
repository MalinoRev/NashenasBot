from aiogram import Router
from aiogram.types import CallbackQuery


router = Router(name="callbacks")


@router.callback_query()
async def handle_any_callback(callback: CallbackQuery) -> None:
	data = callback.data or ""
	print(f"LOG: handle_any_callback called with data: '{data}'")
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
	if data.startswith("profile_chat_request:"):
		print(f"LOG: Routing callback to profile_chat_request handler: {data}")
		from src.handlers.callbacks.visitor_profile_chat_request import handle_visitor_profile_chat_request
		await handle_visitor_profile_chat_request(callback)
		return
	if data.startswith("chat_request_reject:"):
		from src.handlers.callbacks.chat_request_decisions import handle_chat_request_reject
		await handle_chat_request_reject(callback)
		return
	if data.startswith("chat_request_accept:"):
		from src.handlers.callbacks.chat_request_decisions import handle_chat_request_accept
		await handle_chat_request_accept(callback)
		return

	if data.startswith("chat_request_view:"):
		print(f"LOG: Routing callback to chat_request_view handler: {data}")
		from src.handlers.callbacks.chat_request_view import handle_chat_request_view
		await handle_chat_request_view(callback)
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
	if data.startswith("profile_direct:") or data.startswith("direct_confirm:"):
		from src.handlers.callbacks.visitor_profile_direct import handle_visitor_profile_direct
		await handle_visitor_profile_direct(callback)
		return
	if data.startswith("direct_send_confirm:"):
		from src.handlers.callbacks.direct_send_flow import handle_direct_send_confirm
		await handle_direct_send_confirm(callback)
		return
	if data.startswith("direct_send_cancel:"):
		from src.handlers.callbacks.direct_send_flow import handle_direct_send_cancel
		await handle_direct_send_cancel(callback)
		return
	if data.startswith("direct_send_edit:"):
		from src.handlers.callbacks.direct_send_flow import handle_direct_send_edit
		await handle_direct_send_edit(callback)
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
	if data == "profile:edit":
		from src.handlers.callbacks.profile_edit_menu import handle_profile_edit_menu
		await handle_profile_edit_menu(callback)
		return
	if data == "profile_edit:name":
		from src.handlers.callbacks.profile_edit_name import handle_profile_edit_name
		await handle_profile_edit_name(callback)
		return
	if data == "profile_edit:gender":
		from src.handlers.callbacks.profile_edit_gender import handle_profile_edit_gender
		await handle_profile_edit_gender(callback)
		return
	if data == "profile_edit:age":
		from src.handlers.callbacks.profile_edit_age import handle_profile_edit_age
		await handle_profile_edit_age(callback)
		return
	if data == "profile_edit:state_city":
		from src.handlers.callbacks.profile_edit_state_city import handle_profile_edit_state_city
		await handle_profile_edit_state_city(callback)
		return
	if data == "profile_edit:photo":
		from src.handlers.callbacks.profile_edit_photo import handle_profile_edit_photo
		await handle_profile_edit_photo(callback)
		return
	if data == "profile_edit_photo:cancel":
		from src.handlers.callbacks.profile_edit_photo_cancel import handle_profile_edit_photo_cancel
		await handle_profile_edit_photo_cancel(callback)
		return
	if data == "advanced:silent_mode":
		from src.handlers.callbacks.advanced_silent_mode import handle_advanced_silent_mode
		await handle_advanced_silent_mode(callback)
		return
	if data == "advanced:alarms":
		from src.handlers.callbacks.advanced_alarms import handle_advanced_alarms
		await handle_advanced_alarms(callback)
		return
	if data == "advanced:chat_filter":
		from src.handlers.callbacks.advanced_chat_filter import handle_advanced_chat_filter
		await handle_advanced_chat_filter(callback)
		return
	if data.startswith("advanced_filter_gender:"):
		from src.handlers.callbacks.advanced_chat_filter_gender_set import (
			handle_advanced_chat_filter_gender_set,
		)
		await handle_advanced_chat_filter_gender_set(callback)
		return
	if data.startswith("advanced_filter_distance:"):
		from src.handlers.callbacks.advanced_chat_filter_distance_set import (
			handle_advanced_chat_filter_distance_set,
		)
		await handle_advanced_chat_filter_distance_set(callback)
		return
	if data.startswith("advanced_filter_age_from:"):
		from src.handlers.callbacks.advanced_chat_filter_age_from_set import (
			handle_advanced_chat_filter_age_from_set,
		)
		await handle_advanced_chat_filter_age_from_set(callback)
		return
	if data.startswith("advanced_filter_age_until:"):
		from src.handlers.callbacks.advanced_chat_filter_age_until_set import (
			handle_advanced_chat_filter_age_until_set,
		)
		await handle_advanced_chat_filter_age_until_set(callback)
		return
	if data.startswith("advanced_filter_review:"):
		from src.handlers.callbacks.advanced_chat_filter_review_set import (
			handle_advanced_chat_filter_review_set,
		)
		await handle_advanced_chat_filter_review_set(callback)
		return
	if data.startswith("advanced_silent:"):
		from src.handlers.callbacks.advanced_silent_mode_set import handle_advanced_silent_mode_set
		await handle_advanced_silent_mode_set(callback)
		return
	if data.startswith("advanced_alarms:"):
		from src.handlers.callbacks.advanced_alarms_toggle import handle_advanced_alarms_toggle
		await handle_advanced_alarms_toggle(callback)
		return
	if data == "search:same_province":
		from src.context.messages.callbacks.search_same_province import get_message as get_msg
		from src.context.keyboards.inline.search_same_province import build_keyboard as build_kb
		try:
			await callback.message.delete()
		except Exception:
			pass
		await callback.message.answer(get_msg(), reply_markup=build_kb())
		await callback.answer()
		return
	if data.startswith("search_same_province:"):
		from src.handlers.callbacks.search_same_province import handle_search_same_province
		await handle_search_same_province(callback)
		return
	if data == "search:same_age":
		from src.context.messages.callbacks.search_same_age import get_message as get_msg
		from src.context.keyboards.inline.search_same_age import build_keyboard as build_kb
		try:
			await callback.message.delete()
		except Exception:
			pass
		await callback.message.answer(get_msg(), reply_markup=build_kb())
		await callback.answer()
		return
	if data.startswith("search_same_age:"):
		from src.handlers.callbacks.search_same_age import handle_search_same_age
		await handle_search_same_age(callback)
		return
	if data == "search:new_users":
		from src.context.messages.callbacks.search_new_users import get_message as get_msg
		from src.context.keyboards.inline.search_new_users import build_keyboard as build_kb
		try:
			await callback.message.delete()
		except Exception:
			pass
		await callback.message.answer(get_msg(), reply_markup=build_kb())
		await callback.answer()
		return
	if data.startswith("search_new_users:"):
		from src.handlers.callbacks.search_new_users import handle_search_new_users
		await handle_search_new_users(callback)
		return
	if data == "search:no_chats":
		from src.context.messages.callbacks.search_no_chats import get_message as get_msg
		from src.context.keyboards.inline.search_no_chats import build_keyboard as build_kb
		try:
			await callback.message.delete()
		except Exception:
			pass
		await callback.message.answer(get_msg(), reply_markup=build_kb())
		await callback.answer()
		return
	if data.startswith("search_no_chats:"):
		from src.handlers.callbacks.search_no_chats import handle_search_no_chats
		await handle_search_no_chats(callback)
		return
	if data == "search:popular":
		from src.context.messages.callbacks.search_popular import get_message as get_msg
		from src.context.keyboards.inline.search_popular import build_keyboard as build_kb
		try:
			await callback.message.delete()
		except Exception:
			pass
		await callback.message.answer(get_msg(), reply_markup=build_kb())
		await callback.answer()
		return
	if data.startswith("search_popular:"):
		from src.handlers.callbacks.search_popular import handle_search_popular
		await handle_search_popular(callback)
		return
	if data == "search:by_location":
		from src.handlers.callbacks.search_by_location import handle_search_by_location_request
		await handle_search_by_location_request(callback)
		return
	if data == "search:special_contact":
		from src.context.messages.callbacks.search_special_contact_prompt import get_message as get_msg
		from sqlalchemy import select
		from src.core.database import get_session
		from src.databases.users import User
		try:
			await callback.message.delete()
		except Exception:
			pass
		user_id = callback.from_user.id if callback.from_user else 0
		async with get_session() as session:
			user: User | None = await session.scalar(select(User).where(User.user_id == user_id))
			if not user:
				await callback.answer()
				return
			user.step = "search_special_contact"
			await session.commit()
		from src.context.keyboards.reply.special_contact import build_back_keyboard
		kb, _ = build_back_keyboard()
		await callback.message.answer(get_msg(), reply_markup=kb)
		await callback.answer()
		return
	if data == "search:recent_chats":
		from src.context.messages.callbacks.search_recent_chats import get_message as get_msg
		from src.context.keyboards.inline.search_recent_chats import build_keyboard as build_kb
		try:
			await callback.message.delete()
		except Exception:
			pass
		await callback.message.answer(get_msg(), reply_markup=build_kb())
		await callback.answer()
		return
	if data.startswith("search_recent_chats:"):
		from src.handlers.callbacks.search_recent_chats import handle_search_recent_chats
		await handle_search_recent_chats(callback)
		return
	if data.startswith("search_by_location_gender:"):
		# Retrieve temp coords and run location search with chosen gender
		from sqlalchemy import select
		from src.core.database import get_session
		from src.databases.users import User
		from src.services.temp_location_cache import get_temp_location
		from src.services.location_search import generate_location_list

		gender = "all"
		if data.endswith(":male"):
			gender = "boys"
		elif data.endswith(":female"):
			gender = "girls"
		user_id = callback.from_user.id if callback.from_user else 0
		async with get_session() as session:
			user: User | None = await session.scalar(select(User).where(User.user_id == user_id))
			if not user:
				await callback.answer()
				return
		coords = get_temp_location(user.id)
		try:
			await callback.message.delete()
		except Exception:
			pass
		if not coords:
			await callback.message.answer("⚠️ ابتدا موقعیت مکانی خود را ارسال کنید.")
			await callback.answer()
			return
		lat, lon = coords
		text, ok, has_next, has_items = await generate_location_list(user_id, lat, lon, 100, gender, page=1)
		from src.context.keyboards.inline.search_pagination import build_keyboard as build_pagination_kb
		kb = build_pagination_kb("by_location", page=1, gender=gender, has_next=has_next)
		await callback.message.answer(text, parse_mode="HTML", reply_markup=kb)
		await callback.answer()
		return
	if data.startswith("search_page:"):
		# Unified pagination handler
		# Patterns:
		# search_page:same_province:gender:page
		# search_page:same_age:gender:page
		# search_page:new_users:gender:page
		# search_page:no_chats:gender:page
		# search_page:popular:gender:page
		# search_page:recent_chats:gender:page
		# search_page:nearby:max_km:gender:page
		# search_page:by_location:gender:page  (uses temp location)
		parts = data.split(":")
		if len(parts) < 4:
			await callback.answer()
			return
		_, kind, *rest = parts
		page = 1
		gender = "all"
		max_km = None
		if kind == "nearby":
			# rest: [max_km, gender, page]
			if len(rest) >= 3:
				max_km = int(rest[0])
				gender = rest[1]
				page = int(rest[2])
		elif kind in {"same_province", "same_age", "new_users", "no_chats", "popular", "recent_chats", "by_location"}:
			# rest: [gender, page]
			if len(rest) >= 2:
				gender = rest[0]
				page = int(rest[1])
		else:
			await callback.answer()
			return

		from sqlalchemy import select
		from src.core.database import get_session
		from src.databases.users import User
		async with get_session() as session:
			user = await session.scalar(select(User).where(User.user_id == (callback.from_user.id if callback.from_user else 0)))
			if not user:
				await callback.answer()
				return

		from src.context.keyboards.inline.search_pagination import build_keyboard as build_pagination_kb
		kb = None
		text = ""
		at_first_page = page <= 1
		at_last_page = False
		has_items = True
		if kind == "same_province":
			from src.services.state_search import generate_state_list
			text, ok, has_next, has_items = await generate_state_list(callback.from_user.id if callback.from_user else 0, gender, page=page)
			at_last_page = not has_next
			kb = build_pagination_kb("same_province", page=page, gender=gender, has_next=has_next)
		elif kind == "same_age":
			from src.services.age_search import generate_same_age_list
			text, ok, has_next, has_items = await generate_same_age_list(callback.from_user.id if callback.from_user else 0, gender, page=page)
			at_last_page = not has_next
			kb = build_pagination_kb("same_age", page=page, gender=gender, has_next=has_next)
		elif kind == "new_users":
			from src.services.new_users_search import generate_new_users_list
			text, ok, has_next, has_items = await generate_new_users_list(callback.from_user.id if callback.from_user else 0, gender, page=page)
			at_last_page = not has_next
			kb = build_pagination_kb("new_users", page=page, gender=gender, has_next=has_next)
		elif kind == "no_chats":
			from src.services.no_chats_search import generate_no_chats_list
			text, ok, has_next, has_items = await generate_no_chats_list(callback.from_user.id if callback.from_user else 0, gender, page=page)
			at_last_page = not has_next
			kb = build_pagination_kb("no_chats", page=page, gender=gender, has_next=has_next)
		elif kind == "popular":
			from src.services.popular_search import generate_popular_list
			text, ok, has_next, has_items = await generate_popular_list(callback.from_user.id if callback.from_user else 0, gender, page=page)
			at_last_page = not has_next
			kb = build_pagination_kb("popular", page=page, gender=gender, has_next=has_next)
		elif kind == "recent_chats":
			from src.services.recent_chats_search import generate_recent_chats_list
			text, ok, has_next, has_items = await generate_recent_chats_list(callback.from_user.id if callback.from_user else 0, gender, page=page)
			at_last_page = not has_next
			kb = build_pagination_kb("recent_chats", page=page, gender=gender, has_next=has_next)
		elif kind == "nearby":
			from src.services.nearby_search import generate_nearby_list
			text, ok, has_next, has_items = await generate_nearby_list(callback.from_user.id if callback.from_user else 0, int(max_km or 5), gender, page=page)
			at_last_page = not has_next
			kb = build_pagination_kb("nearby", page=page, gender=gender, has_next=has_next, max_km=int(max_km or 5))
		elif kind == "by_location":
			from src.services.temp_location_cache import get_temp_location
			coords = get_temp_location(user.id)
			if not coords:
				await callback.message.answer("⚠️ ابتدا موقعیت مکانی خود را ارسال کنید.")
				await callback.answer()
				return
			from src.services.location_search import generate_location_list
			lat, lon = coords
			text, ok, has_next, has_items = await generate_location_list(callback.from_user.id if callback.from_user else 0, lat, lon, 100, gender, page=page)
			at_last_page = not has_next
			kb = build_pagination_kb("by_location", page=page, gender=gender, has_next=has_next)
		else:
			await callback.answer()
			return

		# Bound alerts
		# Bounds checks BEFORE deleting current message
		from src.context.alerts.search_bounds import get_first_page_message, get_last_page_message
		if page <= 1 and at_first_page:
			await callback.answer(get_first_page_message(), show_alert=True)
			return
		if not has_items and at_last_page:
			await callback.answer(get_last_page_message(), show_alert=True)
			return

		# Now safe to delete previous message and show new page
		try:
			await callback.message.delete()
		except Exception:
			pass

		await callback.message.answer(text, parse_mode="HTML", reply_markup=kb)
		await callback.answer()
		return
	if data.startswith("chat_end_no:"):
		from src.handlers.callbacks.chat_end_confirm import handle_chat_end_no
		await handle_chat_end_no(callback)
		return
	if data.startswith("chat_end_yes:"):
		from src.handlers.callbacks.chat_end_confirm import handle_chat_end_yes
		await handle_chat_end_yes(callback)
		return
	if data.startswith("profile_direct:") or data.startswith("direct_confirm:"):
		from src.handlers.callbacks.visitor_profile_direct import handle_visitor_profile_direct
		await handle_visitor_profile_direct(callback)
		return
	if data.startswith("profile_like:") or data.startswith("profile_block_toggle:") or data.startswith("profile_contact_toggle:"):
		from src.handlers.callbacks.visitor_profile_actions import handle_visitor_profile_action
		await handle_visitor_profile_action(callback)
		return
	if data == "coin:buy_vip":
		from src.handlers.callbacks.coin_buy_vip import handle_coin_buy_vip
		await handle_coin_buy_vip(callback)
		return
	if data == "advanced:delete_account":
		from src.handlers.callbacks.advanced_delete_account import handle_advanced_delete_account
		await handle_advanced_delete_account(callback)
		return
	if data == "advanced_delete:pay":
		from src.handlers.callbacks.advanced_delete_account_pay import handle_advanced_delete_account_pay
		await handle_advanced_delete_account_pay(callback)
		return
	if data.startswith("coin:buy:"):
		from src.handlers.callbacks.coin_buy import handle_coin_buy
		await handle_coin_buy(callback)
		return
	if data.startswith("direct_view:"):
		from src.handlers.callbacks.direct_view import handle_direct_view
		await handle_direct_view(callback)
		return
	if data.startswith("direct_list_send_confirm:"):
		from src.handlers.callbacks.direct_list_send_flow import handle_direct_list_send_confirm
		await handle_direct_list_send_confirm(callback)
		return
	if data.startswith("direct_list_send_cancel:"):
		from src.handlers.callbacks.direct_list_send_flow import handle_direct_list_send_cancel
		await handle_direct_list_send_cancel(callback)
		return
	if data.startswith("direct_list_send_edit:"):
		from src.handlers.callbacks.direct_list_send_flow import handle_direct_list_send_edit
		await handle_direct_list_send_edit(callback)
		return
	if data.startswith("direct_list:"):
		from src.handlers.callbacks.direct_list import handle_direct_list
		await handle_direct_list(callback)
		return
	if data.startswith("admin_rewards:"):
		from src.handlers.callbacks.admin_rewards_menu import handle_admin_rewards_menu
		await handle_admin_rewards_menu(callback)
		return
	if data.startswith("admin_management:"):
		from src.handlers.callbacks.admin_management import handle_admin_management
		await handle_admin_management(callback)
		return
	if data.startswith("support_management:"):
		from src.handlers.callbacks.support_management import handle_support_management
		await handle_support_management(callback)
		return
	if data.startswith("admin_add_confirm:"):
		from src.handlers.callbacks.admin_add_confirm import handle_admin_add_confirm
		await handle_admin_add_confirm(callback)
		return
	if data.startswith("admin_remove_confirm:"):
		from src.handlers.callbacks.admin_remove_confirm import handle_admin_remove_confirm
		await handle_admin_remove_confirm(callback)
		return
	if data.startswith("support_add_confirm:"):
		from src.handlers.callbacks.support_add_confirm import handle_support_add_confirm
		await handle_support_add_confirm(callback)
		return
	if data.startswith("support_remove_confirm:"):
		from src.handlers.callbacks.support_remove_confirm import handle_support_remove_confirm
		await handle_support_remove_confirm(callback)
		return
	if data.startswith("pricing:"):
		from src.handlers.callbacks.pricing_management import handle_pricing_management
		await handle_pricing_management(callback)
		return
	if data.startswith("bot_settings:"):
		from src.handlers.callbacks.bot_settings import handle_bot_settings
		await handle_bot_settings(callback)
		return
	if data.startswith("bot_settings_branding:"):
		from src.handlers.callbacks.bot_settings import handle_bot_settings
		await handle_bot_settings(callback)
		return
	if data.startswith("financial:"):
		from src.handlers.callbacks.financial_management import handle_financial_callbacks
		await handle_financial_callbacks(callback)
		return
	if data.startswith("financial_page:"):
		from src.handlers.callbacks.financial_management import handle_financial_callbacks
		await handle_financial_callbacks(callback)
		return
	if data.startswith("bot_settings_maintenance:"):
		from src.handlers.callbacks.bot_settings_maintenance import handle_maintenance_mode_toggle
		await handle_maintenance_mode_toggle(callback)
		return
	await callback.answer()
	await callback.message.answer("❌ در هنگام پردازش درخواست شما خطایی رخ داد ❌")


