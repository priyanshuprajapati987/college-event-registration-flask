# College Event Registration System (Flask)
College Tech/Cultural/Sports events ke liye online registration + QR ticket + certificate system.

## Quick Start
```bash
pip install -r requirements.txt
python run.py
# open http://127.0.0.1:5000
```

## Structure
- `app/models/` -> user, event, registration
- `app/routes/` -> auth, events, admin, api
- `app/utils/` -> qr, certificate, mail
- Full doc: `../College_Event_Registration_System_Plan_and_Document.md`
- PDF: `../College_Event_Registration_System_Document.pdf`

## GitHub Push (jab bole)
```bash
git init; git add .; git commit -m "feat: initial flask boilerplate"
gh repo create college-event-registration-flask --public --source=. --push
```

## Roles
student | organizer | admin
