import os
def make_qr(token):
    """QR image banao static/qr/<token>.png"""
    import qrcode
    base = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "qr")
    os.makedirs(base, exist_ok=True)
    path = os.path.join(base, f"{token}.png")
    img = qrcode.make(f"CHECKIN:{token}")
    img.save(path)
    return path

def send_mail_safe(to, sub, body):
    # Try real SMTP, fallback console - Bilkul!
    import os, smtplib
    from email.mime.text import MIMEText
    user, pwd = os.environ.get("MAIL_USERNAME", ""), os.environ.get("MAIL_PASSWORD", "")
    if not user or not pwd:
        print(f"[MAIL to={to}] {sub}: {body}")
        return True
    try:
        msg = MIMEText(body)
        msg["Subject"], msg["From"], msg["To"] = sub, user, to
        with smtplib.SMTP("smtp.gmail.com", 587, timeout=10) as s:
            s.starttls(); s.login(user, pwd); s.send_message(msg)
        return True
    except Exception as ex:
        print("mail err:", ex, f"[fallback MAIL to={to}] {sub}")
        return True

def export_csv(event_id):
    """Excel/CSV export - pandas nahi to csv fallback"""
    import csv
    base = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
    path = os.path.join(base, f"event_{event_id}.csv")
    try:
        from ..models.registration import Registration
        from ..models.user import User
        regs = Registration.query.filter_by(event_id=event_id).all()
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["reg_id", "name", "email", "roll", "team", "status", "attended"])
            for r in regs:
                u = User.query.get(r.user_id)
                w.writerow([r.id, u.name if u else "", u.email if u else "",
                            u.roll_no if u else "", r.team, r.status, r.attended])
    except Exception as ex:
        print("export err", ex)
    return path
