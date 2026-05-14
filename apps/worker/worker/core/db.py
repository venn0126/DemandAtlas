from sqlalchemy import create_engine

from worker.core.config import settings

engine = create_engine(settings.database_url, pool_pre_ping=True)
