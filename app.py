from flask import Flask, send_from_directory
from backend.config.db_config import db, init_db
from backend.auth.auth_routes import auth_bp
from backend.api.analyze_routes import analyze_bp
from backend.petitions.petition_routes import petition_bp
from backend.admin.admin_routes import admin_bp
from backend.dashboard.dashboard_routes import dashboard_bp

import os
from flask_jwt_extended import JWTManager

app = Flask(__name__)
init_db(app)

# JWT configuration
app.config["JWT_SECRET_KEY"] = "super-secret-key"  # change to a strong key
app.config["JWT_TOKEN_LOCATION"] = ["headers"]
jwt = JWTManager(app)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(BASE_DIR, "web_frontend")

# Register Blueprints
app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(analyze_bp)
app.register_blueprint(petition_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(dashboard_bp)



@app.route("/")
def serve_index():
    return send_from_directory(FRONTEND_DIR, "index.html")

@app.route("/<path:path>")
def serve_static(path):
    return send_from_directory(FRONTEND_DIR, path)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    print("🚀 Petition System Backend Running")
    app.run(debug=True)
