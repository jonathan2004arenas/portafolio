from flask import Blueprint, render_template

from app.models.project import get_featured_projects
from app.models.skill import get_all_skills

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def home():
    return render_template(
        "index.html",
        featured_projects=get_featured_projects(),
        skills=get_all_skills(),
    )

@main_bp.route("/contacto")
def contact():
    return render_template("contact.html")