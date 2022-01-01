from sqlmodel import create_engine

from coin_tracker.config import settings


engine = create_engine(settings.database_url)
