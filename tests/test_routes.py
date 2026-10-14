
# tests/test_routes.py

import pytest

from app import create_app


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True

    with app.test_client() as test_client:
        yield test_client


def test_home_page(client):
    response = client.get("/")

    assert response.status_code == 200
    assert b"Hola, soy Arenas" in response.data


def test_projects_page(client):
    response = client.get("/projects")

    assert response.status_code == 200
    assert b"Mis proyectos" in response.data


def test_project_detail(client):
    response = client.get("/projects/1")

    assert response.status_code == 200
    assert b"Mi portafolio" in response.data


def test_missing_project_returns_404(client):
    response = client.get("/projects/999")

    assert response.status_code == 404


def test_projects_api_returns_json(client):
    response = client.get("/api/projects")

    assert response.status_code == 200

    data = response.get_json()

    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]["title"] == "Mi portafolio"
