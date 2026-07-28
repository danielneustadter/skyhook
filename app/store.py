"""In-memory mission store.

Deliberately simple: the point of this repo is the pipeline around the
service, not the persistence layer. Swap for a real database behind the
same interface if this ever grows up.
"""

import threading

from app.orbits import (
    orbital_period_minutes,
    orbital_velocity_km_s,
    revolutions_per_day,
)
from app.schemas import Mission, MissionCreate, MissionStatus, OrbitProfile


class MissionStore:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._missions: dict[int, Mission] = {}
        self._next_id = 1

    def create(self, payload: MissionCreate) -> Mission:
        orbit = OrbitProfile(
            altitude_km=payload.altitude_km,
            velocity_km_s=orbital_velocity_km_s(payload.altitude_km),
            period_minutes=orbital_period_minutes(payload.altitude_km),
            revolutions_per_day=revolutions_per_day(payload.altitude_km),
        )
        with self._lock:
            mission = Mission(
                id=self._next_id,
                name=payload.name,
                altitude_km=payload.altitude_km,
                inclination_deg=payload.inclination_deg,
                status=MissionStatus.PLANNED,
                orbit=orbit,
            )
            self._missions[mission.id] = mission
            self._next_id += 1
        return mission

    def list_all(self) -> list[Mission]:
        with self._lock:
            return list(self._missions.values())

    def get(self, mission_id: int) -> Mission | None:
        with self._lock:
            return self._missions.get(mission_id)

    def set_status(self, mission_id: int, status: MissionStatus) -> Mission | None:
        with self._lock:
            mission = self._missions.get(mission_id)
            if mission is None:
                return None
            updated = mission.model_copy(update={"status": status})
            self._missions[mission_id] = updated
            return updated

    def delete(self, mission_id: int) -> bool:
        with self._lock:
            return self._missions.pop(mission_id, None) is not None

    def clear(self) -> None:
        with self._lock:
            self._missions.clear()
            self._next_id = 1
