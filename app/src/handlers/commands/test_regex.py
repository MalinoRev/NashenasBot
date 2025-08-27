from aiogram.types import Message
from src.middlewares.link_filter_middleware import LinkFilterMiddleware


async def handle_test_regex(message: Message) -> None:
    """
    Test regex patterns - only for admin
    """
    user_id = message.from_user.id if message.from_user else 0

    # Check if user is admin
    import os
    admin_id = int(os.getenv('TELEGRAM_ADMIN_USER_ID', 0))

    if user_id != admin_id:
        await message.reply("❌ این دستور فقط برای ادمین است.")
        return

    # Get the text to test
    command_parts = message.text.split(maxsplit=1)
    if len(command_parts) < 2:
        await message.reply("❌ استفاده: /test_regex <متن برای تست>")
        return

    test_text = command_parts[1]

    # Test patterns
    middleware = LinkFilterMiddleware()
    results = middleware.test_patterns(test_text)

    response = f"🧪 **تست Regex:**\n\n"
    response += f"📝 **متن تست:** `{test_text}`\n\n"
    response += f"🔍 **نتایج تشخیص:**\n"

    pattern_names = {
        'url': 'لینک وب',
        'telegram': 'لینک تلگرام',
        'email': 'ایمیل',
        'username': 'یوزرنیم (@)',
        'username_alt': 'یوزرنیم Alt',
        'phone': 'شماره تلفن'
    }

    blocked = False
    for pattern_key, detected in results.items():
        status = "✅" if detected else "❌"
        pattern_name = pattern_names.get(pattern_key, pattern_key)
        response += f"  • {pattern_name}: {status}\n"
        if detected:
            blocked = True

    response += f"\n🚫 **نتیجه کلی:** {'بلاک می‌شود' if blocked else 'مجاز است'}"

    await message.reply(response, parse_mode="Markdown")
