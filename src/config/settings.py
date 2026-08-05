import logging.config
from typing import Any

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.config.app import AppConfig
from src.config.broker import BrokerConfig
from src.config.database import DatabaseConfig
from src.config.logging_config import LOGGING_CONFIG


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        case_sensitive=False,
        env_nested_delimiter="__",
        env_file=".env",
        extra="ignore",
    )

    app: AppConfig = Field(default_factory=AppConfig)  # type: ignore[arg-type]
    db: DatabaseConfig = Field(default_factory=DatabaseConfig)  # type: ignore[arg-type]
    broker: BrokerConfig = Field(default_factory=BrokerConfig)  # type: ignore[arg-type]
    external_api_base_url: str

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        logging.config.dictConfig(LOGGING_CONFIG)


settings = Settings()
