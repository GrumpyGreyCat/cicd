import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    db_path: Path = Path(os.environ.get("SOUNDPINS_DB_PATH", "data/mock_db.json"))


settings = Settings()
