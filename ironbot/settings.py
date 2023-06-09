import os
from contextlib import contextmanager
from functools import cached_property
from pathlib import Path

from alembic.config import Config


class MissingSettingsError(Exception):
    pass


class Settings:
    @cached_property
    def base_dir(self):
        return Path(__file__).parent.parent

    @cached_property
    def database_url(self):
        url = os.environ.get("DATABASE_URL")
        if not url:
            raise MissingSettingsError("Missing DATABASE_URL environment variable.")
        return url

    @cached_property
    def alembic(self):
        config = Config(self.base_dir / "alembic.ini")
        config.set_main_option("sqlalchemy.url", self.database_url)
        return config
