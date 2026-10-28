
from app.database import get_db_connection


def get_all_skills():
    """Devuelve todas las habilidades ordenadas."""
    connection = get_db_connection()

    try:
        rows = connection.execute(
            "SELECT * FROM skills ORDER BY sort_order, id"
        ).fetchall()

        return [dict(row) for row in rows]
    finally:
        connection.close()


def get_skill_by_id(skill_id):
    """Busca una habilidad por su ID."""
    connection = get_db_connection()

    try:
        row = connection.execute(
            "SELECT * FROM skills WHERE id = ?",
            (skill_id,),
        ).fetchone()

        return dict(row) if row else None
    finally:
        connection.close()


def create_skill(data):
    """Crea una habilidad."""
    connection = get_db_connection()

    try:
        cursor = connection.execute(
            """
            INSERT INTO skills (name, percentage, sort_order)
            VALUES (?, ?, ?)
            """,
            (
                data["name"].strip(),
                int(data["percentage"]),
                int(data["sort_order"]),
            ),
        )

        skill_id = cursor.lastrowid
        connection.commit()

        row = connection.execute(
            "SELECT * FROM skills WHERE id = ?",
            (skill_id,),
        ).fetchone()

        return dict(row)
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def update_skill(skill_id, data):
    """Actualiza una habilidad existente."""
    connection = get_db_connection()

    try:
        cursor = connection.execute(
            """
            UPDATE skills
            SET name = ?, percentage = ?, sort_order = ?
            WHERE id = ?
            """,
            (
                data["name"].strip(),
                int(data["percentage"]),
                int(data["sort_order"]),
                skill_id,
            ),
        )

        connection.commit()

        if cursor.rowcount == 0:
            return None

        row = connection.execute(
            "SELECT * FROM skills WHERE id = ?",
            (skill_id,),
        ).fetchone()

        return dict(row)
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def delete_skill(skill_id):
    """Elimina una habilidad."""
    connection = get_db_connection()

    try:
        cursor = connection.execute(
            "DELETE FROM skills WHERE id = ?",
            (skill_id,),
        )

        connection.commit()
        return cursor.rowcount > 0
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()
