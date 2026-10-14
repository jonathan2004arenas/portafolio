
# app/controllers/project_controller.py

from flask import Blueprint, abort, render_template, jsonify

from app.models.project import (
    get_all_projects,
    get_project_by_id,
    get_all_technologies
)

project_bp = Blueprint("projects", __name__)



@project_bp.route("/projects")
def list_projects():
    projects = get_all_projects()
    technologies = get_all_technologies()

    return render_template(
        "projects.html",
        projects=projects,
        technologies=technologies,
    )


@project_bp.route("/projects/<int:project_id>")
def project_detail(project_id):
    project = get_project_by_id(project_id)

    if project is None:
        abort(404)

    return render_template(
        "project_detail.html",
        project=project,
    )


@project_bp.route("/api/projects")
def projects_api():
    return jsonify(get_all_projects())
