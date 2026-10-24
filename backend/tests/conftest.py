import os
import tempfile

os.environ["DATABASE_URL"] = f"sqlite:///{tempfile.mkdtemp()}/test.db"

import pytest

from app.database import Base, SessionLocal, engine
from app.services.forecast_selector import clear_cache


@pytest.fixture(autouse=True)
def fresh_db():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    clear_cache()
    yield
    clear_cache()


@pytest.fixture
def db():
    with SessionLocal() as session:
        yield session
