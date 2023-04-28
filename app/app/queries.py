from .database import sql_query_raw


async def get_name_of_stop(stop_id: int) -> list[dict]:
    """
    Get attributes of a single stop, from its ID
    """

    query = f"""
        SELECT
            stop_name,
            stop_id,
            stop_url,
            wheelchair_boarding,
            stop_lon,
            stop_lat
        FROM stops
        WHERE stop_id = {stop_id}
    """
    return await sql_query_raw(query)
