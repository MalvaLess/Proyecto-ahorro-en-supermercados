import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
from datetime import timedelta
from flask_cors import CORS

load_dotenv()

from flask import Flask, jsonify
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from extensions import mail
from routes.health_routes import health_bp
from routes.user_routes import user_bp
from routes.auth_routes import auth_bp
from routes.brand_routes import brand_bp
from routes.category_routes import category_bp
from routes.product_routes import product_bp
from routes.store_chain_routes import store_chain_bp
from routes.store_routes import store_bp
from routes.store_product_routes import store_product_bp
from routes.price_snapshot_routes import price_snapshot_bp
from routes.price_comparison_routes import price_comparison_bp
from routes.shopping_list_routes import shopping_list_bp
from routes.shopping_list_item_routes import shopping_list_item_bp
from routes.favorite_routes import favorite_bp
from routes.offer_routes import offer_bp
from routes.offer_schedule_routes import offer_schedule_bp

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from models.models import db

app = Flask(__name__)
CORS(
    app,
    resources={
        r"/api/*": {
            "origins": [
                "*"
            ],
            "methods": ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    }
)

app.config["DEBUG"] = False
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_pre_ping": True,
    "pool_recycle": 300,
}

app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=int(os.getenv("JWT_TIME_DELTA")))

app.config["MAIL_SERVER"] = os.getenv("MAIL_SERVER", "smtp.gmail.com")
app.config["MAIL_PORT"] = int(os.getenv("MAIL_PORT", 587))
app.config["MAIL_USE_TLS"] = os.getenv("MAIL_USE_TLS", "true").lower() == "true"
app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")
app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")
app.config["MAIL_DEFAULT_SENDER"] = os.getenv("MAIL_DEFAULT_SENDER")
app.config["FRONTEND_URL"] = os.getenv("FRONTEND_URL", "http://localhost:5173")
app.config["GOOGLE_CLIENT_ID"] = os.getenv("GOOGLE_CLIENT_ID")

db.init_app(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)
mail.init_app(app)

app.register_blueprint(health_bp, url_prefix="/api/check")
app.register_blueprint(user_bp, url_prefix="/api")
app.register_blueprint(auth_bp, url_prefix="/api/auth")
app.register_blueprint(brand_bp, url_prefix="/api/brands")
app.register_blueprint(category_bp, url_prefix="/api/categories")
app.register_blueprint(product_bp, url_prefix="/api")
app.register_blueprint(store_chain_bp, url_prefix="/api/store-chain")
app.register_blueprint(store_bp, url_prefix="/api/stores")
app.register_blueprint(store_product_bp, url_prefix="/api/store-products")
app.register_blueprint(price_snapshot_bp, url_prefix="/api/price-snapshots")
app.register_blueprint(price_comparison_bp, url_prefix="/api/price-comparison")
app.register_blueprint(shopping_list_bp, url_prefix="/api/shopping-lists")
app.register_blueprint(shopping_list_item_bp, url_prefix="/api/shopping-lists")
app.register_blueprint(favorite_bp, url_prefix="/api/favorites")
app.register_blueprint(offer_bp, url_prefix="/api/offers")
app.register_blueprint(offer_schedule_bp, url_prefix="/api/offer-schedules")

@app.route("/")
def main():
    return jsonify({"status": "connected to postgres"}), 200

if __name__ == "__main__":
    app.run()