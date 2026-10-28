import json

from app.database import get_db_connection

PROJECTS = [
    {
        "id": 1,
        "title": "Mi portafolio",
        "description": (
            "Aplicación web personal desarrollada con Flask para presentar "
            "mis proyectos, habilidades y recorrido como desarrollador."
        ),
        "technologies": [
            "Python", "Flask", "HTML", "CSS", "JavaScript"
        ],
        "github": "https://github.com/jonathan2004arenas/portafolio",
        "demo": "https://jonathan2004arenas.github.io/portafolio/",
        "image": "img/panorama-silueta-centro-manhattan-ciudad-nueva-york-al-atardecer-rascacielos-cielo-colorido-sobre-rio 1.png",
        "featured": False,
    },
    {
        "id": 2,
        "title": "Cinemafull",
        "description": (
            "Sitio web temático dedicado a películas y series, creado como "
            "práctica de diseño y desarrollo web."
        ),
        "technologies": ["HTML", "CSS", "PHP", "Git"],
        "github": "https://github.com/jonathan2004arenas/Cinemafull",
        "demo": "https://jonathan2004arenas.github.io/Cinemafull/",
        "image": "img/Cinemafull.png",
        "featured": True,
    },
    {
        "id": 3,
        "title": "Cara de Papa",
        "description": (
            "Ejercicio visual que construye un personaje inspirado en Toy "
            "Story utilizando elementos y estilos de HTML y CSS."
        ),
        "technologies": ["HTML", "CSS"],
        "github": "https://github.com/jonathan2004arenas/cara-de-papa",
        "demo": "https://jonathan2004arenas.github.io/cara-de-papa/",
        "image": "img/caradpapa.png",
        "featured": True,
    },
    {
        "id": 4,
        "title": "Rumbo",
        "description": (
            "Propuesta web dedicada a destinos turísticos y planificación "
            "de viajes."
        ),
        "technologies": ["HTML", "CSS", "JavaScript"],
        "github": "https://github.com/jonathan2004arenas/Rumbo",
        "demo": "https://jonathan2004arenas.github.io/Rumbo/",
        "image": "img/rumbo.png",
        "featured": True,
    },
    {
        "id": 5,
        "title": "Website Bootstrap",
        "description": (
            "Práctica de diseño web adaptable utilizando Bootstrap, HTML, "
            "CSS y JavaScript."
        ),
        "technologies": ["HTML", "CSS", "JavaScript", "Bootstrap"],
        "github": "https://github.com/jonathan2004arenas/Bootstrap",
        "demo": "https://jonathan2004arenas.github.io/Bootstrap/",
        "image": "img/website-bootstrap.png",
        "featured": True,
    },
]


def get_default_projects():
    """Devuelve todos los proyectos."""
    return PROJECTS.copy()


def _row_to_project(row):
    """Convierte una fila de SQLite en un diccionario de Python."""
    if row is None:
        return None

    project = dict(row)

    project["technologies"] = json.loads(
        project.get("technologies") or "[]"
    )
    project["featured"] = bool(project["featured"])

    return project


def get_all_projects():
    """Obtiene todos los proyectos guardados en SQLite."""
    connection = get_db_connection()

    try:
        rows = connection.execute(
            "SELECT * FROM projects ORDER BY id"
        ).fetchall()

        return [_row_to_project(row) for row in rows]
    finally:
        connection.close()


def get_project_by_id(project_id):
    """Obtiene un proyecto por su identificador."""
    connection = get_db_connection()

    try:
        row = connection.execute(
            "SELECT * FROM projects WHERE id = ?",
            (project_id,),
        ).fetchone()

        return _row_to_project(row)
    finally:
        connection.close()


def get_all_technologies():
    """Devuelve las tecnologías utilizadas en los proyectos."""
    technologies = set()

    for project in get_all_projects():
        technologies.update(project["technologies"])

    return sorted(technologies, key=str.lower)


def get_featured_projects():
    """Obtiene los proyectos destacados."""
    connection = get_db_connection()

    try:
        rows = connection.execute(
            """
            SELECT * FROM projects
            WHERE featured = 1
            ORDER BY id
            """
        ).fetchall()

        return [_row_to_project(row) for row in rows]
    finally:
        connection.close()


def create_project(data):
    """Guarda un nuevo proyecto."""
    connection = get_db_connection()

    try:
        cursor = connection.execute(
            """
            INSERT INTO projects (
                title, description, technologies,
                github, demo, image, featured
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data["title"].strip(),
                data["description"].strip(),
                json.dumps(
                    data.get("technologies", []),
                    ensure_ascii=False,
                ),
                data.get("github", "").strip(),
                data.get("demo", "").strip(),
                data.get("image", "").strip(),
                int(bool(data.get("featured", False))),
            ),
        )

        project_id = cursor.lastrowid
        connection.commit()

        return get_project_by_id(project_id)
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def update_project(project_id, data):
    """Actualiza los datos de un proyecto existente."""
    connection = get_db_connection()

    try:
        cursor = connection.execute(
            """
            UPDATE projects
            SET title = ?,
                description = ?,
                technologies = ?,
                github = ?,
                demo = ?,
                image = ?,
                featured = ?
            WHERE id = ?
            """,
            (
                data["title"].strip(),
                data["description"].strip(),
                json.dumps(
                    data.get("technologies", []),
                    ensure_ascii=False,
                ),
                data.get("github", "").strip(),
                data.get("demo", "").strip(),
                data.get("image", "").strip(),
                int(bool(data.get("featured", False))),
                project_id,
            ),
        )

        connection.commit()

        if cursor.rowcount == 0:
            return None

        return get_project_by_id(project_id)
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def delete_project(project_id):
    """Elimina un proyecto por su identificador."""
    connection = get_db_connection()

    try:
        cursor = connection.execute(
            "DELETE FROM projects WHERE id = ?",
            (project_id,),
        )

        connection.commit()

        return cursor.rowcount > 0
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()
