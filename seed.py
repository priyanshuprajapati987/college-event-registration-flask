# Demo data - python seed.py
from app import create_app
from app.models import db
from app.models.user import User
from app.models.event import Event

app = create_app()
with app.app_context():
    db.drop_all(); db.create_all()
    a = User(name="Admin", email="admin@college.edu", role="admin", roll_no="0", branch="CSE")
    a.set_password("admin123")
    o = User(name="Organizer", email="org@college.edu", role="organizer")
    o.set_password("org123")
    s = User(name="Rahul", email="rahul@college.edu", role="student", roll_no="21CS01", branch="CSE", year="3")
    s.set_password("123456")
    db.session.add_all([a, o, s])
    db.session.add_all([
        Event(title="HackNight 2026", description="12-hr hackathon", category="tech", date="2026-10-15 10:00", venue="CSE Block", capacity=100, fee=0, organizer_id=2),
        Event(title="Udaan Cultural Fest", description="Dance+Music", category="cultural", date="2026-11-02 17:00", venue="Main Ground", capacity=500, fee=50, organizer_id=2),
        Event(title="Python Workshop", description="Flask hands-on", category="workshop", date="2026-10-20 11:00", venue="Lab 4", capacity=60, fee=0, organizer_id=2),
    ])
    db.session.commit()
    print("Seed Ho gaya! admin@college.edu/admin123")
