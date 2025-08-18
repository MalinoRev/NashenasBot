from aiogram import Dispatcher
from aiogram.types import Message, Update

from src.routes.callbacks import router as callbacks_router
from src.routes.commands import router as commands_router
from src.routes.default import router as default_router
from src.routes.replies import router as replies_router
from src.middlewares.auth_middleware import AuthMiddleware
from src.middlewares.profile_middleware import ProfileMiddleware
from src.middlewares.channel_join_middleware import ChannelJoinMiddleware
from src.middlewares.processing_toast_middleware import ProcessingToastMiddleware
from src.middlewares.profile_completion_middleware import ProfileCompletionMiddleware


def build_dispatcher() -> Dispatcher:
	dp = Dispatcher()
	# Global middlewares (order matters)
	processing = ProcessingToastMiddleware()
	auth = AuthMiddleware()
	profile = ProfileMiddleware()
	channels_guard = ChannelJoinMiddleware()
	profile_completion = ProfileCompletionMiddleware()
	# Processing toast must run first
	dp.message.middleware(processing)
	dp.callback_query.middleware(processing)
	# Then auth/profile/required-channels
	dp.message.middleware(auth)
	dp.callback_query.middleware(auth)
	dp.message.middleware(profile)
	dp.callback_query.middleware(profile)
	# Channel membership check MUST run after other middlewares
	dp.message.middleware(channels_guard)
	dp.callback_query.middleware(channels_guard)
	# Profile completion reward should run last
	dp.message.middleware(profile_completion)
	dp.callback_query.middleware(profile_completion)
	# Attach routers
	dp.include_router(commands_router)
	dp.include_router(callbacks_router)

	# Replies router should see plain text messages first
	dp.include_router(replies_router)

	# Default router last
	dp.include_router(default_router)

	return dp


