from aiogram import Dispatcher
from aiogram.types import Message, Update

from src.routes.callbacks import router as callbacks_router
from src.routes.commands import router as commands_router
from src.routes.default import router as default_router
from src.routes.replies import router as replies_router
from src.middlewares.auth_middleware import AuthMiddleware


def build_dispatcher() -> Dispatcher:
	dp = Dispatcher()
	# Global middlewares
	dp.message.middleware(AuthMiddleware())
	dp.callback_query.middleware(AuthMiddleware())
	# Attach routers
	dp.include_router(commands_router)
	dp.include_router(callbacks_router)

	# Replies router should see plain text messages first
	dp.include_router(replies_router)

	# Default router last
	dp.include_router(default_router)

	return dp


