from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from ..models import db
from ..models.event import Event
from ..models.registration import Registration

events_bp = Blueprint("events", __name__)

@events_bp.route("/")
def index():
    evts = Event.query.filter_by(status="open").order_by(Event.id.desc()).limit(20).all()
    return render_template("index.html", events=evts)

@events_bp.route("/events")
def list_events():
    cat = request.args.get("category", "")
    q = Event.query.filter_by(status="open")
    if cat:
        q = q.filter_by(category=cat)
    return render_template("events.html", events=q.order_by(Event.id.desc()).all(), cat=cat)

@events_bp.route("/event/<int:eid>")
def detail(eid):
    e = Event.query.get_or_404(eid)
    mine = None
    if current_user.is_authenticated:
        mine = Registration.query.filter_by(user_id=current_user.id, event_id=eid).first()
    return render_template("event_detail.html", e=e, mine=mine)

@events_bp.route("/event/<int:eid>/register", methods=["POST"])
@login_required
def register_event(eid):
    e = Event.query.get_or_404(eid)
    # checks: duplicate, capacity
    if Registration.query.filter_by(user_id=current_user.id, event_id=eid).first():
        flash("Already registered bro!", "warning")
        return redirect(url_for("events.detail", eid=eid))
    if e.seats_left <= 0:
        flash("Housefull! Seats over.", "danger")
        return redirect(url_for("events.detail", eid=eid))
    team = request.form.get("team", "")
    r = Registration(user_id=current_user.id, event_id=eid, team=team,
                     payment="free" if e.fee == 0 else "pending")
    db.session.add(r)
    db.session.commit()
    # QR banao
    try:
        from ..utils.qr_generator import make_qr
        make_qr(r.qr_token)
    except Exception:
        pass
    flash("Registration Ho gaya! QR ticket dashboard me he.", "success")
    return redirect(url_for("events.dashboard"))

@events_bp.route("/dashboard")
@login_required
def dashboard():
    regs = Registration.query.filter_by(user_id=current_user.id).order_by(Registration.id.desc()).all()
    ev_map = {e.id: e for e in Event.query.all()}
    return render_template("dashboard.html", regs=regs, ev_map=ev_map)

@events_bp.route("/ticket/<qr_token>")
@login_required
def ticket(qr_token):
    r = Registration.query.filter_by(qr_token=qr_token).first_or_404()
    e = Event.query.get(r.event_id)
    return render_template("ticket.html", r=r, e=e)
