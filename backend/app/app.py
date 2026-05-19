import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()

from flask import Flask, jsonify
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from routes.health_routes import health_bp
from routes.user_routes import user_bp
from routes.auth_routes import auth_bp
from routes.brand_routes import brand_bp
from routes.category_routes import category_bp
from routes.product_routes import product_bp
from routes.store_chain_routes import store_chain_bp
from routes.store_routes import store_bp
from routes.store_product_routes import store_product_bp
from models.models import db

app = Flask(__name__)

app.config["DEBUG"] = True
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=int(os.getenv("JWT_TIME_DELTA")))

db.init_app(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)

app.register_blueprint(health_bp, url_prefix="/api/check")
app.register_blueprint(user_bp, url_prefix="/api/users")
app.register_blueprint(auth_bp, url_prefix="/api/auth")
app.register_blueprint(brand_bp, url_prefix="/api/brands")
app.register_blueprint(category_bp, url_prefix="/api/categories")
app.register_blueprint(product_bp, url_prefix="/api/products")
app.register_blueprint(store_chain_bp, url_prefix="/api/store-chain")
app.register_blueprint(store_bp, url_prefix="/api/stores")
app.register_blueprint(store_product_bp, url_prefix="/api/stores-products")

@app.route("/")
def main():
    return jsonify({"status": "connected to postgres"}), 200

if __name__ == "__main__":
    app.run()