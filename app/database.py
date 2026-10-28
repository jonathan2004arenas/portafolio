
import json
import os
import sqlite3

from flask import current_app


def get_db_connection():
    """Abre una conexión con la base de datos SQLite."""
    connection = sqlite3.connect(current_app.config["DATABASE"])
    connection.row_factory = sqlite3.Row
    return connection


def init_db(app):
    """Crea la tabla de proyectos y copia los proyectos iniciales."""

    os.makedirs(app.instance_path, exist_ok=True)

    with app.app_context():
        connection = get_db_connection()

        try:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS projects (
                    id INTEGER PRIMARY KEY,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    technologies TEXT NOT NULL DEFAULT '[]',
                    github TEXT,
                    demo TEXT,
                    image TEXT,
                    featured INTEGER NOT NULL DEFAULT 0
                )
                """
            )

            connection.commit()

            # Importación local para evitar dependencias circulares.
            from app.models.project import get_default_projects

            existing_count = connection.execute(
                "SELECT COUNT(*) FROM projects"
            ).fetchone()[0]

            # Importar los proyectos actuales solo la primera vez.
            if existing_count == 0:
                projects = get_default_projects()

                for project in projects:
                    connection.execute(
                        """
                        INSERT INTO projects (
                            id, title, description, technologies,
                            github, demo, image, featured
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            project["id"],
                            project["title"],
                            project["description"],
                            json.dumps(
                                project.get("technologies", []),
                                ensure_ascii=False,
                            ),
                            project.get("github", ""),
                            project.get("demo", ""),
                            project.get("image", ""),
                            int(project.get("featured", False)),
                        ),
                    )

                connection.commit()

            
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS skills (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    percentage INTEGER NOT NULL DEFAULT 0
                        CHECK (percentage BETWEEN 0 AND 100),
                    sort_order INTEGER NOT NULL DEFAULT 0
                )
                """
            )

            connection.commit()

            # Cargar las habilidades iniciales solo si la tabla está vacía.
            skills_count = connection.execute(
                "SELECT COUNT(*) FROM skills"
            ).fetchone()[0]

            if skills_count == 0:
                initial_skills = [
                    ("HTML y CSS", 80, 1),
                    ("MySQL", 55, 2),
                    ("PHP", 45, 3),
                    ("Python y Flask", 60, 4),
                    ("JavaScript", 50, 5),
                    ("Git y GitHub", 55, 6),
                ]

                connection.executemany(
                    """
                    INSERT INTO skills (name, percentage, sort_order)
                    VALUES (?, ?, ?)
                    """,
                    initial_skills,
                )

                connection.commit()

            
            # Crear la tabla de experiencias profesionales y proyectos.
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS experiences (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    organization TEXT NOT NULL,
                    start_date TEXT NOT NULL DEFAULT '',
                    end_date TEXT NOT NULL DEFAULT '',
                    description TEXT NOT NULL,
                    technologies TEXT NOT NULL DEFAULT '[]',
                    sort_order INTEGER NOT NULL DEFAULT 0
                )
                """
            )
            connection.commit()


        finally:
            connection.close()
