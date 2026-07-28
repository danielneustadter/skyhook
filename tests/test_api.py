from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from app.main import app, store

client = TestClient(app)


@pytest.fixture(autouse=True)
def clean_store() -> Iterator[None]:
    store.clear()
    yield
    store.clear()


def make_mission(name: str = "SENTINEL-1", altitude_km: float = 408.0) -> dict:
    resp = client.post(
        "/api/v1/missions",
        json={"name": name, "altitude_km": altitude_km, "inclination_deg": 51.6},
    )
    assert resp.status_code == 201
    return resp.json()


class TestHealth:
    def test_healthz(self) -> None:
        resp = client.get("/healthz")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"

    def test_readyz(self) -> None:
        resp = client.get("/readyz")
        assert resp.status_code == 200

    def test_metrics_counts_requests(self) -> None:
        client.get("/healthz")
        resp = client.get("/metrics")
        assert resp.status_code == 200
        assert 'skyhook_requests_total{route="GET /healthz 200"}' in resp.text


class TestOrbitEndpoint:
    def test_orbit_profile_for_iss_altitude(self) -> None:
        resp = client.get("/api/v1/orbits/408")
        assert resp.status_code == 200
        body = resp.json()
        assert body["period_minutes"] == pytest.approx(92.8, abs=0.5)
        assert body["velocity_km_s"] == pytest.approx(7.66, abs=0.02)

    def test_orbit_profile_rejects_low_altitude(self) -> None:
        resp = client.get("/api/v1/orbits/50")
        assert resp.status_code == 422


class TestMissionCrud:
    def test_create_computes_orbit_profile(self) -> None:
        mission = make_mission()
        assert mission["status"] == "planned"
        assert mission["orbit"]["revolutions_per_day"] == pytest.approx(15.5, abs=0.1)

    def test_create_rejects_bad_altitude(self) -> None:
        resp = client.post(
            "/api/v1/missions",
            json={"name": "BAD", "altitude_km": 10.0, "inclination_deg": 0.0},
        )
        assert resp.status_code == 422

    def test_list_and_get(self) -> None:
        created = make_mission("KESTREL-9", 550.0)
        listed = client.get("/api/v1/missions").json()
        assert len(listed) == 1
        fetched = client.get(f"/api/v1/missions/{created['id']}").json()
        assert fetched["name"] == "KESTREL-9"

    def test_get_missing_returns_404(self) -> None:
        assert client.get("/api/v1/missions/999").status_code == 404

    def test_status_transition(self) -> None:
        created = make_mission()
        resp = client.put(f"/api/v1/missions/{created['id']}/status", params={"status": "active"})
        assert resp.status_code == 200
        assert resp.json()["status"] == "active"

    def test_status_transition_missing_returns_404(self) -> None:
        resp = client.put("/api/v1/missions/999/status", params={"status": "active"})
        assert resp.status_code == 404

    def test_delete(self) -> None:
        created = make_mission()
        assert client.delete(f"/api/v1/missions/{created['id']}").status_code == 204
        assert client.get(f"/api/v1/missions/{created['id']}").status_code == 404

    def test_delete_missing_returns_404(self) -> None:
        assert client.delete("/api/v1/missions/999").status_code == 404
