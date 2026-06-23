from pydantic import BaseSettings


class Settings(BaseSettings):
    app_name: str = "onejulian-backend"
    app_env: str = "dev"
    database_url: str = "sqlite:///./onejulian.db"

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
