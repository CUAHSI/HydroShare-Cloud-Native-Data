from functools import lru_cache
from typing import Any

from pydantic import BaseSettings, HttpUrl
from dotenv import load_dotenv

# had to use load_dotenv() to get the env variables to work during testing
load_dotenv()


class Settings(BaseSettings):
    database_name: str
    db_username: str
    db_password: str
    db_host: str
    db_protocol: str
    testing: bool = False

    oidc_issuer: str
    hydroshare_meta_read_url: HttpUrl
    hydroshare_file_read_url: HttpUrl
    search_relevance_score_threshold: float = 1.4

    def __init__(self, **data: Any) -> None:
        super().__init__(**data)
        if self.testing:
            self.database_name = f"{self.database_name}"

    @property
    def db_connection_string(self):
        return f"{self.db_protocol}://{self.db_username}:{self.db_password}@{self.db_host}/?retryWrites=true&w=majority"

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings():
    return Settings()
