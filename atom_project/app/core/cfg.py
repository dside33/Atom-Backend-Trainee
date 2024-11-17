from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: str
    DB_USER: str
    DB_PASS: str
    DB_NAME: str

    SECRET: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_HOURS: int
    ACCESS_COOKIE_EXPIRE_HOURS: int
    ISSUER: str

    class Config:
        env_file = ".env"


settings = Settings()
