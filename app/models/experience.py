
import json

from app.database import get_db_connection


def get_all_experiences():
    """Devuelve las experiencias ordenadas para mostrarlas."""
    connection = get_db_connection()

    try:
        rows = connection.execute(
            """
            SELECT *
            FROM experiences
            ORDER BY sort_order, id
            """
        ).fetchall()

        experiences = []

        for row in rows:
            experience = dict(row)
            experience["technologies"] = json.loads(
                experience["technologies"]
            )
            experiences.append(experience)

        return experiences
    finally:
        connection.close()


def get_experience_by_id(experience_id):
    """Busca una experiencia por su ID."""
    connection = get_db_connection()

    try:
        row = connection.execute(
            "SELECT * FROM experiences WHERE id = ?",
            (experience_id,),
        ).fetchone()

        if row is None:
            return None

        experience = dict(row)
        experience["technologies"] = json.loads(
            experience["technologies"]
        )

        return experience
    finally:
        connection.close()


def create_experience(data):
    """Crea una experiencia."""
    connection = get_db_connection()

    try:
        cursor = connection.execute(
            """
            INSERT INTO experiences (
                title,
                organization,
                start_date,
                end_date,
                description,
                technologies,
                sort_order
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data["title"].strip(),
                data["organization"].strip(),
                data.get("start_date", "").strip(),
                data.get("end_date", "").strip(),
                data["description"].strip(),
                json.dumps(
                    data.get("technologies", []),
                    ensure_ascii=False,
                ),
                int(data.get("sort_order", 0)),
            ),
        )

        experience_id = cursor.lastrowid
        connection.commit()

        return get_experience_by_id(experience_id)

    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def update_experience(experience_id, data):
    """Actualiza una experiencia existente."""
    connection = get_db_connection()

    try:
        cursor = connection.execute(
            """
            UPDATE experiences
            SET title = ?,
                organization = ?,
                start_date = ?,
                end_date = ?,
                description = ?,
                technologies = ?,
                sort_order = ?
            WHERE id = ?
            """,
            (
                data["title"].strip(),
                data["organization"].strip(),
                data.get("start_date", "").strip(),
                data.get("end_date", "").strip(),
                data["description"].strip(),
                json.dumps(
                    data.get("technologies", []),
                    ensure_ascii=False,
                ),
                int(data.get("sort_order", 0)),
                experience_id,
            ),
        )

        if cursor.rowcount == 0:
            connection.rollback()
            return None

        connection.commit()

        row = connection.execute(
            "SELECT * FROM experiences WHERE id = ?",
            (experience_id,),
        ).fetchone()

        experience = dict(row)
        experience["technologies"] = json.loads(
            experience["technologies"]
        )

        return experience

    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def delete_experience(experience_id):
    """Elimina una experiencia."""
    connection = get_db_connection()

    try:
        cursor = connection.execute(
            "DELETE FROM experiences WHERE id = ?",
            (experience_id,),
        )

        connection.commit()
        return cursor.rowcount > 0

    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()
