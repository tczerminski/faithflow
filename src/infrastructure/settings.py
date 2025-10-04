from pydantic import BaseModel, SecretStr, HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class YoutubeSettings(BaseModel):
    api_key: SecretStr
    channel_id: str
    url: HttpUrl


class FaithflowSettings(BaseSettings):
    youtube: YoutubeSettings

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
    )
