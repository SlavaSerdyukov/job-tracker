from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Job Tracker API"
    secret_key: str
    access_token_expire_minutes: int = 60

    postgres_host: str = "db"
    postgres_port: int = 5432
    postgres_db: str = "jobtracker"
    postgres_user: str = "jobtracker"
    postgres_password: str = "jobtracker"

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg2://"
            f"{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
