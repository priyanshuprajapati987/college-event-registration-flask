from . import db
from datetime import datetime
import secrets

class Registration(db.Model):
    __tablename__ = "registrations"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey("events.id"), nullable=False)
    team = db.Column(db.Text, default="")  # comma names
    status = db.Column(db.String(20), default="approved")  # approved|pending|rejected
    payment = db.Column(db.String(20), default="free")  # free|pending|verified
    qr_token = db.Column(db.String(50), unique=True, default=lambda: secrets.token_hex(8))
    attended = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint("user_id", "event_id", name="uix_user_event"),)
