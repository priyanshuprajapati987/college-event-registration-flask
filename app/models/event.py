from . import db
from datetime import datetime

class Event(db.Model):
    __tablename__ = "events"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, default="")
    category = db.Column(db.String(30), default="tech")  # tech|cultural|sports|workshop
    date = db.Column(db.String(30), nullable=False)  # MVP: string, Phase2: DateTime
    venue = db.Column(db.String(100), default="Main Auditorium")
    capacity = db.Column(db.Integer, default=100)
    fee = db.Column(db.Float, default=0.0)
    deadline = db.Column(db.String(30), default="")
    poster = db.Column(db.String(200), default="")
    status = db.Column(db.String(20), default="open")  # open|closed
    # Small-small details - Bilkul!
    mode = db.Column(db.String(20), default="offline")  # online|offline|hybrid
    event_type = db.Column(db.String(20), default="solo")  # solo|team
    team_max = db.Column(db.Integer, default=1)
    rules = db.Column(db.Text, default="")
    prizes = db.Column(db.String(200), default="")
    contact = db.Column(db.String(100), default="")  # phone / email
    organizer_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def registered_count(self):
        from .registration import Registration
        return Registration.query.filter_by(event_id=self.id).count()

    @property
    def seats_left(self):
        return max(0, self.capacity - self.registered_count)
