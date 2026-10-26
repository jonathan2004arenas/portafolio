
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
