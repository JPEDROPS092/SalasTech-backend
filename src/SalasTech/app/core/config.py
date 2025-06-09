from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
from os import getenv
from typing import Literal, Optional


def _get_from_env(var_name: str, default: Optional[str] = None) -> str:
    value = getenv(var_name, default)
    if value is None:
        raise ValueError(f"Environment variable '{var_name}' must be set.")
    return value

@dataclass(frozen=True)
class Config:
    DB_CONNECTION_STRING: str
    DB_TYPE: Literal['sqlite', 'mysql']
    COOKIES_KEY_NAME: str
    SESSION_TIME: timedelta
    HASH_SALT: str

    @staticmethod
    def get_config() -> Config:
        # Database configuration
        db_type = getenv("DB_TYPE", "sqlite").lower()
        
        if db_type == "sqlite":
            # SQLite configuration
            sqlite_path = getenv("SQLITE_PATH", "db.sqlite")
            db_connection_string = f"sqlite:///{sqlite_path}"
        elif db_type == "mysql":
            # MySQL configuration
            db_host = getenv("DB_HOST", "localhost")
            db_port = getenv("DB_PORT", "3306")
            db_user = getenv("DB_USER", "root")
            db_password = getenv("DB_PASSWORD", "")
            db_name = getenv("DB_NAME", "room_management")
            
            db_connection_string = f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        else:
            # Default to SQLite if invalid type specified
            db_type = "sqlite"
            db_connection_string = "sqlite:///db.sqlite"
            print(f"Warning: Invalid DB_TYPE specified. Defaulting to {db_type}.")
        
        # Override connection string if explicitly provided
        explicit_connection_string = getenv("DB_CONNECTION_STRING", "")
        if explicit_connection_string:
            db_connection_string = explicit_connection_string
            # Determine db_type from connection string if explicitly provided
            if db_connection_string.startswith("sqlite"):
                db_type = "sqlite"
            elif db_connection_string.startswith("mysql"):
                db_type = "mysql"

        # Other configuration
        cookies_key_name = "session_token"
        session_time = timedelta(days=30)
        hash_salt = getenv("HASH_SALT", "SomeRandomStringHere")

        return Config(db_connection_string, db_type, cookies_key_name, session_time, hash_salt)


CONFIG = Config.get_config()
