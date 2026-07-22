"""
WEOS Map Engine
Version: 0.1.0
"""

from dataclasses import dataclass
from typing import Dict


@dataclass
class MapPoint:
    id: str
    name: str
    latitude: float
    longitude: float
    point_type: str

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "point_type": self.point_type,
        }


class MapEngine:

    def __init__(self):
        self.points: Dict[str, MapPoint] = {}

    def add_point(self, point: MapPoint):
        self.points[point.id] = point

    def get_point(self, point_id: str):
        return self.points.get(point_id)

    def get_all_points(self):
        return list(self.points.values())

    def remove_point(self, point_id: str):
        if point_id in self.points:
            del self.points[point_id]

    def total_points(self):
        return len(self.points)


if __name__ == "__main__":

    world_map = MapEngine()

    vietnam = MapPoint(
        id="VN",
        name="Vietnam",
        latitude=16.0,
        longitude=108.0,
        point_type="Country"
    )

    world_map.add_point(vietnam)

    print(world_map.get_point("VN"))
    print("Total:", world_map.total_points())
