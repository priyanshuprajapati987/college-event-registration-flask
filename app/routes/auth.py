from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from ..models import db
from ..models.user import User

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        pwd = request.form.get("password", "")
        role = request.form.get("role", "student")
        if not name or not email or not pwd:
            flash("Sab fields bharo bro!", "danger")
            return redirect(url_for("auth.register"))
        if User.query.filter_by(email=email).first():
            flash("Email already registered!", "warning")
            return redirect(url_for("auth.login"))
        u = User(name=name, email=email, role=role,
                 roll_no=request.form.get("roll_no", ""),
                 branch=request.form.get("branch", ""),
                 year=request.form.get("year", ""))
        u.set_password(pwd)
        db.session.add(u)
        db.session.commit()
        flash("Ho gaya! Ab login karo.", "success")
        return redirect(url_for("auth.login"))
    return render_template("register.html")

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        pwd = request.form.get("password", "")
        u = User.query.filter_by(email=email).first()
        if u and u.check_password(pwd):
            login_user(u)
            return redirect(url_for("events.index"))
        flash("Email/password galat!", "danger")
    return render_template("login.html")

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("events.index"))
