# backend/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "sqlite:///./dev.db"
    chroma_persist_dir: str = "./chroma_db"
    groq_api_key: str = ""
    clerk_secret_key: str = ""
    clerk_publishable_key: str = ""
    r2_account_id: str = ""
    r2_access_key_id: str = ""
    r2_secret_access_key: str = ""
    r2_bucket_name: str = "molly-docs"
    youtube_api_key: str = ""
    facebook_page_id: str = "colegiogemelli"
    instagram_username: str = "colegiogemelli"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
