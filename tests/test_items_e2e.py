import time
from datetime import datetime
import os
import pytest
import httpx

BASE_URL = os.getenv("BASE_URL", "http://api:8000")
RETRIES = 3
DELAY = 5 # seconds
STATUS_ACCEPTED = 202
STATUS_OK = 200
STATUS_NOT_FOUND = 404

@pytest.fixture
def client():
    return httpx.Client(base_url=BASE_URL)

def create_item(client, name: str, description: str) -> None:
    payload = {"name": name, "description": description}
    response = client.post("/items/", json=payload)
    assert response.status_code == STATUS_ACCEPTED

def create_and_verify_item(client, name: str, description = "A test item") -> int:
    create_item(client, name, description)

    for attempt in range(RETRIES):
        response = client.get("/items/")
        assert response.status_code == STATUS_OK

        items = response.json()
        for item in items:
            if item["name"] == name:
                return item["id"]

        print(f"Retry {attempt + 1}/{RETRIES}: Item not found yet. Retrying in {DELAY} seconds.")
        time.sleep(DELAY)

    raise AssertionError(f"Item with name '{name}' was not found after {RETRIES} retries.")

# Tests

def test_creation_and_verify_item(client):
    unique_name = f"Test Create Item {datetime.now().isoformat()}"
    create_and_verify_item(client, unique_name)

def test_read_item_by_id(client):
    unique_name = f"Test Read Item by ID {datetime.now().isoformat()}"

    item_id = create_and_verify_item(client, unique_name)

    response = client.get(f"/items/{item_id}")
    assert response.status_code == STATUS_OK
    
    item = response.json()
    assert item["id"] == item_id, f"Expected item ID {item_id}, but got {item['id']}"
    assert item["name"] == unique_name, f"Expected name '{unique_name}', but got '{item['name']}'"

def test_read_items(client):
    response = client.get("/items/")
    assert response.status_code == STATUS_OK
    assert isinstance(response.json(), list)

def test_read_nonexistent_item(client):
    response = client.get("/items/999")
    assert response.status_code == STATUS_NOT_FOUND

def test_delete_item(client):
    unique_name = f"Test Delete Item by ID {datetime.now().isoformat()}"

    item_id = create_and_verify_item(client, unique_name)

    delete_response = client.delete(f"/items/{item_id}")
    assert delete_response.status_code == STATUS_OK

    fetch_response = client.get(f"/items/{item_id}")
    assert fetch_response.status_code == STATUS_NOT_FOUND

def test_delete_nonexistent_item(client):
    response = client.delete("/items/999")
    assert response.status_code == STATUS_NOT_FOUND

def test_update_existing_item(client):
    unique_name = f"Test Update Item {datetime.now().isoformat()}"
    item_id = create_and_verify_item(client, unique_name)

    updated_name = f"Updated {unique_name}"
    payload = {"name": updated_name, "description": "Updated description"}

    update_response = client.put(f"/items/{item_id}", json=payload)
    assert update_response.status_code == STATUS_ACCEPTED

    for attempt in range(RETRIES):
        response = client.get(f"/items/{item_id}")
        assert response.status_code == STATUS_OK

        item = response.json()
        
        if item["name"] == updated_name:
            assert item["description"] == "Updated description"
            return

        print(f"Retry {attempt + 1}/{RETRIES}: Update not reflected yet. Retrying in {DELAY} seconds.")
        time.sleep(DELAY)

    raise AssertionError(f"Item update was not reflected after {RETRIES} retries.")