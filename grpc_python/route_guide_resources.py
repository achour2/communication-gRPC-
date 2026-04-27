import json
import math
from pathlib import Path

import route_guide_pb2


DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "route_guide_db.json"


def read_route_guide_database():
    with DATA_PATH.open("r", encoding="utf-8") as handle:
        data = json.load(handle)

    return [
        route_guide_pb2.Feature(
            name=item["name"],
            location=route_guide_pb2.Point(
                latitude=item["location"]["latitude"],
                longitude=item["location"]["longitude"],
            ),
        )
        for item in data
    ]


def get_feature(db, point):
    for feature in db:
        if (
            feature.location.latitude == point.latitude
            and feature.location.longitude == point.longitude
        ):
            return feature
    return None


def get_distance(start, end):
    coord_factor = 10_000_000.0
    lat_1 = start.latitude / coord_factor
    lat_2 = end.latitude / coord_factor
    lon_1 = start.longitude / coord_factor
    lon_2 = end.longitude / coord_factor

    lat_rad_1, lat_rad_2, lon_rad_1, lon_rad_2 = map(
        math.radians, [lat_1, lat_2, lon_1, lon_2]
    )
    delta_lat = lat_rad_2 - lat_rad_1
    delta_lon = lon_rad_2 - lon_rad_1

    a = (
        math.sin(delta_lat / 2) ** 2
        + math.cos(lat_rad_1) * math.cos(lat_rad_2) * math.sin(delta_lon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return int(6_371_000 * c)
