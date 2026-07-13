from flask import Flask
from flask_cors import CORS
from models import db
from routes import api
import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv not installed, use system env vars

def create_app():
    app = Flask(__name__)
    
    # Security
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-fallback-key-change-in-production')
    
    # Database
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    default_db = f"sqlite:///{os.path.join(BASE_DIR, 'database.db')}"
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', default_db)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # CORS - restrict origins in production
    allowed_origins = os.environ.get('ALLOWED_ORIGINS', '*')
    if allowed_origins != '*':
        origins = [o.strip() for o in allowed_origins.split(',')]
        CORS(app, origins=origins)
    else:
        CORS(app)
    
    db.init_app(app)
    app.register_blueprint(api, url_prefix='/api')
    
    with app.app_context():
        db.create_all()
        
    return app

if __name__ == '__main__':
    app = create_app()
    debug = os.environ.get('DEBUG', 'False').lower() in ('true', '1', 'yes')
    port = int(os.environ.get('PORT', 5000))
    
    if debug:
        print("Starting AI-Based Smart Bank Appointment Backend (Development)...")
        app.run(debug=True, port=port)
    else:
        print("Starting AI-Based Smart Bank Appointment Backend (Production)...")
        try:
            from waitress import serve
            print(f"Serving with Waitress on http://0.0.0.0:{port}")
            serve(app, host='0.0.0.0', port=port)
        except ImportError:
            print("Waitress not installed, falling back to Flask dev server.")
            print("Install waitress for production: pip install waitress")
            app.run(debug=False, host='0.0.0.0', port=port)
