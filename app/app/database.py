import asyncpg
import os
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

DATABASE_URL = os.getenv("DATABASE_URL", None)

async def sql_query_raw(query: str, uri: str = DATABASE_URL):
    """
    Connect to postgres via `asyncpg` and return raw result of query
    """
    conn = await asyncpg.connect(uri)

    try:
        print("trying...")
        result = await conn.fetch(query)

    finally:
        await conn.close()

    return result
