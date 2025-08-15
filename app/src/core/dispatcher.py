from aiogram import Dispatcher
from aiogram.types import Message, Update

from src.routes.callbacks import router as callbacks_router
from src.routes.commands import router as commands_router
from src.routes.default import router as default_router
from src.routes.replies import router as replies_router
from src.middlewares.auth_middleware import AuthMiddleware
from src.middlewares.profile_middleware import ProfileMiddleware


def build_dispatcher() -> Dispatcher:
	dp = Dispatcher()
	# Global middlewares
	auth = AuthMiddleware()
	profile = ProfileMiddleware()
	dp.message.middleware(auth)
	dp.callback_query.middleware(auth)
	dp.message.middleware(profile)
	dp.callback_query.middleware(profile)
	# Attach routers
	dp.include_router(commands_router)
	dp.include_router(callbacks_router)

	# Replies router should see plain text messages first
	dp.include_router(replies_router)

	# Default router last
	dp.include_router(default_router)

	return dp


