import asyncpg


async def sql_query_raw(query: str, uri: str):
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
