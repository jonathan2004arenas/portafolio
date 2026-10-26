
import pytest

from werkzeug.security import generate_password_hash

from app import create_app

@pytest.fixture
def client(monkeypatch, tmp_path):
    monkeypatch.setenv("SECRET_KEY", "test-secret-key")
    monkeypatch.setenv(
        "ADMIN_PASSWORD_HASH",
        generate_password_hash("test-admin-password"),
    )

    app = create_app()
    app.config["TESTING"] = True

    # Base de datos temporal exclusiva para las pruebas.
    app.config["DATABASE"] = str(tmp_path / "test_portfolio.db")

    from app.database import init_db
    init_db(app)

    with app.test_client() as test_client:
        yield test_client


def test_home_page(client):
    response = client.get("/")

    assert response.status_code == 200
    assert b"Jonathan Arenas" in response.data


def test_projects_page(client):
    response = client.get("/projects")

    assert response.status_code == 200
    assert b"proyectos" in response.data


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


def test_admin_login_page(client):
    response = client.get("/admin/login")

    assert response.status_code == 200
    assert b"Panel de administracion" in response.data or (
        "Panel de administración".encode("utf-8") in response.data
    )


def test_admin_dashboard_requires_login(client):
    response = client.get("/admin/")

    assert response.status_code == 302
    assert "/admin/login" in response.headers["Location"]


def test_admin_login_with_correct_password(client):
    response = client.get("/admin/login")
    assert response.status_code == 200

    with client.session_transaction() as session:
        token = session["_csrf_token"]

    response = client.post(
        "/admin/login",
        data={
            "password": "test-admin-password",
            "csrf_token": token,
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Proyectos registrados" in response.data


def test_admin_login_with_wrong_password(client):
    response = client.get("/admin/login")

    with client.session_transaction() as session:
        token = session["_csrf_token"]

    response = client.post(
        "/admin/login",
        data={
            "password": "incorrecta",
            "csrf_token": token,
        },
    )

    assert response.status_code == 200
    assert b"La contrase" in response.data



def test_admin_logout(client):
    client.get("/admin/login")

    with client.session_transaction() as session:
        token = session["_csrf_token"]

    client.post(
        "/admin/login",
        data={
            "password": "test-admin-password",
            "csrf_token": token,
        },
    )

    with client.session_transaction() as session:
        token = session["_csrf_token"]

    response = client.post(
        "/admin/logout",
        data={"csrf_token": token},
    )

    assert response.status_code == 302
    assert "/admin/login" in response.headers["Location"]

    response = client.get("/admin/")
    assert response.status_code == 302


def _admin_login(client):
    client.get("/admin/login")

    with client.session_transaction() as session:
        token = session["_csrf_token"]

    return client.post(
        "/admin/login",
        data={
            "password": "test-admin-password",
            "csrf_token": token,
        },
        follow_redirects=True,
    )


def test_admin_can_create_project(client):
    _admin_login(client)

    with client.session_transaction() as session:
        token = session["_csrf_token"]

    response = client.post(
        "/admin/projects/new",
        data={
            "csrf_token": token,
            "title": "Proyecto de prueba CRUD",
            "description": "Proyecto creado durante las pruebas.",
            "technologies": "Python, Flask, SQLite",
            "github": "https://github.com/example/test",
            "demo": "",
            "image": "/static/img/test.png",
            "featured": "on",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert "Proyecto de prueba CRUD".encode() in response.data


def test_admin_can_edit_project(client):
    _admin_login(client)

    with client.session_transaction() as session:
        token = session["_csrf_token"]

    response = client.post(
        "/admin/projects/1/edit",
        data={
            "csrf_token": token,
            "title": "Mi portafolio actualizado",
            "description": "Descripción actualizada desde las pruebas.",
            "technologies": "Python, Flask",
            "github": "",
            "demo": "",
            "image": "",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert "Mi portafolio actualizado".encode() in response.data


def test_admin_cannot_create_project_without_required_fields(client):
    _admin_login(client)

    with client.session_transaction() as session:
        token = session["_csrf_token"]

    response = client.post(
        "/admin/projects/new",
        data={
            "csrf_token": token,
            "title": "",
            "description": "",
        },
    )

    assert response.status_code == 400
    assert "obligatorios".encode() in response.data
