from aiogram.types import Message
from src.services.cache import CacheService


async def handle_test_cache(message: Message) -> None:
    """
    Test cache channel access - only for admin
    """
    user_id = message.from_user.id if message.from_user else 0

    # Check if user is admin (you might want to add proper admin check here)
    import os
    admin_id = int(os.getenv('TELEGRAM_ADMIN_USER_ID', 0))

    if user_id != admin_id:
        await message.reply("❌ این دستور فقط برای ادمین است.")
        return

    cache_service = CacheService(message.bot)

    # Test cache channel access
    result = await cache_service.test_cache_channel_access()

    response = "🧪 **تست دسترسی کانال کش:**\n\n"
    response += f"📋 Channel ID: `{result['channel_id']}`\n"
    response += f"⚙️ تنظیم شده: {'✅' if result['is_set'] else '❌'}\n"

    if result['error']:
        response += f"❌ خطا: `{result['error']}`\n"
        response += "\n🔧 **راه حل‌های ممکن:**\n"
        response += "1. ربات را ادمین کانال کنید\n"
        response += "2. CACHE_CHANNEL_ID را در .env چک کنید\n"
        response += "3. کانال را دوباره ایجاد کنید\n"
        response += "4. کانتینر را ری‌استارت کنید\n"
    else:
        response += f"✅ دسترسی: {'✅' if result['has_access'] else '❌'}\n"
        if result['channel_info']:
            response += f"📺 اطلاعات کانال:\n"
            response += f"  • نام: {result['channel_info']['title']}\n"
            response += f"  • نوع: {result['channel_info']['type']}\n"
        response += f"💬 ارسال پیام: {'✅' if result.get('can_send_messages', False) else '❌'}\n"

        if result.get('can_send_messages', False):
            response += "\n✅ کانال کش آماده استفاده است!"
        else:
            response += "\n⚠️ کانال کش تنظیم شده اما ربات نمی‌تواند پیام ارسال کند."

    await message.reply(response, parse_mode="Markdown")
