"""
Populates brand.normalizedName for existing records and merges duplicates.
Run once after migration: pipenv run python merge_brands.py
"""
import sys
import os

sys.path.append(os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv()

from app.app import app
from models.models import db, Brand, Product
from utils import normalize_brand


def merge_brands():
    with app.app_context():
        brands = Brand.query.all()

        # Map normalizedName -> canonical brand (first one found = canonical)
        canonical = {}
        duplicates = []

        for brand in brands:
            key = normalize_brand(brand.name)
            if key not in canonical:
                canonical[key] = brand
                brand.normalizedName = key
            else:
                duplicates.append((brand, canonical[key]))

        db.session.flush()

        # Reassign products from duplicates to canonical, then delete duplicate
        for dup, canon in duplicates:
            print(f"Merging brand '{dup.name}' (id={dup.brandId}) -> '{canon.name}' (id={canon.brandId})")
            Product.query.filter_by(brandId=dup.brandId).update({"brandId": canon.brandId})
            db.session.delete(dup)

        db.session.commit()
        print(f"Done. {len(canonical)} unique brands, {len(duplicates)} merged.")


if __name__ == "__main__":
    merge_brands()
