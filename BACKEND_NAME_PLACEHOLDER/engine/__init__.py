from sqlalchemy import Engine, create_engine

from BACKEND_NAME_PLACEHOLDER.config import Config
from BACKEND_NAME_PLACEHOLDER.model import Base


def get_engine() -> Engine:
    config = Config.get_instance()
    engine = create_engine(config.connection_string)
    Base.metadata.create_all(engine)
    return engine
