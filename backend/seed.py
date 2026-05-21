import sys
import os

sys.path.append(os.path.dirname(__file__))

from dotenv import load_dotenv

load_dotenv()

import csv
from app.app import app
from models.models import db, StoreChain, Store, Category
from datetime import datetime

# Mapa nombre CSV → nombre canónico en DB
CADENAS_NOMBRE_MAP = {
    "Ta - Ta": "Ta-Ta",
    "Disco": "Disco",
    "Devoto": "Devoto",
    "Tienda Inglesa": "Tienda Inglesa",
}
CADENAS_OBJETIVO = set(CADENAS_NOMBRE_MAP.keys())

CSV_PATH = os.path.join(os.path.dirname(__file__), "CKAN", "establecimiento.csv")


def seed():
    with app.app_context():
        cadenas_creadas = {}

        with open(CSV_PATH, encoding="latin-1") as f:
            reader = csv.DictReader(f, delimiter=";")
            for row in reader:
                cadena_nombre = row["cadena"].strip()

                if cadena_nombre not in CADENAS_OBJETIVO:
                    continue

                # Normalizar nombre CSV → nombre canónico
                nombre_canonico = CADENAS_NOMBRE_MAP[cadena_nombre]

                # Crear cadena si no existe
                if nombre_canonico not in cadenas_creadas:
                    cadena = StoreChain.query.filter_by(name=nombre_canonico).first()
                    if not cadena:
                        cadena = StoreChain(
                            name=nombre_canonico, isActive=True, updatedAt=datetime.now()
                        )
                        db.session.add(cadena)
                        db.session.flush()
                        print(f"Cadena creada: {nombre_canonico}")
                    cadenas_creadas[nombre_canonico] = cadena.storeChainId

                # Convertir coordenadas
                try:
                    lat = float(row["long"].replace(",", "."))
                    lon = float(row["lat"].replace(",", "."))
                    print(f"lat={lat}, lon={lon}")
                    # Validar que estén en rango válido para Uruguay
                    if not (-35.5 < lat < -30) or not (-58 < lon < -53):
                        continue
                except (ValueError, AttributeError):
                    print(
                        f"Coordenadas inválidas para {row['nombre.sucursal']}, saltando"
                    )
                    continue

                # Crear store si no existe
                external_id = int(row["id.establecimientos"])
                store = Store.query.filter_by(externalIdSipc=external_id).first()
                if not store:
                    store = Store(
                        storeChainId=cadenas_creadas[nombre_canonico],
                        address=row["direccion"].strip(),
                        latitude=lat,
                        longitude=lon,
                        isActive=True,
                        updatedAt=datetime.now(),
                        externalIdSipc=external_id,
                    )
                    db.session.add(store)
                    print(f"Store creada: {row['nombre.sucursal']}")

        db.session.commit()
        print("Seed completado")


CATEGORIAS_CANONICAS = ["Almacén", "Bebidas", "Frescos", "Limpieza", "Congelados"]


def seed_categories():
    with app.app_context():
        for nombre in CATEGORIAS_CANONICAS:
            if not Category.query.filter_by(name=nombre).first():
                db.session.add(Category(name=nombre, updatedAt=datetime.now()))
                print(f"Categoría creada: {nombre}")
        db.session.commit()
        print("Categorías seed completado")


if __name__ == "__main__":
    seed()
    seed_categories()
