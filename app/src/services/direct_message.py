import json
from typing import Union, Optional
from aiogram import Bot
from aiogram.types import Message
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_session
from src.databases.directs import Direct
from src.databases.users import User
from src.services.cache import CacheService


class DirectMessageService:
	def __init__(self, bot: Bot):
		self.bot = bot
		self.cache_service = CacheService(bot)

	async def send_direct_message(
		self, 
		from_user_id: int, 
		to_user_id: int, 
		message: Union[str, Message]
	) -> Optional[int]:
		"""
		Send a direct message and store it in the directs table
		
		Args:
			from_user_id: ID of the sender user
			to_user_id: ID of the recipient user
			message: Text message or Message object with media
			
		Returns:
			int: The direct message ID if successful, None otherwise
		"""
		try:
			content_data = {}
			
			if isinstance(message, str):
				# Text-only message
				content_data = {
					"message": message,
					"type": "text",
					"media_id": None
				}
			elif isinstance(message, Message):
				# Message with potential media
				if message.text:
					content_data["message"] = message.text
				else:
					content_data["message"] = ""
				
				# Check for media types
				if message.photo:
					content_data["type"] = "image"
					# Store media in cache
					media_id = await self.cache_service.store_media(message)
					content_data["media_id"] = media_id
				elif message.video:
					content_data["type"] = "video"
					media_id = await self.cache_service.store_media(message)
					content_data["media_id"] = media_id
				elif message.document:
					content_data["type"] = "document"
					media_id = await self.cache_service.store_media(message)
					content_data["media_id"] = media_id
				elif message.audio:
					content_data["type"] = "audio"
					media_id = await self.cache_service.store_media(message)
					content_data["media_id"] = media_id
				elif message.voice:
					content_data["type"] = "voice"
					media_id = await self.cache_service.store_media(message)
					content_data["media_id"] = media_id
				else:
					content_data["type"] = "text"
					content_data["media_id"] = None

			# Convert to JSON string
			content_json = json.dumps(content_data, ensure_ascii=False)
			
			# Store in database
			async with get_session() as session:
				direct_message = Direct(
					user_id=from_user_id,
					target_id=to_user_id,
					content=content_json
				)
				session.add(direct_message)
				await session.flush()
				await session.commit()
				
				return direct_message.id

		except Exception as e:
			print(f"Error sending direct message: {e}")
			return None

	async def get_direct_message(self, direct_id: int) -> Optional[dict]:
		"""
		Get a direct message by its ID
		
		Args:
			direct_id: The direct message ID
			
		Returns:
			dict: Message data with parsed content, or None if not found
		"""
		try:
			async with get_session() as session:
				direct: Direct = await session.scalar(
					select(Direct).where(Direct.id == direct_id)
				)
				
				if not direct:
					return None

				# Parse JSON content
				content_data = json.loads(direct.content)
				
				return {
					"id": direct.id,
					"user_id": direct.user_id,
					"target_id": direct.target_id,
					"content": content_data,
					"opened_at": direct.opened_at,
					"created_at": direct.created_at
				}

		except Exception as e:
			print(f"Error getting direct message: {e}")
			return None

	async def get_user_directs(self, user_id: int, limit: int = 50) -> list[dict]:
		"""
		Get all direct messages for a user (both sent and received)
		
		Args:
			user_id: The user ID
			limit: Maximum number of messages to return
			
		Returns:
			list: List of direct message data
		"""
		try:
			async with get_session() as session:
				# Get messages sent by user
				sent_messages = await session.scalars(
					select(Direct)
					.where(Direct.user_id == user_id)
					.order_by(Direct.created_at.desc())
					.limit(limit)
				)
				
				# Get messages received by user
				received_messages = await session.scalars(
					select(Direct)
					.where(Direct.target_id == user_id)
					.order_by(Direct.created_at.desc())
					.limit(limit)
				)
				
				# Combine and sort by creation time
				all_messages = []
				
				for msg in sent_messages:
					content_data = json.loads(msg.content)
					all_messages.append({
						"id": msg.id,
						"user_id": msg.user_id,
						"target_id": msg.target_id,
						"content": content_data,
						"opened_at": msg.opened_at,
						"created_at": msg.created_at,
						"direction": "sent"
					})
				
				for msg in received_messages:
					content_data = json.loads(msg.content)
					all_messages.append({
						"id": msg.id,
						"user_id": msg.user_id,
						"target_id": msg.target_id,
						"content": content_data,
						"opened_at": msg.opened_at,
						"created_at": msg.created_at,
						"direction": "received"
					})
				
				# Sort by creation time (newest first)
				all_messages.sort(key=lambda x: x["created_at"], reverse=True)
				
				return all_messages[:limit]

		except Exception as e:
			print(f"Error getting user directs: {e}")
			return []

	async def mark_as_opened(self, direct_id: int) -> bool:
		"""
		Mark a direct message as opened
		
		Args:
			direct_id: The direct message ID
			
		Returns:
			bool: True if successful, False otherwise
		"""
		try:
			from datetime import datetime
			
			async with get_session() as session:
				direct: Direct = await session.scalar(
					select(Direct).where(Direct.id == direct_id)
				)
				
				if not direct:
					return False

				direct.opened_at = datetime.utcnow()
				await session.commit()
				
				return True

		except Exception as e:
			print(f"Error marking message as opened: {e}")
			return False

	async def get_media_from_direct(self, direct_id: int) -> Optional[Message]:
		"""
		Get media from a direct message using the cache service
		
		Args:
			direct_id: The direct message ID
			
		Returns:
			Message: The cached media message, or None if not found
		"""
		try:
			direct_data = await self.get_direct_message(direct_id)
			if not direct_data:
				return None

			content = direct_data["content"]
			media_id = content.get("media_id")
			
			if not media_id:
				return None

			# Get media from cache
			return await self.cache_service.get_media(media_id)

		except Exception as e:
			print(f"Error getting media from direct: {e}")
			return None
