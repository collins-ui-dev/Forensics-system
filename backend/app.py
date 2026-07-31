from flask import Flask
from flask_pymongo import PyMongo
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from dotenv import load_dotenv
import os

load_dotenv()

from extensions import mongo, jwt

def create_app():
    app = Flask(__name__)

    # Config
    app.config["MONGO_URI"] = os.getenv("MONGO_URI", "mongodb+srv://students:students123%40@students.yrykxbu.mongodb.net/myproject")
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "dev-secret-key")
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES", 86400))
    app.config["UPLOAD_FOLDER"] = os.getenv("UPLOAD_FOLDER", "uploads")
    app.config["MAX_CONTENT_LENGTH"] = int(os.getenv("MAX_CONTENT_LENGTH", 52428800))

    # Ensure upload dirs exist
    os.makedirs(os.path.join(app.config["UPLOAD_FOLDER"], "evidence"), exist_ok=True)
    os.makedirs(os.path.join(app.config["UPLOAD_FOLDER"], "reports"), exist_ok=True)

    # Init extensions
    mongo.init_app(app)
    jwt.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

    # Register blueprints
    from routes.auth_routes import auth_bp
    from routes.case_routes import case_bp
    from routes.evidence_routes import evidence_bp
    from routes.report_routes import report_bp
    from routes.log_routes import log_bp
    from routes.dashboard_routes import dashboard_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(case_bp, url_prefix="/api/cases")
    app.register_blueprint(evidence_bp, url_prefix="/api/evidence")
    app.register_blueprint(report_bp, url_prefix="/api/reports")
    app.register_blueprint(log_bp, url_prefix="/api/logs")
    app.register_blueprint(dashboard_bp, url_prefix="/api/dashboard")

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5000)
