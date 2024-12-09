import json

import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

try:
    conn = psycopg2.connect(
        host="localhost",
        port="5432",
        user="postgres",
        password="notingres",
        dbname="postgres",  # Connect to the default 'postgres' database to perform operations
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)  # Enable autocommit mode
    pg_db = "fluffy_pg"
    cursor = conn.cursor()

    # Check if database exists
    cursor.execute(sql.SQL("SELECT 1 FROM pg_database WHERE datname = %s"), [pg_db])
    database_exists = cursor.fetchone()

    # If the database does not exist, create it
    if not database_exists:
        cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(pg_db)))
        print(f"Database '{pg_db}' created.")
    else:
        print(f"Database '{pg_db}' already exists.")
except Exception as e:
    print(f"An error occurred: {e}")

finally:
    # Close the cursor and connection
    if "cursor" in locals():
        cursor.close()
    if "conn" in locals():
        conn.close()
