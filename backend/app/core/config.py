from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "WEOS"
    VERSION: str = "1.0.0"


settings = Settings()
