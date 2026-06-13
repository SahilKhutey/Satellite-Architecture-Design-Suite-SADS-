# SADS - Ground Station Reference
class GroundStation:
    def __init__(self, name: str, lat: float, lon: float, min_elevation_deg: float = 5.0):
        self.name = name
        self.lat = lat
        self.lon = lon
        self.min_elevation_deg = min_elevation_deg
