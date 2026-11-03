"""
Database Connection & Engine Manager.
Provides seamless connection to SQLite or PostgreSQL based on configuration.
"""
import os
import sys
import yaml
from pathlib import Path
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker

BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from config.logging_config import setup_logger

logger = setup_logger("db_connection")

def load_config() -> dict:
    cfg_path = BASE_DIR / "config" / "config.yaml"
    with open(cfg_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def get_database_engine() -> Engine:
    config = load_config()
    db_engine_type = os.getenv("DB_ENGINE", config.get("database", {}).get("engine", "sqlite")).lower()

    if db_engine_type == "postgresql":
        pg_cfg = config.get("database", {}).get("postgresql", {})
        host = os.getenv("POSTGRES_HOST", pg_cfg.get("host", "localhost"))
        port = os.getenv("POSTGRES_PORT", pg_cfg.get("port", 5432))
        db = os.getenv("POSTGRES_DB", pg_cfg.get("database", "healthcare_analytics"))
        user = os.getenv("POSTGRES_USER", pg_cfg.get("user", "postgres"))
        pwd = os.getenv("POSTGRES_PASSWORD", pg_cfg.get("password", "postgres"))
        
        uri = f"postgresql+psycopg2://{user}:{pwd}@{host}:{port}/{db}"
        logger.info(f"Connecting to PostgreSQL database at {host}:{port}/{db}")
        return create_engine(uri)
    else:
        sqlite_rel = config.get("database", {}).get("sqlite_path", "data/healthcare_mart.db")
        sqlite_path = BASE_DIR / sqlite_rel
        sqlite_path.parent.mkdir(parents=True, exist_ok=True)
        uri = f"sqlite:///{sqlite_path.as_posix()}"
        logger.info(f"Connecting to SQLite data mart at {sqlite_path}")
        return create_engine(uri)

def init_database(engine: Engine = None) -> None:
    """Initializes the database schema using DDL in schema.sql."""
    if engine is None:
        engine = get_database_engine()
        
    schema_path = BASE_DIR / "src" / "database" / "schema.sql"
    with open(schema_path, "r", encoding="utf-8") as f:
        ddl = f.read()

    # For SQLite, clean up AUTOINCREMENT compatibility if needed
    is_sqlite = "sqlite" in str(engine.url)
    statements = [s.strip() for s in ddl.split(";") if s.strip()]
    
    with engine.begin() as conn:
        for stmt in statements:
            if is_sqlite and "AUTOINCREMENT" not in stmt and "SERIAL" in stmt:
                stmt = stmt.replace("SERIAL PRIMARY KEY", "INTEGER PRIMARY KEY AUTOINCREMENT")
            elif not is_sqlite and "AUTOINCREMENT" in stmt:
                stmt = stmt.replace("INTEGER PRIMARY KEY AUTOINCREMENT", "SERIAL PRIMARY KEY")
            conn.exec_driver_sql(stmt)
            
    logger.info("Database schema initialized successfully.")

if __name__ == "__main__":
    eng = get_database_engine()
    init_database(eng)
