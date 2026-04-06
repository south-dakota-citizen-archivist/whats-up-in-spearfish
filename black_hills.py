"""
black_hills.py

Shared geographic constants for the Black Hills region.
Import these anywhere you need to filter by region, build map bounds,
or annotate data with county/state context.

Usage:
    from black_hills import BBOX, COUNTIES, COUNTY_FIPS
"""

# ---------------------------------------------------------------------------
# Bounding box
# ---------------------------------------------------------------------------
# (min_lon, min_lat, max_lon, max_lat) — WGS84
# Covers the Black Hills uplift and immediate surrounding communities,
# from Hot Springs/Edgemont in the south to Spearfish/Belle Fourche in the
# north, and from Rapid City in the east into the Wyoming foothills.
BBOX = {
    "min_lat": 43.30,
    "max_lat": 44.80,
    "min_lon": -104.70,
    "max_lon": -103.00,
}

# Convenience tuple: (south, west, north, east) — matches Leaflet's fitBounds order
BBOX_LEAFLET = [
    [BBOX["min_lat"], BBOX["min_lon"]],
    [BBOX["max_lat"], BBOX["max_lon"]],
]

# Center point (approximate geographic center of the Hills)
CENTER = {"lat": 44.08, "lon": -103.73}


# ---------------------------------------------------------------------------
# Counties
# ---------------------------------------------------------------------------
# Each entry: name, state abbreviation, 5-digit FIPS code.
# Includes the core Black Hills counties in SD plus the Wyoming foothill
# counties that share the Hills landscape or are commonly grouped with them.
COUNTIES = [
    # South Dakota
    {"name": "Lawrence", "state": "SD", "fips": "46081"},  # Spearfish, Lead, Deadwood
    {"name": "Pennington", "state": "SD", "fips": "46103"},  # Rapid City
    {"name": "Meade", "state": "SD", "fips": "46093"},  # Sturgis, Faith
    {"name": "Custer", "state": "SD", "fips": "46033"},  # Custer, Hot Springs area
    {"name": "Fall River", "state": "SD", "fips": "46047"},  # Hot Springs, Edgemont
    {"name": "Butte", "state": "SD", "fips": "46019"},  # Belle Fourche, NW corner
    # Wyoming
    {"name": "Crook", "state": "WY", "fips": "56011"},  # Sundance, NE WY hills
    {"name": "Weston", "state": "WY", "fips": "56045"},  # Newcastle
]

# Quick lookups
COUNTY_FIPS: dict[str, dict] = {c["fips"]: c for c in COUNTIES}
COUNTY_NAMES_SD: list[str] = [c["name"] for c in COUNTIES if c["state"] == "SD"]
COUNTY_NAMES_WY: list[str] = [c["name"] for c in COUNTIES if c["state"] == "WY"]

# All FIPS as a set — useful for filtering datasets
FIPS_SET: set[str] = {c["fips"] for c in COUNTIES}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def in_bbox(lat: float, lon: float) -> bool:
    """Return True if the coordinate falls within the Black Hills bounding box."""
    return BBOX["min_lat"] <= lat <= BBOX["max_lat"] and BBOX["min_lon"] <= lon <= BBOX["max_lon"]
