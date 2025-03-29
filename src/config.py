from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Setting(BaseSettings):
    DB_HOST: str
    DB_PORT: str
    DB_USER: str
    DB_PASS: str
    DB_NAME: str

    @property
    def DB_URL(self):
        return (
            f'postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@'\
            f'{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}'
        )

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parent.parent / '.env'
    )


setting = Setting()