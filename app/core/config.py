import os
from typing import List, Union

from pydantic import AnyHttpUrl, BaseSettings, Field, validator


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = Field(
        os.getenv("SECRET_KEY"), env="SECRET_KEY"
    )  # secrets.token_urlsafe(32)
    # 60 minutes * 24 hours * 8 days = 8 days
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    # SERVER_NAME: str
    # SERVER_HOST: AnyHttpUrl
    PROJECT_NAME: str = Field(os.getenv("PROJECT_NAME"), env="PROJECT_NAME")
    # BASE_URL: str = Field(
    #     os.getenv("BASE_URL", "https://c543-41-190-2-225.ngrok.io"), env="BASE_URL"
    # )
    # BASE_API_URL: str = Field(
    #     os.getenv("BASE_API_URL", "https://c543-41-190-2-225.ngrok.io/api/v1"),
    #     env="BASE_API_URL",
    # )

    DATABASE_URL: str = Field(
        os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./database.db"),
        env="DATABASE_URL",
    )
    # BACKEND_CORS_ORIGINS is a JSON-formatted list of origins
    # e.g: '["http://localhost", "http://localhost:4200", "http://localhost:3000", \
    # "http://localhost:8080", "http://local.dockertoolbox.tiangolo.com"]'
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    class Config:
        case_sensitive = True
        env_file = "./app/.env"
        env_file_encoding = "utf-8"


settings = Settings()
# print(settings.dict())
