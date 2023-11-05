import sys
import yaml
from pathlib import Path

key_dir = str(Path(__file__).parent.parent.parent / "keys")
sys.path.append(key_dir)

from alpha_key import api_key
api_key = api_key

with open(key_dir / "postgres_keys.yaml", 'r') as f:
            credentials = yaml.safe_load(f)

class Settings:
    PROJECT_NAME: str = "My first connection"
    PROJECT_VERSION: str = "0.0.1"

    POSTGRES_USER: str = credentials["user"]
    POSTGRES_PASSWORD = credentials["password"]
    POSTGRES_HOST: str = credentials["host"]
    POSTGRES_PORT: str = credentials["port"]
    POSTGRES_DATABASE: str = credentials["database"]