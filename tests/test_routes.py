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


def test_admin_can_delete_project(client):
    _admin_login(client)

    # Obtener el token CSRF de la sesión autenticada.
    with client.session_transaction() as session:
        token = session["_csrf_token"]

    # Confirmar que el proyecto existe antes de eliminarlo.
    response = client.get("/projects/1")
    assert response.status_code == 200

    # Eliminar mediante POST.
    response = client.post(
        "/admin/projects/1/delete",
        data={"csrf_token": token},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"elimin" in response.data.lower()

    # Verificar que ya no existe.
    response = client.get("/projects/1")
    assert response.status_code == 404


def test_admin_cannot_delete_project_without_login(client):
    response = client.post(
        "/admin/projects/1/delete",
        data={"csrf_token": "token-invalido"},
    )

    assert response.status_code == 302
    assert "/admin/login" in response.headers["Location"]


def test_admin_can_list_skills(client):
    _admin_login(client)

    response = client.get("/admin/skills")

    assert response.status_code == 200
    assert b"Administrar habilidades" in response.data
    assert b"Python y Flask" in response.data


def test_admin_can_create_skill(client):
    _admin_login(client)

    with client.session_transaction() as session:
        token = session["_csrf_token"]

    response = client.post(
        "/admin/skills/new",
        data={
            "csrf_token": token,
            "name": "Docker",
            "percentage": "40",
            "sort_order": "7",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Docker" in response.data


def test_admin_can_edit_skill(client):
    _admin_login(client)

    from app.models.skill import get_all_skills

    skill = get_all_skills()[0]

    with client.session_transaction() as session:
        token = session["_csrf_token"]

    response = client.post(
        f"/admin/skills/{skill['id']}/edit",
        data={
            "csrf_token": token,
            "name": "HTML y CSS avanzado",
            "percentage": "85",
            "sort_order": "1",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"HTML y CSS avanzado" in response.data


def test_admin_can_delete_skill(client):
    _admin_login(client)

    from app.models.skill import get_all_skills

    skill = get_all_skills()[0]

    with client.session_transaction() as session:
        token = session["_csrf_token"]

    response = client.post(
        f"/admin/skills/{skill['id']}/delete",
        data={"csrf_token": token},
        follow_redirects=True,
    )

    assert response.status_code == 200

    from app.models.skill import get_skill_by_id

    assert get_skill_by_id(skill["id"]) is None


def test_skills_admin_requires_login(client):
    response = client.get("/admin/skills")

    assert response.status_code == 302
    assert "/admin/login" in response.headers["Location"]


def test_home_displays_skills_from_database(client):
    from app.models.skill import get_all_skills

    response = client.get("/")

    assert response.status_code == 200

    skills = get_all_skills()
    assert len(skills) > 0

    for skill in skills:
        assert skill["name"].encode("utf-8") in response.data
        assert (
            f'{skill["percentage"]}%'.encode("utf-8")
            in response.data
        )


def test_new_skill_appears_on_public_homepage(client):
    _admin_login(client)

    with client.session_transaction() as session:
        token = session["_csrf_token"]

    response = client.post(
        "/admin/skills/new",
        data={
            "csrf_token": token,
            "name": "Docker",
            "percentage": "40",
            "sort_order": "7",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200

    homepage = client.get("/")

    assert homepage.status_code == 200
    assert b"Docker" in homepage.data
    assert b"40%" in homepage.data



def test_home_displays_experiences_from_database(client):
    from app.models.experience import get_all_experiences

    # Consultar la base de datos dentro del contexto de Flask.
    with client.application.app_context():
        experiences = get_all_experiences()

    response = client.get("/")

    assert response.status_code == 200
    assert len(experiences) == 4

    for experience in experiences:
        assert experience["title"].encode("utf-8") in response.data
        assert experience["organization"].encode("utf-8") in response.data


def test_admin_can_list_experiences(client):
    _admin_login(client)

    response = client.get("/admin/experiences")

    assert response.status_code == 200
    assert b"Administrar" in response.data
    assert b"Desarrollo de proyectos web" in response.data


def test_new_experience_appears_on_public_homepage(client):
    _admin_login(client)

    with client.session_transaction() as session:
        token = session["_csrf_token"]

    response = client.post(
        "/admin/experiences/new",
        data={
            "csrf_token": token,
            "title": "Aplicación de prueba",
            "organization": "Proyecto personal",
            "start_date": "Octubre de 2026",
            "end_date": "Actualidad",
            "description": "Experiencia creada desde el panel administrativo.",
            "technologies": "Python, Flask, SQLite",
            "sort_order": "5",
            "category": "Proyecto personal",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200

    homepage = client.get("/")

    assert homepage.status_code == 200
    assert "Aplicación de prueba".encode("utf-8") in homepage.data
    assert "Proyecto personal".encode("utf-8") in homepage.data
    assert b"Python" in homepage.data
    assert b"SQLite" in homepage.data
