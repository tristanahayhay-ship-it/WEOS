"""
WEOS Entity Engine
Version 0.1.0
"""

from dataclasses import dataclass


@dataclass
class Entity:
    id: str
    name: str
    entity_type: str
    country: str
    latitude: float
    longitude: float

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "type": self.entity_type,
            "country": self.country,
            "latitude": self.latitude,
            "longitude": self.longitude
        }


if __name__ == "__main__":
    vietnam = Entity(
        id="VN",
        name="Vietnam",
        entity_type="Country",
        country="Vietnam",
        latitude=16.0,
        longitude=108.0
    )

    print(vietnam.to_dict())
