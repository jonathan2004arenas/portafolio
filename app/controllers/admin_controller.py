
import hmac
import secrets
from functools import wraps

from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.security import check_password_hash

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


def csrf_token():
    """Obtiene o crea un token CSRF para la sesión actual."""
    if "_csrf_token" not in session:
        session["_csrf_token"] = secrets.token_hex(32)

    return session["_csrf_token"]


@admin_bp.app_context_processor
def inject_csrf_token():
    return {"csrf_token": csrf_token}


def validate_csrf():
    """Valida el token CSRF enviado por un formulario."""
    submitted_token = request.form.get("csrf_token", "")
    session_token = session.get("_csrf_token", "")

    if (
        not submitted_token
        or not session_token
        or not hmac.compare_digest(submitted_token, session_token)
    ):
        abort(400, description="Token CSRF inválido.")


def login_required(view):
    """Impide el acceso a las rutas privadas sin iniciar sesión."""
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if not session.get("admin_logged_in"):
            return redirect(url_for("admin.login"))

        return view(*args, **kwargs)

    return wrapped_view


@admin_bp.route("/login", methods=["GET", "POST"])
def login():
    if session.get("admin_logged_in"):
        return redirect(url_for("admin.dashboard"))

    if request.method == "POST":
        validate_csrf()

        password = request.form.get("password", "")
        password_hash = current_app.config["ADMIN_PASSWORD_HASH"]

        if check_password_hash(password_hash, password):
            session.clear()
            session["admin_logged_in"] = True
            session["_csrf_token"] = secrets.token_hex(32)

            flash("Has iniciado sesión correctamente.", "success")
            return redirect(url_for("admin.dashboard"))

        flash("La contraseña no es correcta.", "error")

    return render_template("admin_login.html")


@admin_bp.route("/")
@login_required
def dashboard():
    from app.models.project import get_all_projects

    projects = get_all_projects()

    return render_template(
        "admin_dashboard.html",
        projects=projects,
    )


@admin_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    validate_csrf()
    session.clear()

    flash("Has cerrado sesión.", "success")
    return redirect(url_for("admin.login"))


def _get_project_form_data():
    """Obtiene y valida los campos enviados por el formulario."""
    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()

    technologies_text = request.form.get("technologies", "")
    technologies = [
        technology.strip()
        for technology in technologies_text.split(",")
        if technology.strip()
    ]

    data = {
        "title": title,
        "description": description,
        "technologies": technologies,
        "github": request.form.get("github", "").strip(),
        "demo": request.form.get("demo", "").strip(),
        "image": request.form.get("image", "").strip(),
        "featured": request.form.get("featured") == "on",
    }

    if not title or not description:
        return None

    return data


@admin_bp.route("/projects/new", methods=["GET", "POST"])
@login_required
def create_project_view():
    from app.models.project import create_project

    if request.method == "POST":
        validate_csrf()
        data = _get_project_form_data()

        if data is None:
            flash(
                "El título y la descripción son obligatorios.",
                "error",
            )
            return render_template(
                "admin_project_form.html",
                project=None,
                form_title="Crear proyecto",
            ), 400

        create_project(data)
        flash("Proyecto creado correctamente.", "success")

        return redirect(url_for("admin.dashboard"))

    return render_template(
        "admin_project_form.html",
        project=None,
        form_title="Crear proyecto",
    )


@admin_bp.route(
    "/projects/<int:project_id>/edit",
    methods=["GET", "POST"],
)
@login_required
def edit_project_view(project_id):
    from app.models.project import (
        get_project_by_id,
        update_project,
    )

    project = get_project_by_id(project_id)

    if project is None:
        abort(404)

    if request.method == "POST":
        validate_csrf()
        data = _get_project_form_data()

        if data is None:
            flash(
                "El título y la descripción son obligatorios.",
                "error",
            )
            return render_template(
                "admin_project_form.html",
                project=project,
                form_title="Editar proyecto",
            ), 400

        update_project(project_id, data)
        flash("Proyecto actualizado correctamente.", "success")

        return redirect(url_for("admin.dashboard"))

    return render_template(
        "admin_project_form.html",
        project=project,
        form_title="Editar proyecto",
    )

@admin_bp.route(
    "/projects/<int:project_id>/delete",
    methods=["POST"],
)
@login_required
def delete_project_view(project_id):
    from app.models.project import (
        delete_project,
        get_project_by_id,
    )

    # Comprobar que el proyecto existe antes de eliminarlo.
    project = get_project_by_id(project_id)

    if project is None:
        abort(404)

    # Validar el token de seguridad del formulario.
    validate_csrf()

    deleted = delete_project(project_id)

    if not deleted:
        abort(404)

    flash(
        f'El proyecto "{project["title"]}" se eliminó correctamente.',
        "success",
    )

    return redirect(url_for("admin.dashboard"))


def _get_skill_form_data():
    """Valida los datos enviados desde el formulario de habilidades."""
    name = request.form.get("name", "").strip()
    percentage_text = request.form.get("percentage", "")
    sort_order_text = request.form.get("sort_order", "0")

    if not name:
        return None

    try:
        percentage = int(percentage_text)
        sort_order = int(sort_order_text)
    except (TypeError, ValueError):
        return None

    if not 0 <= percentage <= 100 or sort_order < 0:
        return None

    return {
        "name": name,
        "percentage": percentage,
        "sort_order": sort_order,
    }


@admin_bp.route("/skills")
@login_required
def skills_list():
    from app.models.skill import get_all_skills

    return render_template(
        "admin_skills.html",
        skills=get_all_skills(),
    )


@admin_bp.route("/skills/new", methods=["GET", "POST"])
@login_required
def create_skill_view():
    from app.models.skill import create_skill

    if request.method == "POST":
        validate_csrf()
        data = _get_skill_form_data()

        if data is None:
            flash(
                "Revisa el nombre, el porcentaje (0 a 100) y el orden.",
                "error",
            )
            return render_template(
                "admin_skill_form.html",
                skill=None,
                form_title="Crear habilidad",
            ), 400

        try:
            create_skill(data)
        except Exception as error:
            # El nombre es único. Evitamos mostrar detalles internos.
            current_app.logger.warning(
                "No se pudo crear la habilidad: %s", error
            )
            flash(
                "No se pudo guardar la habilidad. "
                "Comprueba que no exista otra con el mismo nombre.",
                "error",
            )
            return render_template(
                "admin_skill_form.html",
                skill=None,
                form_title="Crear habilidad",
            ), 400

        flash("Habilidad creada correctamente.", "success")
        return redirect(url_for("admin.skills_list"))

    return render_template(
        "admin_skill_form.html",
        skill=None,
        form_title="Crear habilidad",
    )


@admin_bp.route(
    "/skills/<int:skill_id>/edit",
    methods=["GET", "POST"],
)
@login_required
def edit_skill_view(skill_id):
    from app.models.skill import get_skill_by_id, update_skill

    skill = get_skill_by_id(skill_id)

    if skill is None:
        abort(404)

    if request.method == "POST":
        validate_csrf()
        data = _get_skill_form_data()

        if data is None:
            flash(
                "Revisa el nombre, el porcentaje (0 a 100) y el orden.",
                "error",
            )
            return render_template(
                "admin_skill_form.html",
                skill=skill,
                form_title="Editar habilidad",
            ), 400

        try:
            updated = update_skill(skill_id, data)
        except Exception as error:
            current_app.logger.warning(
                "No se pudo actualizar la habilidad: %s", error
            )
            flash(
                "No se pudo guardar. Comprueba que no exista otra "
                "habilidad con el mismo nombre.",
                "error",
            )
            return render_template(
                "admin_skill_form.html",
                skill=skill,
                form_title="Editar habilidad",
            ), 400

        if updated is None:
            abort(404)

        flash("Habilidad actualizada correctamente.", "success")
        return redirect(url_for("admin.skills_list"))

    return render_template(
        "admin_skill_form.html",
        skill=skill,
        form_title="Editar habilidad",
    )


@admin_bp.route(
    "/skills/<int:skill_id>/delete",
    methods=["POST"],
)
@login_required
def delete_skill_view(skill_id):
    from app.models.skill import delete_skill, get_skill_by_id

    skill = get_skill_by_id(skill_id)

    if skill is None:
        abort(404)

    validate_csrf()
    delete_skill(skill_id)

    flash("Habilidad eliminada correctamente.", "success")
    return redirect(url_for("admin.skills_list"))


def _get_experience_form_data():
    """Valida los datos enviados desde el formulario de experiencias."""
    title = request.form.get("title", "").strip()
    organization = request.form.get("organization", "").strip()
    start_date = request.form.get("start_date", "").strip()
    end_date = request.form.get("end_date", "").strip()
    description = request.form.get("description", "").strip()
    technologies_text = request.form.get("technologies", "")
    sort_order_text = request.form.get("sort_order", "0")
    category = request.form.get("category", "").strip()

    allowed_categories = {
        "Experiencia laboral",
        "Formación académica",
        "Formación complementaria",
        "Proyecto personal",
    }

    if category not in allowed_categories:
        return None, "Selecciona una categoría válida."

    technologies = [
        technology.strip()
        for technology in technologies_text.split(",")
        if technology.strip()
    ]

    if not title or not organization or not description:
        return None

    try:
        sort_order = int(sort_order_text)
    except (TypeError, ValueError):
        return None

    if sort_order < 0:
        return None

    return {
        "title": title,
        "organization": organization,
        "start_date": start_date,
        "end_date": end_date,
        "description": description,
        "technologies": technologies,
        "sort_order": sort_order,
        "category": category,
    }


@admin_bp.route("/experiences")
@login_required
def experiences_list():
    from app.models.experience import get_all_experiences

    return render_template(
        "admin_experiences.html",
        experiences=get_all_experiences(),
    )


@admin_bp.route("/experiences/new", methods=["GET", "POST"])
@login_required
def create_experience_view():
    from app.models.experience import create_experience

    if request.method == "POST":
        validate_csrf()
        data = _get_experience_form_data()

        if data is None:
            flash(
                "Revisa los campos obligatorios y el orden de visualización.",
                "error",
            )
            return render_template(
                "admin_experience_form.html",
                experience=None,
                form_title="Crear experiencia",
            ), 400

        try:
            create_experience(data)
        except Exception:
            current_app.logger.exception(
                "No se pudo crear la experiencia."
            )
            flash("No se pudo guardar la experiencia.", "error")
            return render_template(
                "admin_experience_form.html",
                experience=None,
                form_title="Crear experiencia",
            ), 400

        flash("Experiencia creada correctamente.", "success")
        return redirect(url_for("admin.experiences_list"))

    return render_template(
        "admin_experience_form.html",
        experience=None,
        form_title="Crear experiencia",
    )


@admin_bp.route(
    "/experiences/<int:experience_id>/edit",
    methods=["GET", "POST"],
)
@login_required
def edit_experience_view(experience_id):
    from app.models.experience import (
        get_experience_by_id,
        update_experience,
    )

    experience = get_experience_by_id(experience_id)

    if experience is None:
        abort(404)

    if request.method == "POST":
        validate_csrf()
        data = _get_experience_form_data()

        if data is None:
            flash(
                "Revisa los campos obligatorios y el orden de visualización.",
                "error",
            )
            return render_template(
                "admin_experience_form.html",
                experience=experience,
                form_title="Editar experiencia",
            ), 400

        updated = update_experience(experience_id, data)

        if updated is None:
            abort(404)

        flash("Experiencia actualizada correctamente.", "success")
        return redirect(url_for("admin.experiences_list"))

    return render_template(
        "admin_experience_form.html",
        experience=experience,
        form_title="Editar experiencia",
    )


@admin_bp.route(
    "/experiences/<int:experience_id>/delete",
    methods=["POST"],
)
@login_required
def delete_experience_view(experience_id):
    from app.models.experience import (
        delete_experience,
        get_experience_by_id,
    )

    experience = get_experience_by_id(experience_id)

    if experience is None:
        abort(404)

    validate_csrf()

    deleted = delete_experience(experience_id)

    if not deleted:
        abort(404)

    flash("Experiencia eliminada correctamente.", "success")
    return redirect(url_for("admin.experiences_list"))
