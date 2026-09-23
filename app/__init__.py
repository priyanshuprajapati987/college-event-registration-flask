from flask import Flask
import os
from .config import Config
from .models import db, login_manager
from .models.user import User

def create_app():
    """App factory - testing + prod dono ke liye best"""
    app = Flask(__name__)
    app.config.from_object(Config)

    # Folders banao agar nahi he
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    os.makedirs(app.config["QR_FOLDER"], exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Blueprints register
    from .routes.auth import auth_bp
    from .routes.events import events_bp
    from .routes.admin import admin_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(events_bp)
    app.register_blueprint(admin_bp)

    with app.app_context():
        db.create_all()  # MVP ke liye ok, prod me flask-migrate

    return app
