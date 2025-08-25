"""
Example usage of the CacheService

This file demonstrates how to use the cache service for storing and retrieving media.
"""

from aiogram import Bot
from aiogram.types import Message
from src.services.cache import CacheService


async def example_usage(bot: Bot):
	"""
	Example of how to use the CacheService
	"""
	# Initialize cache service
	cache_service = CacheService(bot)
	
	# Example 1: Store media from a user message
	async def store_user_media(user_message: Message):
		# Store the media and get media.id
		media_id = await cache_service.store_media(user_message)
		if media_id:
			print(f"Media stored with ID: {media_id}")
			return media_id
		else:
			print("Failed to store media")
			return None
	
	# Example 2: Retrieve media using media.id
	async def retrieve_media(media_id: int):
		# Get the media from cache
		media_message = await cache_service.get_media(media_id)
		if media_message:
			print(f"Retrieved media: {media_message.message_id}")
			return media_message
		else:
			print("Media not found")
			return None
	
	# Example 3: Get media.id from a message
	async def get_media_id_from_message(message: Message):
		# Get media.id for a message
		media_id = await cache_service.get_media_id(message)
		if media_id:
			print(f"Media ID: {media_id}")
			return media_id
		else:
			print("Media ID not found")
			return None
	
	# Example 4: Delete media from cache
	async def delete_cached_media(media_id: int):
		# Delete media from cache
		success = await cache_service.delete_media(media_id)
		if success:
			print(f"Media {media_id} deleted successfully")
		else:
			print(f"Failed to delete media {media_id}")
		return success


# Usage in handlers:
"""
# In a message handler
@router.message()
async def handle_media_message(message: Message, bot: Bot):
	cache_service = CacheService(bot)
	
	# Store media in cache
	media_id = await cache_service.store_media(message)
	
	# Save media_id to user profile or database
	# user.avatar_media_id = media_id
	
	await message.reply(f"Media stored with ID: {media_id}")

# Later, when you want to send the media to someone
async def send_cached_media(chat_id: int, media_id: int, bot: Bot):
	cache_service = CacheService(bot)
	
	# Get media from cache
	media_message = await cache_service.get_media(media_id)
	if media_message:
		# Forward the media to the user
		await bot.forward_message(
			chat_id=chat_id,
			from_chat_id=cache_service.cache_channel_id,
			message_id=media_message.message_id
		)
"""
