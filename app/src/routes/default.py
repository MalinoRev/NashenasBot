from aiogram import Router
from aiogram.types import Message


router = Router(name="default")


@router.message()
async def handle_default(message: Message) -> None:
	await message.answer("Default handler: no specific reply found.")


