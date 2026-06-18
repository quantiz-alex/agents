from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List


class Settings(BaseSettings):
    # Database
    db_server: str = Field(default="localhost", description="SQL Server host")
    db_name: str = Field(default="kc-pricing-system", description="Database name")
    db_user: str = Field(default="sa", description="Database user")
    db_password: str = Field(default="", description="Database password")
    db_driver: str = Field(default="ODBC Driver 18 for SQL Server", description="ODBC driver")
    use_sqlite: bool = Field(default=True, description="Use SQLite for development")

    # Auth
    secret_key: str = Field(default="changeme-use-a-strong-secret-in-production", description="JWT secret key")
    algorithm: str = Field(default="HS256", description="JWT algorithm")
    access_token_expire_minutes: int = Field(default=480, description="Token expiry in minutes (8h)")

    # CORS
    cors_origins: List[str] = Field(
        default=["http://localhost:8050", "http://127.0.0.1:8050"],
        description="Allowed CORS origins"
    )

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
