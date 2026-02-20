from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="SOCKETIO_", env_file=".env", env_file_encoding="utf-8"
    )

    host: str = "0.0.0.0"
    port: int = 5556
    cors_origins: str = "*"
    cors_methods: str = "GET,POST,PUT,DELETE,OPTIONS"
    cors_headers: str = "Content-Type,Authorization"
    cors_credentials: bool = True
    ping_timeout: int = 60
    ping_interval: int = 25
    max_http_buffer_size: int = 1000000
    async_mode: str = "asgi"
    logger_level: str = "INFO"
    json_serializer: str | None = None
    always_connect: bool = False
    namespaces: str = "/"

    @property
    def cors_origins_list(self) -> list[str]:
        if self.cors_origins == "*":
            return ["*"]
        return [origin.strip() for origin in self.cors_origins.split(",")]


settings = Settings()
