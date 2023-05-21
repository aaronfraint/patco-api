import os
import json
import asyncpg
import shapely
import geopandas
from dotenv import find_dotenv, load_dotenv


load_dotenv(find_dotenv())

DATABASE_URL = os.getenv("DATABASE_URL", None)


async def sql_query_raw(query: str, uri: str = DATABASE_URL):
    """
    Connect to postgres via `asyncpg` and return raw result of query
    """
    conn = await asyncpg.connect(uri)

    try:
        result = await conn.fetch(query)

    finally:
        await conn.close()

    return result


def _encode_geometry(geometry):
    """
    Transform `shapely.geometry' into PostGIS type
    """
    if not hasattr(geometry, "__geo_interface__"):
        raise TypeError(
            "{g} does not conform to " "the geo interface".format(g=geometry)
        )

    shape = shapely.geometry.asShape(geometry)
    return shapely.wkb.dumps(shape)


def _decode_geometry(wkb):
    """
    Transform PostGIS type into `shapely.geometry'
    """
    return shapely.wkb.loads(wkb)


async def postgis_query_to_geojson(query: str, columns: list, uri: str = DATABASE_URL):
    """
    Connect to postgres via `asyncpg` and return spatial query output
    as a geojson file
    """
    conn = await asyncpg.connect(uri)

    try:
        await conn.set_type_codec(
            "geometry",
            encoder=_encode_geometry,
            decoder=_decode_geometry,
            format="binary",
        )

        result = await conn.fetch(query)

    finally:
        await conn.close()

    gdf = geopandas.GeoDataFrame.from_records(result, columns=columns)

    return json.loads(gdf.to_json())
