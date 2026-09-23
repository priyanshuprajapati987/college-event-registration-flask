# Flask boilerplate - full code next step me aayega
# Samajh gaya! Run: pip install -r requirements.txt; python run.py
from app import create_app
app = create_app()
if __name__ == "__main__":
    app.run(debug=True)
