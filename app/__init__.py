
import os

from dotenv import load_dotenv
from flask import Flask


def create_app():
    load_dotenv()

    app = Flask(
        __name__,
        template_folder="views",
        static_folder="static",
        instance_relative_config=True,
    )

    app.config["DATABASE"] = os.path.join(
        app.instance_path, "portfolio.db"
    )
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
    app.config["ADMIN_PASSWORD_HASH"] = os.environ.get(
        "ADMIN_PASSWORD_HASH"
    )

    if not app.config["SECRET_KEY"]:
        raise RuntimeError(
            "Falta SECRET_KEY. Configúrala en el archivo .env."
        )

    if not app.config["ADMIN_PASSWORD_HASH"]:
        raise RuntimeError(
            "Falta ADMIN_PASSWORD_HASH. Configúralo en el archivo .env."
        )

    from app.controllers.main_controller import main_bp
    from app.controllers.project_controller import project_bp
    from app.controllers.admin_controller import admin_bp
    from app.database import init_db

    app.register_blueprint(main_bp)
    app.register_blueprint(project_bp)
    app.register_blueprint(admin_bp)

    init_db(app)

    return app