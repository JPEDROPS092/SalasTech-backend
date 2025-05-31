
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import Engine

from app.models.db import Base
from app.core.config import CONFIG

# Configure engine based on database type
engine_kwargs = {
    "echo": False,
    "pool_pre_ping": True,
}

# Add MySQL-specific configurations
if CONFIG.DB_TYPE == "mysql":
    engine_kwargs["pool_recycle"] = 3600  # Reconnect after 1 hour

# Create the engine with appropriate configurations
engine = create_engine(CONFIG.DB_CONNECTION_STRING, **engine_kwargs)

# Enable foreign key support for SQLite
if CONFIG.DB_TYPE == "sqlite":
    @event.listens_for(Engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

session_maker = sessionmaker(bind=engine, expire_on_commit=False)

def create_tables() -> None:
    """
    Creates the database tables by calling `Base.metadata.create_all(engine)`.
    """
    Base.metadata.create_all(engine)

def drop_tables() -> None:
    """
    Drops all database tables by calling `Base.metadata.drop_all(engine)`.
    """
    Base.metadata.drop_all(engine)

def recreate_tables() -> None:
    """
    Recreates all database tables by dropping them first and then creating them again.
    """
    drop_tables()
    create_tables()

def auto_create_db():
    """
    Automatically creates the database if it doesn't already exist.
    """
    try:
        con = engine.connect()
        create_tables()
        con.close()

    except Exception as e:
        if CONFIG.DB_TYPE == "mysql":
            # For MySQL, create the database if it doesn't exist
            try:
                connection_string, db_name = CONFIG.DB_CONNECTION_STRING.rsplit("/", 1)
                tmp_engine = create_engine(connection_string)
                with tmp_engine.begin() as session:
                    session.exec_driver_sql(f"CREATE DATABASE `{db_name}`")
                create_tables()
            except Exception as mysql_error:
                print(f"Error creating MySQL database: {mysql_error}")
                raise
        elif CONFIG.DB_TYPE == "sqlite":
            # For SQLite, the database file will be created automatically
            # when we call create_tables()
            create_tables()
        else:
            # For other database types, re-raise the exception
            print(f"Error connecting to database: {e}")
            raise
