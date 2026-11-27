import os
import unittest
from pathlib import Path

from alembic.config import Config
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from alembic import command
from db import get_db
from main import app

PROJECT_ROOT = Path(__file__).resolve().parents[2]


class IntegrationTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        load_dotenv(PROJECT_ROOT / ".env.test", override=True)
        database_url = os.getenv("DATABASE_URL", "")

        cls.engine = create_engine(database_url)
        database = cls.engine.url.database or ""
        if not database.endswith("_test"):
            raise RuntimeError(
                f"Integration tests needs test database (name ends with _test), now: '{database}'"
            )

        command.upgrade(Config(PROJECT_ROOT / "alembic.ini"), "head")

        cls.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=cls.engine)

        def get_test_db():
            db = cls.SessionLocal()
            try:
                yield db
            finally:
                db.close()

        app.dependency_overrides[get_db] = get_test_db
        cls.client = cls.enterClassContext(TestClient(app))

    @classmethod
    def tearDownClass(cls):
        app.dependency_overrides.pop(get_db, None)
        cls.engine.dispose()

    def setUp(self):
        with self.engine.begin() as connection:
            connection.execute(text("TRUNCATE TABLE users RESTART IDENTITY CASCADE"))

        self.session = self.SessionLocal()

    def tearDown(self):
        self.session.close()