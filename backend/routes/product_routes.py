from flask import Blueprint, jsonify 
from models.models import Product

product_bp = Blueprint("products", __name__)

@product_bp.route("/", methods=["GET"])
def get_products():
    products = Product.query.all()

    result = []

    for product in products:
        result.append({
            
        })