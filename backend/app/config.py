"""
Application Configuration
Handles environment variables and settings
"""
import os
import yaml
from typing import List
from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    # Project Info
    PROJECT_NAME: str = "Bookkeeping API"
    VERSION: str = "1.0.0"
    
    # API Settings
    API_V1_PREFIX: str = "/api/v1"
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
    ]
    
    # Paths
    BASE_DIR: Path = Path(__file__).parent.parent.parent.parent
    DATA_BASE_DIR: str = "./data"
    USER_DATA_DIR: str = "./data/user"
    CONFIG_FILE: str = "./config/config.yaml"
    
    # Google Drive
    DRIVE_FOLDER_ID: str = ""
    GOOGLE_CREDENTIALS_FILE: str = "credentials.json"
    GOOGLE_TOKEN_FILE: str = "token.json"
    GOOGLE_SCOPES: List[str] = ["https://www.googleapis.com/auth/drive.file"]
    
    # Database
    DATABASE_URL: str = "sqlite:///./data/bookkeeping.db"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-this"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Default Categories
    DEFAULT_CATEGORIES: List[str] = [
        "Food",
        "Salary",
        "Transport",
        "Entertainment",
        "Others"
    ]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


def load_yaml_config(config_path: str = None) -> dict:
    """Load configuration from YAML file"""
    if config_path is None:
        config_path = Settings().CONFIG_FILE
    
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    return {}


# Global settings instance
settings = Settings()

# Load and merge YAML config if exists
yaml_config = load_yaml_config()
if yaml_config:
    if 'google_drive' in yaml_config:
        settings.DRIVE_FOLDER_ID = yaml_config['google_drive'].get('folder_id', '')
        settings.GOOGLE_SCOPES = yaml_config['google_drive'].get('scopes', settings.GOOGLE_SCOPES)
    
    if 'defaults' in yaml_config and 'categories' in yaml_config['defaults']:
        settings.DEFAULT_CATEGORIES = yaml_config['defaults']['categories']
    
    if 'paths' in yaml_config:
        paths = yaml_config['paths']
        settings.DATA_BASE_DIR = paths.get('data_base_dir', settings.DATA_BASE_DIR)
        settings.USER_DATA_DIR = paths.get('user_data_dir', settings.USER_DATA_DIR)