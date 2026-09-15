from flask import Flask
from flask_cors import CORS
from config import Config
from db import init_db
from routes.dashboard import dashboard_bp
from routes.api_interests import interests_bp
from routes.api_settings import settings_bp
from routes.api_naver_auth import auth_bp
from routes.api_publish import publish_bp

def create_app():
    """Create and configure Flask app"""
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize database
    init_db()

    # Enable CORS
    CORS(app)

    # Register blueprints
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(interests_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(publish_bp)

    # Initialize scheduler (M7)
    try:
        from services.scheduler_service import init_scheduler
        init_scheduler(app)
    except Exception as e:
        print(f"Warning: Scheduler initialization failed: {e}")

    print(f"Flask app created on {Config.FLASK_HOST}:{Config.FLASK_PORT}")
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(
        host=Config.FLASK_HOST,
        port=Config.FLASK_PORT,
        debug=(Config.FLASK_ENV == "development")
    )
