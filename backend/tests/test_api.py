import pytest

def test_list_datasets_seeds_sample(client):
    response = client.get("/api/v1/datasets")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    sample = data[0]
    assert "id" in sample
    assert "name" in sample
    assert "row_count" in sample

def test_dataset_preview(client):
    # First get list
    res_list = client.get("/api/v1/datasets")
    dataset_id = res_list.json()[0]["id"]

    res_preview = client.get(f"/api/v1/datasets/{dataset_id}/preview?limit=10")
    assert res_preview.status_code == 200
    p_data = res_preview.json()
    assert "columns" in p_data
    assert "rows" in p_data
    assert len(p_data["rows"]) <= 10

def test_dataset_validate_endpoint(client):
    res_list = client.get("/api/v1/datasets")
    dataset_id = res_list.json()[0]["id"]

    res_val = client.post(f"/api/v1/datasets/{dataset_id}/validate")
    assert res_val.status_code == 200
    val_data = res_val.json()
    assert "is_valid" in val_data
    assert val_data["is_valid"] is True

def test_dataset_not_found(client):
    res = client.get("/api/v1/datasets/non-existent-id")
    assert res.status_code == 404

def test_dashboard_summary(client):
    res = client.get("/api/v1/dashboard/summary")
    assert res.status_code == 200
    d = res.json()
    assert "total_datasets" in d
    assert "total_products" in d
    assert "latest_forecast" in d
    assert "latest_inventory" in d

