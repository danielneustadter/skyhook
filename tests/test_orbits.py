import math

import pytest

from app import orbits


class TestOrbitalMath:
    def test_iss_period_is_about_93_minutes(self) -> None:
        assert orbits.orbital_period_minutes(408.0) == pytest.approx(92.8, abs=0.5)

    def test_iss_velocity_is_about_7_66_km_s(self) -> None:
        assert orbits.orbital_velocity_km_s(408.0) == pytest.approx(7.66, abs=0.02)

    def test_geo_period_is_about_one_day(self) -> None:
        # Geostationary altitude: period should be ~1436 min (sidereal day)
        assert orbits.orbital_period_minutes(35786.0) == pytest.approx(1436.0, abs=2.0)

    def test_revolutions_per_day_iss(self) -> None:
        assert orbits.revolutions_per_day(408.0) == pytest.approx(15.5, abs=0.1)

    def test_higher_orbit_is_slower(self) -> None:
        assert orbits.orbital_velocity_km_s(2000.0) < orbits.orbital_velocity_km_s(400.0)

    def test_radius_includes_earth_radius(self) -> None:
        assert orbits.orbital_radius_km(500.0) == pytest.approx(orbits.EARTH_RADIUS_KM + 500.0)


class TestValidation:
    @pytest.mark.parametrize("altitude", [159.9, -100.0, 40001.0])
    def test_out_of_bounds_altitude_rejected(self, altitude: float) -> None:
        with pytest.raises(ValueError, match="altitude must be between"):
            orbits.validate_altitude(altitude)

    @pytest.mark.parametrize("altitude", [math.nan, math.inf, -math.inf])
    def test_non_finite_altitude_rejected(self, altitude: float) -> None:
        with pytest.raises(ValueError, match="finite"):
            orbits.validate_altitude(altitude)

    @pytest.mark.parametrize("altitude", [160.0, 408.0, 35786.0, 40000.0])
    def test_valid_altitudes_accepted(self, altitude: float) -> None:
        orbits.validate_altitude(altitude)
