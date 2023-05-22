from typing import Tuple
from dataclasses import dataclass


@dataclass
class GeomQuery:
    query: str
    columns: list


def GET_STATION_GEOMS() -> GeomQuery:
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

    return GeomQuery(query, columns)


def GET_ROUTE_GEOM() -> GeomQuery:
    query = """
        select
            shape_id,
           st_makeline(st_makepoint(shape_pt_lon, shape_pt_lat)) as geometry
        from
            shapes
        where
            shape_id = 1
        group by
            shape_id
    """
    return GeomQuery(query, ["shape_id", "geometry"])
