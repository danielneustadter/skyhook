"""Skyhook — satellite mission-tasking API.

A small FastAPI service used to demonstrate a complete DevSecOps
pipeline. See README.md for the pipeline architecture.
"""

import threading
from collections import Counter
from collections.abc import Awaitable, Callable

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import PlainTextResponse

from app.orbits import (
    orbital_period_minutes,
    orbital_velocity_km_s,
    revolutions_per_day,
    validate_altitude,
)
from app.schemas import Mission, MissionCreate, MissionStatus, OrbitProfile
from app.store import MissionStore

APP_VERSION = "1.0.0"

app = FastAPI(
    title="Skyhook",
    version=APP_VERSION,
    description="Satellite mission-tasking API (DevSecOps pipeline demo).",
)

store = MissionStore()

_metrics_lock = threading.Lock()
_request_counts: Counter[str] = Counter()


@app.middleware("http")
async def count_requests(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    response = await call_next(request)
    key = f"{request.method} {request.url.path} {response.status_code}"
    with _metrics_lock:
        _request_counts[key] += 1
    return response


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok", "version": APP_VERSION}


@app.get("/readyz")
def readyz() -> dict[str, str]:
    return {"status": "ready"}


@app.get("/metrics", response_class=PlainTextResponse)
def metrics() -> str:
    with _metrics_lock:
        lines = [
            f'skyhook_requests_total{{route="{key}"}} {count}'
            for key, count in sorted(_request_counts.items())
        ]
    return "\n".join(lines) + "\n"


@app.get("/api/v1/orbits/{altitude_km}")
def orbit_profile(altitude_km: float) -> OrbitProfile:
    try:
        validate_altitude(altitude_km)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return OrbitProfile(
        altitude_km=altitude_km,
        velocity_km_s=orbital_velocity_km_s(altitude_km),
        period_minutes=orbital_period_minutes(altitude_km),
        revolutions_per_day=revolutions_per_day(altitude_km),
    )


@app.post("/api/v1/missions", status_code=201)
def create_mission(payload: MissionCreate) -> Mission:
    return store.create(payload)


@app.get("/api/v1/missions")
def list_missions() -> list[Mission]:
    return store.list_all()


@app.get("/api/v1/missions/{mission_id}")
def get_mission(mission_id: int) -> Mission:
    mission = store.get(mission_id)
    if mission is None:
        raise HTTPException(status_code=404, detail="mission not found")
    return mission


@app.put("/api/v1/missions/{mission_id}/status")
def set_mission_status(mission_id: int, status: MissionStatus) -> Mission:
    mission = store.set_status(mission_id, status)
    if mission is None:
        raise HTTPException(status_code=404, detail="mission not found")
    return mission


@app.delete("/api/v1/missions/{mission_id}", status_code=204)
def delete_mission(mission_id: int) -> None:
    if not store.delete(mission_id):
        raise HTTPException(status_code=404, detail="mission not found")
