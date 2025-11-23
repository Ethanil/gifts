import config
from dotenv import load_dotenv
from os import getenv
from sqlalchemy import inspect, text
from sqlalchemy.exc import OperationalError
from models import *  # Ensure all models are imported

load_dotenv()
app = config.connex_app
app.add_api(config.basedir / "openapi.yaml", name="api_v1", options={"swagger_ui": True})

def ensure_database_schema():
    """
    Checks for missing tables or columns and updates the DB schema.
    This logic is separated so it can be called when running directly.
    """
    with app.app.app_context():
        inspector = inspect(config.db.engine)
        # Loop through models
        for table_class in config.db.Model.__subclasses__():
            table_name = table_class.__tablename__
            if not inspector.has_table(table_name):  # Ensure table exists
                continue

            # Get existing columns in the DB
            existing_columns = {col["name"] for col in inspector.get_columns(table_name)}

            # Check for missing columns
            for column in table_class.__table__.columns:
                if column.name not in existing_columns:
                    alter_statement = f"ALTER TABLE {table_name} ADD COLUMN {column.name} {str(column.type)}"
                    if column.default is not None:
                        default_value = column.default.arg if callable(column.default.arg) else column.default.arg
                        alter_statement += f" DEFAULT {repr(default_value)}"
                    if not column.nullable:
                        alter_statement += " NOT NULL"
                    try:
                        with config.db.engine.connect() as connection:
                            connection.execute(text(alter_statement))
                        print(f"Added missing column: {column.name} to {table_name}")
                    except OperationalError:
                        print(f"Could not add column: {column.name} (possible type conflict)")

        # Now create any missing tables
        config.db.create_all()

if __name__ == "__main__":
    # If running with 'python main.py', we run migrations and start the built-in server
    ensure_database_schema()
    app.run(host=getenv('BACKEND_HOST', '0.0.0.0'), port=int(getenv('BACKEND_PORT', 5000)))