import os
from flask import Flask, request
from flask_cors import CORS
from src.firebase.client import ensure_firebase
from src.auth.security import authenticate_request
from src.http.responses import register_error_handlers
from src.http.routes_auth import users_bp
from src.http.routes_catalogs import catalogs_bp
from src.http.routes_health import health_bp
from src.http.routes_schedules import schedules_bp
from src.http.routes_ai import ai_bp

def create_app(testing: bool = False) -> Flask:
    app = Flask(__name__)
    app.config.update(TESTING=testing, MAX_CONTENT_LENGTH=256 * 1024)
    register_error_handlers(app)
    allowed = [o.strip() for o in os.getenv('CORS_ORIGINS', 'http://localhost:3000,http://127.0.0.1:3000').split(',') if o.strip()]
    CORS(app, origins=allowed, allow_headers=['Authorization', 'Content-Type'], methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS'])
    if not testing:
        ensure_firebase()
        app.before_request(authenticate_request)
    app.register_blueprint(health_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(catalogs_bp)
    app.register_blueprint(schedules_bp)
    app.register_blueprint(ai_bp)
    return app
