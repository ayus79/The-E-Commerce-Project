from pydantic_settings import BaseSettings


class SettingsConfig(BaseSettings):
    # app details
    app_name: str = "The E-Commerce Project"
    app_version: str = "0.1.0"
    app_env: str = "local"
    # api docs credentials
    api_docs_username: str = "admin@123"
    api_docs_password: str = "admin@123"
    api_docs_allowed_ips: str = "127.0.0.1,localhost"
    # postgres database details
    postgres_database_name: str = "the-ecommerce-project"
    postgres_database_url: str = (
        f"postgresql://postgres@localhost:5432/{postgres_database_name}"
    )
    # mongo database details
    mongo_database_name: str = "the-ecommerce-project"
    mongo_database_url: str = f"mongodb://localhost:27017/{mongo_database_name}"
    # redis details
    redis_url: str = "redis://localhost:6379/0"

    class Config:
        env_file = ".env"


settings = SettingsConfig()
