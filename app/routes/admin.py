from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file, current_app, jsonify
from flask_login import login_required, current_user
from functools import wraps
from werkzeug.utils import secure_filename
from ..models import db
from ..models.event import Event
from ..models.registration import Registration
from ..models.user import User
import os

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

def role_required(*roles):
    def deco(fn):
        @wraps(fn)
        @login_required
        def inner(*a, **kw):
            if current_user.role not in roles:
                flash("Access denied bro!", "danger")
                return redirect(url_for("events.index"))
            return fn(*a, **kw)
        return inner
    return deco

@admin_bp.route("/")
@role_required("admin", "organizer")
def panel():
    evts = Event.query.order_by(Event.id.desc()).all()
    return render_template("admin.html", events=evts)

@admin_bp.route("/event/new", methods=["GET", "POST"])
@role_required("admin", "organizer")
def new_event():
    if request.method == "POST":
        # Poster upload - Bilkul!
        poster_name = ""
        f = request.files.get("poster")
        if f and f.filename:
            ext = f.filename.rsplit(".", 1)[-1].lower()
            if ext in current_app.config["ALLOWED_EXT"]:
                poster_name = secure_filename(f.filename)
                f.save(os.path.join(current_app.config["UPLOAD_FOLDER"], poster_name))
        e = Event(
            title=request.form.get("title"),
            description=request.form.get("description", ""),
            category=request.form.get("category", "tech"),
            date=request.form.get("date", ""),
            venue=request.form.get("venue", "Main Auditorium"),
            capacity=int(request.form.get("capacity", 100)),
            fee=float(request.form.get("fee", 0)),
            deadline=request.form.get("deadline", ""),
            poster=poster_name,
            organizer_id=current_user.id,
        )
        db.session.add(e)
        db.session.commit()
        flash("Event create Ho gaya with poster!", "success")
        return redirect(url_for("admin.panel"))
    return render_template("create_event.html")

@admin_bp.route("/event/<int:eid>")
@role_required("admin", "organizer")
def view_event(eid):
    e = Event.query.get_or_404(eid)
    regs = Registration.query.filter_by(event_id=eid).all()
    users = {u.id: u for u in User.query.all()}
    return render_template("admin_reg.html", e=e, regs=regs, users=users)

@admin_bp.route("/checkin/<qr_token>", methods=["GET", "POST"])
@role_required("admin", "organizer")
def checkin(qr_token):
    token = qr_token.replace("CHECKIN:", "").strip()
    r = Registration.query.filter_by(qr_token=token).first_or_404()
    r.attended = True
    r.status = "approved"
    db.session.commit()
    flash(f"Check-in done! Reg #{r.id}", "success")
    return redirect(url_for("admin.view_event", eid=r.event_id))

@admin_bp.route("/scanner")
@role_required("admin", "organizer")
def scanner():
    return render_template("scanner.html")

@admin_bp.route("/analytics")
@role_required("admin", "organizer")
def analytics():
    evts = Event.query.all()
    labels = [e.title[:15] for e in evts]
    counts = [Registration.query.filter_by(event_id=e.id).count() for e in evts]
    attended = [Registration.query.filter_by(event_id=e.id, attended=True).count() for e in evts]
    cats = {}
    for e in evts:
        cats[e.category] = cats.get(e.category, 0) + 1
    total_users = User.query.count()
    total_regs = Registration.query.count()
    return render_template("analytics.html", labels=labels, counts=counts, attended=attended,
                           cats=cats, total_users=total_users, total_regs=total_regs, evts=evts)

@admin_bp.route("/api/stats")
@role_required("admin", "organizer")
def api_stats():
    evts = Event.query.all()
    return jsonify([{"title": e.title, "reg": Registration.query.filter_by(event_id=e.id).count()} for e in evts])

@admin_bp.route("/event/<int:eid>/export")
@role_required("admin", "organizer")
def export(eid):
    from ..utils.excel_export import export_csv
    path = export_csv(eid)
    return send_file(path, as_attachment=True)
