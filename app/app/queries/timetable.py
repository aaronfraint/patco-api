def GET_TIMES_FOR_SINGLE_STATION(
    station_name: str,
    tablename: str,
    time: str,
):
    """
    Tablename encapsulates the day of week and direction
    Time can be any current, past, or future time formatted as HH:MM:SS
    """
    return f"""
    with _data as (
        select
            station_{station_name} as value
        from
            {tablename}
        where
            station_{station_name} != 'Does not stop'          
    )
    select
        value as stop_time,
        value::time - '{time}'::time as seconds_away
    from
        _data
    where
        value::time >= '{time}'::time;
"""


def GET_TIMES_FOR_TWO_STATIONS(
    origin_station_name: str,
    destination_station_name: str,
    tablename: str,
    time: str,
    arrive_or_depart: str,
    limit: int,
):
    """
    Tablename encapsulates the day of week and direction
    Time can be any current, past, or future time formatted as HH:MM:SS
    """

    # Build up the proper WHERE clause depending on the directionality requested
    if arrive_or_depart == "arrive":
        where_clause = f"""
            where destination_station::time <= '{time}'::time
            order by destination_station::time desc
            limit {limit}
        """
    elif arrive_or_depart == "depart":
        where_clause = f"""
            where origin_station::time >= '{time}'::time
            order by origin_station::time asc
            limit {limit}
        """

    return f"""
        with _data as (
            select
                station_{origin_station_name} as origin_station,
                station_{destination_station_name} as destination_station
            from
                {tablename}
            where
                station_{origin_station_name} != 'Does not stop'
            and
                station_{destination_station_name} != 'Does not stop'
        )
        select
            origin_station as depart_at,
            destination_station	as arrive_by
        from _data
        {where_clause}
    """
