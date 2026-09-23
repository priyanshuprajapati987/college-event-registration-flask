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

def save_poster(f):
    """Poster save helper - Bilkul!"""
    if not f or not f.filename:
        return ""
    ext = f.filename.rsplit(".", 1)[-1].lower() if "." in f.filename else ""
    if ext not in current_app.config["ALLOWED_EXT"]:
        return ""
    import time
    name = f"{int(time.time())}_{secure_filename(f.filename)}"
    f.save(os.path.join(current_app.config["UPLOAD_FOLDER"], name))
    return name

def fill_event(e, form):
    e.title = form.get("title", e.title)
    e.description = form.get("description", "")
    e.category = form.get("category", "tech")
    e.date = form.get("date", "")
    e.venue = form.get("venue", "Main Auditorium")
    e.capacity = int(form.get("capacity", 100) or 100)
    e.fee = float(form.get("fee", 0) or 0)
    e.deadline = form.get("deadline", "")
    e.mode = form.get("mode", "offline")
    e.event_type = form.get("event_type", "solo")
    e.team_max = int(form.get("team_max", 1) or 1)
    e.rules = form.get("rules", "")
    e.prizes = form.get("prizes", "")
    e.contact = form.get("contact", "")
    return e

@admin_bp.route("/event/new", methods=["GET", "POST"])
@role_required("admin", "organizer")
def new_event():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        if not title:
            flash("Title to dalo bro!", "danger")
            return redirect(url_for("admin.new_event"))
        e = Event(title=title, organizer_id=current_user.id)
        e = fill_event(e, request.form)
        e.poster = save_poster(request.files.get("poster"))
        db.session.add(e)
        db.session.commit()
        flash(f"Event create Ho gaya! ID #{e.id}", "success")
        return redirect(url_for("admin.panel"))
    return render_template("create_event.html", e=None)

@admin_bp.route("/event/<int:eid>/edit", methods=["GET", "POST"])
@role_required("admin", "organizer")
def edit_event(eid):
    e = Event.query.get_or_404(eid)
    if request.method == "POST":
        e = fill_event(e, request.form)
        new_poster = save_poster(request.files.get("poster"))
        if new_poster:
            e.poster = new_poster
        db.session.commit()
        flash("Event update Ho gaya!", "success")
        return redirect(url_for("admin.view_event", eid=eid))
    return render_template("create_event.html", e=e)

@admin_bp.route("/event/<int:eid>/toggle")
@role_required("admin", "organizer")
def toggle_event(eid):
    e = Event.query.get_or_404(eid)
    e.status = "closed" if e.status == "open" else "open"
    db.session.commit()
    flash(f"Event {e.status} kar diya!", "info")
    return redirect(url_for("admin.panel"))

@admin_bp.route("/event/<int:eid>/delete", methods=["POST"])
@role_required("admin", "organizer")
def delete_event(eid):
    e = Event.query.get_or_404(eid)
    Registration.query.filter_by(event_id=eid).delete()
    db.session.delete(e)
    db.session.commit()
    flash("Event delete Ho gaya!", "warning")
    return redirect(url_for("admin.panel"))

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
