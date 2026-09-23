from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
from flask_login import login_required, current_user
from functools import wraps
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
        e = Event(
            title=request.form.get("title"),
            description=request.form.get("description", ""),
            category=request.form.get("category", "tech"),
            date=request.form.get("date", ""),
            venue=request.form.get("venue", "Main Auditorium"),
            capacity=int(request.form.get("capacity", 100)),
            fee=float(request.form.get("fee", 0)),
            deadline=request.form.get("deadline", ""),
            organizer_id=current_user.id,
        )
        db.session.add(e)
        db.session.commit()
        flash("Event create Ho gaya!", "success")
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
    r = Registration.query.filter_by(qr_token=qr_token).first_or_404()
    r.attended = True
    r.status = "approved"
    db.session.commit()
    flash(f"Check-in done! Reg #{r.id}", "success")
    return redirect(url_for("admin.view_event", eid=r.event_id))

@admin_bp.route("/event/<int:eid>/export")
@role_required("admin", "organizer")
def export(eid):
    from ..utils.excel_export import export_csv
    path = export_csv(eid)
    return send_file(path, as_attachment=True)
