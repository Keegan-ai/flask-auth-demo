#===========================================================
# Database Related Functions
#===========================================================

from libsql_client import create_client_sync, LibsqlError
from contextlib import contextmanager
from dotenv import load_dotenv
from functools import wraps
from os import getenv, path
from app.helpers.errors import server_error


# Load Turso environment variables from the .env file
load_dotenv()
TURSO_URL = getenv("TURSO_URL")
TURSO_KEY = getenv("TURSO_KEY")

# Define the locations of our DB files
DB_FOLDER   = path.join(path.dirname(__file__), "db")
SCHEMA_FILE = path.join(DB_FOLDER, "schema.sql")


#-----------------------------------------------------------
# Connect to the Turso DB and return the connection
#-----------------------------------------------------------
@contextmanager
def connect_db():
    client = None

    try:
        # Attempt to connect Turso DB, and pass back the connection
        client = create_client_sync(url=TURSO_URL, auth_token=TURSO_KEY)
        yield client

    finally:
        # Properly close the connection when done
        if client is not None:
            client.close()


#-----------------------------------------------------------
# A decorator function to handle errors connecting to the DB
#-----------------------------------------------------------
def handle_db_errors(func):
    @wraps(func)
    # Wrap the given function...
    def wrapper(*args, **kwargs):
        try:
            # Attempt to run the given function
            return func(*args, **kwargs)

        except LibsqlError as e:
            # Caught a DB related error
            print(f"Database error: {e}")
            return server_error("A database error occurred")

        except Exception as e:
            # Caught a general error
            print(f"Unexpected error: {e}")
            return server_error("An unexpected server error occurred")

    return wrapper


