def GET_STATION_GEOMS() -> str:
    columns = ["geometry", "stop_id", "stop_name", "stop_url", "wheelchair_boarding"]
    query = """
        select 
            st_setsrid(st_makepoint(stop_lon, stop_lat), 4326) as geometry,
            stop_id,
            stop_name,
            stop_url,
            wheelchair_boarding 
        from stops
    """

    return query, columns
