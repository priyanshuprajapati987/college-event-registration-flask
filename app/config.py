import os

class Config:
    # Basic config - .env se override hota he
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-college-event-123")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///events.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), "app", "static", "uploads")
    QR_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), "app", "static", "qr")
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024  # 2MB poster limit
    ALLOWED_EXT = {"png", "jpg", "jpeg"}
    MAIL_SERVER = os.environ.get("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.environ.get("MAIL_PORT", 587))
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME", "")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD", "")
