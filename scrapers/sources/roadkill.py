"""
scrapers/sources/roadkill.py

Fetches recent wildlife carcass pickup records from the SD DOT ArcGIS
FeatureServer, filtered to the Black Hills bounding box.

Source: SD DOT / Survey123 "DOT Wildlife Carcass Pickup" layer
API: https://services1.arcgis.com/PwrabBhZHUggYYSp/ArcGIS/rest/services/
     service_45cc7abd52f846ce8ad10dba811a5535/FeatureServer/0

Usage:
    uv run python -c "
    from scrapers.sources.roadkill import fetch_roadkill
    fetch_roadkill()
    "
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests

from black_hills import BBOX

DATA_FILE = Path(__file__).resolve().parent.parent.parent / "data" / "roadkill.json"

BASE_URL = (
    "https://services1.arcgis.com/PwrabBhZHUggYYSp/ArcGIS/rest/services"
    "/service_45cc7abd52f846ce8ad10dba811a5535/FeatureServer/0/query"
)

HEADERS = {"User-Agent": "whats-up-in-spearfish/1.0 (public data aggregator)"}

# How far back to fetch
LOOKBACK_DAYS = 30

# ArcGIS envelope geometry (WGS84) from black_hills BBOX
BH_ENVELOPE = (
    f'{{"xmin":{BBOX["min_lon"]},"ymin":{BBOX["min_lat"]},'
    f'"xmax":{BBOX["max_lon"]},"ymax":{BBOX["max_lat"]},'
    f'"spatialReference":{{"wkid":4326}}}}'
)


def _ts_to_iso(ms: int | None) -> str:
    """Convert ArcGIS epoch-milliseconds timestamp to ISO date string."""
    if not ms:
        return ""
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).strftime("%Y-%m-%d")


def fetch_roadkill() -> None:
    cutoff = datetime.now(tz=timezone.utc) - timedelta(days=LOOKBACK_DAYS)
    cutoff_str = cutoff.strftime("%Y-%m-%d %H:%M:%S")

    params = {
        "where": f"Date > TIMESTAMP '{cutoff_str}'",
        "geometry": BH_ENVELOPE,
        "geometryType": "esriGeometryEnvelope",
        "spatialRel": "esriSpatialRelIntersects",
        "outFields": "Date,Species,Highway,Sex,Present,Comments,Contractor",
        "orderByFields": "Date DESC",
        "resultRecordCount": 1000,
        "f": "json",
    }

    try:
        resp = requests.get(BASE_URL, params=params, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        data = resp.json()
    except Exception as exc:
        print(f"[Roadkill] Warning: fetch failed: {exc}")
        return

    if "error" in data:
        print(f"[Roadkill] API error: {data['error']}")
        return

    records = []
    for feature in data.get("features") or []:
        attrs = feature.get("attributes") or {}
        geom = feature.get("geometry") or {}

        species = (attrs.get("Species") or "").strip()
        if not species:
            continue

        lat = geom.get("y") or attrs.get("Latitude")
        lon = geom.get("x") or attrs.get("Longitude")

        # Skip records with no usable coordinates
        if not lat or not lon:
            continue

        highway = (attrs.get("Highway") or "").strip()
        if highway.upper() in ("N/A", "NA", "NONE", ""):
            highway = ""

        records.append(
            {
                "date": _ts_to_iso(attrs.get("Date")),
                "species": species,
                "highway": highway,
                "sex": (attrs.get("Sex") or "").strip(),
                "present": attrs.get("Present"),
                "comments": (attrs.get("Comments") or "").strip() or None,
                "contractor": (attrs.get("Contractor") or "").strip() or None,
                "lat": round(lat, 6),
                "lon": round(lon, 6),
            }
        )

    DATA_FILE.write_text(
        json.dumps(
            {
                "fetched_at": datetime.now(timezone.utc).isoformat(),
                "lookback_days": LOOKBACK_DAYS,
                "records": records,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"[Roadkill] {len(records)} records (last {LOOKBACK_DAYS} days, BH bbox) → {DATA_FILE.name}")


if __name__ == "__main__":
    fetch_roadkill()
