
# app/__init__.py

from flask import Flask


def create_app():
    app = Flask(
        __name__,
        template_folder="views",
        static_folder="static",
    )

    from app.controllers.main_controller import main_bp
    from app.controllers.project_controller import project_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(project_bp)

    return app
