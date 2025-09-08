import os
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine


def _build_database_url() -> str:
	url = os.getenv("DATABASE_URL")
	if not url:
		raise RuntimeError("DATABASE_URL is not set")
	if url.startswith("mysql+pymysql://"):
		url = url.replace("mysql+pymysql://", "mysql+asyncmy://", 1)
	
	# Add charset parameters for UTF-8 support
	if "?" in url:
		url += "&charset=utf8mb4"
	else:
		url += "?charset=utf8mb4"
	
	return url


engine = create_async_engine(
	_build_database_url(), 
	pool_pre_ping=True, 
	future=True,
	connect_args={
		"charset": "utf8mb4",
		"use_unicode": True,
	}
)
SessionFactory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


@asynccontextmanager
async def get_session() -> AsyncSession:
	session = SessionFactory()
	try:
		yield session
	finally:
		await session.close()


