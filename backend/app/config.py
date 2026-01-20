from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    database_url: str = "postgresql://wunderlists_user:password@localhost:5432/wunderlists_db"
    openweather_api_key: str = ""
    debug: bool = True
    host: str = "0.0.0.0"
    port: int = 8000

    # Google Calendar OAuth credentials
    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_uri: str = "http://localhost:8000/api/calendar-sync/oauth-callback"
    google_calendar_credentials: str = ""  # JSON string of stored credentials

    class Config:
        env_file = ".env"
        case_sensitive = False

@lru_cache()
def get_settings():
    return Settings()
