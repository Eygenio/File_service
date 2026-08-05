import logging

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from src.config.settings import settings
from src.infrastructure.models.base import ModelBase

logger = logging.getLogger(__name__)

engine = create_async_engine(
    settings.db.database_url,
    echo=False,
    poolclass=NullPool,
)
async_session_factory = async_sessionmaker(
    engine,
    expire_on_commit=False,
)


async def create_tables() -> None:
    logger.info("Creating database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(ModelBase.metadata.create_all)
    logger.info("Tables created successfully")
