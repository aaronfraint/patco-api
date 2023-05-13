from enum import Enum


class Direction(str, Enum):
    eb = "eb"
    wb = "wb"


class Station(str, Enum):
    x15_16th_and_locust = "15_16th_and_locust"
    x12_13th_and_locust = "12_13th_and_locust"
    x9_10th_and_locust = "9_10th_and_locust"
    x8th_and_market = "8th_and_market"
    city_hall = "city_hall"
    broadway = "broadway"
    ferry_ave = "ferry_ave"
    collingswood = "collingswood"
    westmont = "westmont"
    haddonfield = "haddonfield"
    woodcrest = "woodcrest"
    ashland = "ashland"
    lindenwold = "lindenwold"


class RouteEndpoint(str, Enum):
    arrive = "arrive"
    depart = "depart"


STATIONS_EB = [
    "15_16th_and_locust",
    "12_13th_and_locust",
    "9_10th_and_locust",
    "8th_and_market",
    "city_hall",
    "broadway",
    "ferry_ave",
    "collingswood",
    "westmont",
    "haddonfield",
    "woodcrest",
    "ashland",
    "lindenwold",
]
