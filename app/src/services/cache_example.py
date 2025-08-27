"""
مثال استفاده از سرویس کش مدیا

این فایل مثال‌هایی از نحوه استفاده از سرویس کش رو نشون می‌ده.
در پروژه واقعی باید این کدها رو در جای مناسب استفاده کنید.
"""

from src.services.cache import get_cache_service

# مثال ۱: ذخیره کردن مدیا
async def example_save_media(bot, file_id: str, file_type: str = "photo"):
    """مثال ذخیره کردن مدیا در کش"""
    cache_service = get_cache_service(bot)

    # ذخیره مدیا و گرفتن media_id
    media_id = await cache_service.save_media(file_id, file_type)

    if media_id:
        print(f"مدیا با موفقیت ذخیره شد. media_id: {media_id}")
        return media_id
    else:
        print("خطا در ذخیره مدیا")
        return None

# مثال ۲: گرفتن مدیا از کش
async def example_get_media(bot, media_id: int):
    """مثال گرفتن مدیا از کش"""
    cache_service = get_cache_service(bot)

    # گرفتن اطلاعات مدیا
    media_info = await cache_service.get_media(media_id)

    if media_info:
        message = media_info["message"]
        print(f"مدیا یافت شد: message_id={media_info['message_id']}")

        # ارسال مدیا به چت کاربر
        await cache_service.send_cached_media(chat_id=123456789, media_id=media_id)
        return True
    else:
        print("مدیا یافت نشد")
        return False

# مثال ۳: گرفتن media_id از message_id
async def example_get_media_id(bot, message_id: int):
    """مثال گرفتن media_id از message_id"""
    cache_service = get_cache_service(bot)

    media_id = await cache_service.get_media_id_by_message_id(message_id)

    if media_id:
        print(f"media_id برای message_id {message_id}: {media_id}")
        return media_id
    else:
        print("media_id یافت نشد")
        return None

# مثال ۴: حذف مدیا از کش
async def example_delete_media(bot, media_id: int):
    """مثال حذف مدیا از کش"""
    cache_service = get_cache_service(bot)

    success = await cache_service.delete_media(media_id)

    if success:
        print(f"مدیا {media_id} با موفقیت حذف شد")
        return True
    else:
        print("خطا در حذف مدیا")
        return False

# مثال استفاده در handlers
async def handle_user_photo(message):
    """مثال استفاده در handler برای ذخیره عکس کاربر"""
    from src.services.cache import get_cache_service

    if message.photo:
        cache_service = get_cache_service()

        # ذخیره عکس در کش
        file_id = message.photo[-1].file_id
        media_id = await cache_service.save_media(file_id, "photo")

        if media_id:
            # ذخیره media_id در پروفایل کاربر یا جای مناسب
            print(f"عکس کاربر ذخیره شد با media_id: {media_id}")

            # بعداً می‌تونید با داشتن media_id، عکس رو برای کاربر ارسال کنید
            await cache_service.send_cached_media(message.chat.id, media_id)
