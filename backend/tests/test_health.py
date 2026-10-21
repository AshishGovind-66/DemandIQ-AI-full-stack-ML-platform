import pytest

def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert "available_models" in data
    assert "naive" in data["available_models"]
    assert "xgboost" in data["available_models"]
    assert "walmart_m5_available" in data

