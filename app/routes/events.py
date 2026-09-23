from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
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
    # Search + filter upgrade - Bilkul!
    cat = request.args.get("category", "")
    q = request.args.get("q", "").strip()
    query = Event.query.filter_by(status="open")
    if cat:
        query = query.filter_by(category=cat)
    if q:
        like = f"%{q}%"
        query = query.filter((Event.title.ilike(like)) | (Event.venue.ilike(like)) | (Event.description.ilike(like)))
    return render_template("events.html", events=query.order_by(Event.id.desc()).all(), cat=cat, q=q)

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
    if Registration.query.filter_by(user_id=current_user.id, event_id=eid).first():
        flash("Already registered bro!", "warning")
        return redirect(url_for("events.detail", eid=eid))
    if e.seats_left <= 0:
        flash("Housefull! Seats over.", "danger")
        return redirect(url_for("events.detail", eid=eid))
    team = request.form.get("team", "")
    upi_ref = request.form.get("upi_ref", "")
    # Payment: free ya UPI ref / Razorpay Phase-2
    pay_status = "free" if e.fee == 0 else ("pending-verify" if upi_ref else "pending")
    r = Registration(user_id=current_user.id, event_id=eid, team=team, payment=pay_status)
    db.session.add(r)
    db.session.commit()
    try:
        from ..utils.qr_generator import make_qr
        make_qr(r.qr_token)
    except Exception:
        pass
    # Email notify (safe - console fallback)
    try:
        from ..utils.mail import send_mail
        send_mail(current_user.email, f"Registered: {e.title}", f"QR: {r.qr_token} | Payment: {pay_status}")
    except Exception:
        pass
    flash(f"Ho gaya! QR ticket ready. Payment: {pay_status}", "success")
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

@events_bp.route("/certificate/<qr_token>")
@login_required
def certificate(qr_token):
    """Auto PDF certificate - attended walo ke liye"""
    from ..models.user import User
    r = Registration.query.filter_by(qr_token=qr_token).first_or_404()
    if r.user_id != current_user.id and current_user.role not in ("admin", "organizer"):
        flash("Access denied!", "danger")
        return redirect(url_for("events.dashboard"))
    if not r.attended:
        flash("Pehle event attend karo, fir certificate milega!", "warning")
        return redirect(url_for("events.ticket", qr_token=qr_token))
    e = Event.query.get(r.event_id)
    u = User.query.get(r.user_id)
    from ..utils.certificate import make_certificate_pdf
    path = make_certificate_pdf(u.name, e.title, r.qr_token)
    return send_file(path, as_attachment=True, download_name=f"certificate_{r.qr_token}.pdf")
