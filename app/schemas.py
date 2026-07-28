"""Pydantic models for the Skyhook API."""

from enum import StrEnum

from pydantic import BaseModel, Field

from app.orbits import MAX_ALTITUDE_KM, MIN_ALTITUDE_KM


class MissionStatus(StrEnum):
    PLANNED = "planned"
    ACTIVE = "active"
    COMPLETE = "complete"


class MissionCreate(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    altitude_km: float = Field(ge=MIN_ALTITUDE_KM, le=MAX_ALTITUDE_KM)
    inclination_deg: float = Field(ge=0.0, le=180.0)


class OrbitProfile(BaseModel):
    altitude_km: float
    velocity_km_s: float
    period_minutes: float
    revolutions_per_day: float


class Mission(BaseModel):
    id: int
    name: str
    altitude_km: float
    inclination_deg: float
    status: MissionStatus
    orbit: OrbitProfile
