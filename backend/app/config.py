from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "NexotLab API"
    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000

    connect_database: bool = False
    # MySQL/MariaDB con pymysql (phpMyAdmin en localhost)
    database_url: str = "mysql+pymysql://root:@localhost:3306/proyectodecimo"

    high_score_threshold: float = 4.0
    low_score_threshold: float = 2.5
    random_seed: int = 42
    cors_origins: str = "http://localhost:5173,http://localhost:8443,http://127.0.0.1:5173"

    @property
    def cors_origin_list(self) -> list[str]:
        return [item.strip() for item in self.cors_origins.split(",") if item.strip()]

    @property
    def db_dialect(self) -> str:
        url = self.database_url.lower()
        if url.startswith("mysql"):
            return "mysql"
        if url.startswith("postgresql") or url.startswith("postgres"):
            return "postgresql"
        return "sqlite" if url.startswith("sqlite") else "other"


settings = Settings()
