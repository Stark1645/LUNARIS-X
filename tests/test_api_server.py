"""
Unit Tests for FastAPI REST Endpoints.
"""

import cv2
import io
import numpy as np
import pytest
from fastapi.testclient import TestClient
from src.api.app import app


@pytest.fixture
def client():
    return TestClient(app)


def test_health_endpoint(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "UP"
    assert "SIFT_Baseline" in data["supported_algorithms"]
    assert "RIFT_Baseline" in data["supported_algorithms"]
    assert "HOMOGRAPHY" in data["supported_models"]


def test_register_endpoint(client):
    # Create mock test PNG images
    img1 = np.ones((128, 128), dtype=np.uint8) * 150
    img2 = np.ones((128, 128), dtype=np.uint8) * 150
    # Draw simple distinct patterns
    cv2.circle(img1, (64, 64), 20, 50, -1)
    cv2.circle(img2, (64, 64), 20, 50, -1)

    _, buf1 = cv2.imencode(".png", img1)
    _, buf2 = cv2.imencode(".png", img2)

    files = {
        "source_file": ("source.png", buf1.tobytes(), "image/png"),
        "reference_file": ("reference.png", buf2.tobytes(), "image/png")
    }
    data = {
        "algorithm": "SIFT_Baseline",
        "transformation_model": "HOMOGRAPHY"
    }

    response = client.post("/api/v1/register", files=files, data=data)
    assert response.status_code == 200
    res_json = response.json()
    assert res_json["algorithm"] == "SIFT_Baseline"
    assert "status" in res_json
    assert "warped_source_base64" in res_json
