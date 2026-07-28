"""Orbital mechanics helpers for satellite pass planning.

Pure functions over circular-orbit approximations. Good enough for
mission scheduling estimates; not for actual flight dynamics.
"""

import math

EARTH_RADIUS_KM = 6371.0
EARTH_MU_KM3_S2 = 398600.4418  # standard gravitational parameter GM
MINUTES_PER_DAY = 1440.0

# Sanity bounds for a circular Earth orbit we are willing to schedule.
MIN_ALTITUDE_KM = 160.0  # below this, drag deorbits you in days
MAX_ALTITUDE_KM = 40000.0  # just past GEO


def validate_altitude(altitude_km: float) -> None:
    """Raise ValueError if the altitude is outside schedulable bounds."""
    if not math.isfinite(altitude_km):
        raise ValueError("altitude must be a finite number")
    if altitude_km < MIN_ALTITUDE_KM or altitude_km > MAX_ALTITUDE_KM:
        raise ValueError(f"altitude must be between {MIN_ALTITUDE_KM} and {MAX_ALTITUDE_KM} km")


def orbital_radius_km(altitude_km: float) -> float:
    """Distance from Earth's center for a given altitude above the surface."""
    validate_altitude(altitude_km)
    return EARTH_RADIUS_KM + altitude_km


def orbital_velocity_km_s(altitude_km: float) -> float:
    """Circular orbital velocity at a given altitude."""
    radius = orbital_radius_km(altitude_km)
    return math.sqrt(EARTH_MU_KM3_S2 / radius)


def orbital_period_minutes(altitude_km: float) -> float:
    """Time for one full revolution at a given altitude."""
    radius = orbital_radius_km(altitude_km)
    period_seconds = 2.0 * math.pi * math.sqrt(radius**3 / EARTH_MU_KM3_S2)
    return period_seconds / 60.0


def revolutions_per_day(altitude_km: float) -> float:
    """How many complete orbits fit in a 24-hour day."""
    return MINUTES_PER_DAY / orbital_period_minutes(altitude_km)
