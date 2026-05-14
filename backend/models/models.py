from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from decimal import Decimal
from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, Numeric, String, ForeignKey
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"
    userId: Mapped[int] = mapped_column(primary_key=True)
    firstName: Mapped[str] = mapped_column(String(50), nullable=False)
    lastName: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    passwordHash: Mapped[str] = mapped_column(String(255), nullable=False)
    isActive: Mapped[bool] = mapped_column(default=True)
    lastLoginAt: Mapped[datetime | None] = mapped_column(nullable=True)
    createdAt: Mapped[datetime] = mapped_column(server_default=func.now())
    updatedAt: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now()
    )

    favorites: Mapped[list["Favorite"]] = relationship(
        "Favorite", back_populates="user"
    )

    shoppingList: Mapped[list["ShoppingList"]] = relationship(
        "ShoppingList", back_populates="user"
    )

    def set_password(self, password: str):
        self.passwordHash = generate_password_hash(password)

    def check_password(self, password: str):
        return check_password_hash(self.passwordHash, password)
    
    def deactivate(self):
        self.isActive = False

    def to_dict(self):
        return {
            "userId": self.userId,
            "firstName": self.firstName,
            "lastName": self.lastName,
            "email": self.email,
            "isActive": self.isActive,
            "lastLoginAt": self.lastLoginAt.isoformat() if self.lastLoginAt else None,
            "createdAt": self.createdAt.isoformat() if self.createdAt else None,
            "updatedAt": self.updatedAt.isoformat() if self.updatedAt else None
        }


class StoreChain(db.Model):
    __tablename__ = "store_chain"
    storeChainId: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    isActive: Mapped[bool] = mapped_column(default=True)
    createdAt: Mapped[datetime] = mapped_column(server_default=func.now())
    updatedAt: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now()
    )

    stores: Mapped[list["Store"]] = relationship("Store", back_populates="chain")

    def to_dict(self):
        return {
            "storeChainId": self.storeChainId,
            "name": self.name,
            "isActive": self.isActive,
            "createdAt": self.createdAt.isoformat() if self.createdAt else None,
            "updatedAt": self.updatedAt.isoformat() if self.updatedAt else None
        }


class Store(db.Model):
    __tablename__ = "store"
    storeId: Mapped[int] = mapped_column(primary_key=True)
    storeChainId: Mapped[int] = mapped_column(ForeignKey("store_chain.storeChainId"))
    externalIdSipc: Mapped[int | None] = mapped_column(
        Integer, nullable=True
    )  # id.establecimientos en CKAN
    address: Mapped[str] = mapped_column(String(255), nullable=False)
    latitude: Mapped[float] = mapped_column(
        Numeric(precision=10, scale=7), nullable=False
    )
    longitude: Mapped[float] = mapped_column(
        Numeric(precision=10, scale=7), nullable=False
    )
    isActive: Mapped[bool] = mapped_column(default=True)
    createdAt: Mapped[datetime] = mapped_column(server_default=func.now())
    updatedAt: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now()
    )

    chain: Mapped["StoreChain"] = relationship("StoreChain", back_populates="stores")

    storeProducts: Mapped[list["StoreProduct"]] = relationship(
        "StoreProduct", back_populates="store"
    )

    def to_dict(self):
        return {
            "storeId": self.storeId,
            "storeChainId": self.storeChainId,
            "chain": {
                "storeChainId": self.chain.storeChainId,
                "name": self.chain.name
            } if self.chain else None,
            "address": self.address,
            "latitude": float(self.latitude) if self.latitude is not None else None,
            "longitude": float(self.longitude) if self.longitude is not None else None,
            "isActive": self.isActive,
            "createdAt": self.createdAt.isoformat() if self.createdAt else None,
            "updatedAt": self.updatedAt.isoformat() if self.updatedAt else None
        }


class Brand(db.Model):
    __tablename__ = "brand"
    brandId: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    createdAt: Mapped[datetime] = mapped_column(server_default=func.now())
    updatedAt: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now()
    )

    products: Mapped[list["Product"]] = relationship("Product", back_populates="brand")

    def to_dict(self):
        return {
            "brandId": self.brandId,
            "name": self.name,
            "createdAt": self.createdAt.isoformat() if self.createdAt else None,
            "updateAt": self.updatedAt.isoformat() if self.updatedAt else None
        }


class Category(db.Model):
    __tablename__ = "category"

    categoryId: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    createdAt: Mapped[datetime] = mapped_column(server_default=func.now())
    updatedAt: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now()
    )

    productCategories: Mapped[list["ProductCategory"]] = relationship(
        "ProductCategory", back_populates="category"
    )

    def to_dict(self):
        return {
            "categoryId": self.categoryId,
            "name": self.name,
            "createdAt": self.createdAt.isoformat() if self.createdAt else None,
            "updateAt": self.updatedAt.isoformat() if self.updatedAt else None
        }

class Product(db.Model):
    __tablename__ = "product"
    productId: Mapped[int] = mapped_column(primary_key=True)
    brandId: Mapped[int] = mapped_column(ForeignKey("brand.brandId"))
    externalIdCkan: Mapped[int | None] = mapped_column(
        Integer, nullable=True
    )  # id.producto en CKAN
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    normalizedName: Mapped[str] = mapped_column(String(50), nullable=False)
    ean: Mapped[str] = mapped_column(String(50), nullable=True)
    description: Mapped[str] = mapped_column(String(50), nullable=True)
    weightValue: Mapped[float] = mapped_column(
        Numeric(precision=10, scale=2), nullable=True
    )
    unit: Mapped[str] = mapped_column(String(5), nullable=False)
    format: Mapped[str] = mapped_column(String(50), nullable=True)
    imageURL: Mapped[str] = mapped_column(String(255), nullable=True)
    isActive: Mapped[bool] = mapped_column(default=True)
    createdAt: Mapped[datetime] = mapped_column(server_default=func.now())
    updatedAt: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now()
    )

    brand: Mapped["Brand"] = relationship("Brand", back_populates="products")

    categories: Mapped[list["ProductCategory"]] = relationship(
        "ProductCategory", back_populates="product"
    )

    stores: Mapped[list["StoreProduct"]] = relationship(
        "StoreProduct", back_populates="product"
    )

    favorites: Mapped[list["Favorite"]] = relationship(
        "Favorite", back_populates="product"
    )

    shoppingListItems: Mapped[list["ShoppingListItem"]] = relationship(
        "ShoppingListItem", back_populates="product"
    )

    def to_dict(self):
        return {
            "productId": self.productId,
            "brandId": self.brandId,
            "brand": {
                "brandId": self.brand.brandId,
                "name": self.brand.name
            } if self.brand else None,
            "externalIdCkan": self.externalIdCkan,
            "name": self.name,
            "normalizedName": self.normalizedName,
            "ean": self.ean,
            "description": self.description,
            "weightValue": float(self.weightValue) if self.weightValue is not None else None,
            "unit": self.unit,
            "format": self.format,
            "imageURL": self.imageURL,
            "isActive": self.isActive,
            "categories": [
                {
                    "categoryId": product_category.category.categoryId,
                    "name": product_category.category.name
                }
                for product_category in self.categories
                if product_category.category is not None
            ],
            "createdAt": self.createdAt.isoformat() if self.createdAt else None,
            "updatedAt": self.updatedAt.isoformat() if self.updatedAt else None
        }


class ProductCategory(db.Model):
    __tablename__ = "product_category"
    productCategoryId: Mapped[int] = mapped_column(primary_key=True)
    productId: Mapped[int] = mapped_column(ForeignKey("product.productId"))
    categoryId: Mapped[int] = mapped_column(ForeignKey("category.categoryId"))

    product: Mapped["Product"] = relationship("Product", back_populates="categories")

    category: Mapped["Category"] = relationship(
        "Category", back_populates="productCategories"
    )

    __table_args__ = (
        db.UniqueConstraint("productId", "categoryId", name="uq_product_category"),
    )

    def to_dict(self):
        return {
            "productCategoryId": self.productCategoryId,
            "productId": self.productId,
            "categoryId": self.categoryId,
            "category": {
                "categoryId": self.category.categoryId,
                "name": self.category.name
            } if self.category else None
        }


class StoreProduct(db.Model):
    __tablename__ = "store_product"
    storeProductId: Mapped[int] = mapped_column(primary_key=True)
    storeId: Mapped[int] = mapped_column(ForeignKey("store.storeId"))
    productId: Mapped[int] = mapped_column(ForeignKey("product.productId"))
    externalSku: Mapped[str] = mapped_column(String(50), nullable=True)
    externalName: Mapped[str] = mapped_column(
        String(255), nullable=True
    )  # Se agregó capacidad al string para que no se corte el nombre del producto
    externalBrand: Mapped[str] = mapped_column(String(50), nullable=True)
    isAvailable: Mapped[bool] = mapped_column(default=True)
    createdAt: Mapped[datetime] = mapped_column(server_default=func.now())
    updatedAt: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now()
    )

    prices: Mapped[list["PriceSnapshot"]] = relationship(
        "PriceSnapshot", back_populates="storeProduct"
    )

    product: Mapped["Product"] = relationship("Product", back_populates="stores")

    store: Mapped["Store"] = relationship("Store", back_populates="storeProducts")

    shoppingListItems: Mapped[list["ShoppingListItem"]] = relationship(
        "ShoppingListItem", back_populates="selectedStoreProduct"
    )

    offers: Mapped[list["Offer"]] = relationship(
        "Offer",
        back_populates="storeProduct"
    )

    __table_args__ = (
        db.UniqueConstraint("storeId", "productId", name="uq_store_product"),
    )


class PriceSnapshot(db.Model):
    __tablename__ = "price_snapshot"
    priceSnapshotId: Mapped[int] = mapped_column(primary_key=True)
    storeProductId: Mapped[int] = mapped_column(
        ForeignKey("store_product.storeProductId")
    )
    price: Mapped[Decimal] = mapped_column(
        Numeric(precision=10, scale=2), nullable=False
    )
    currency: Mapped[str] = mapped_column(String(50), nullable=False)
    capturedAt: Mapped[datetime] = mapped_column()
    createdAt: Mapped[datetime] = mapped_column(server_default=func.now())
    source: Mapped[str] = mapped_column(
        String(10), nullable=False, default="SCRAPER"
    )  # Se agregó el source para poder identificar el origen del precio si Scraper o CKAN

    storeProduct: Mapped["StoreProduct"] = relationship(
        "StoreProduct", back_populates="prices"
    )


class Offer(db.Model):
    __tablename__ = "offer"
    offerId: Mapped[int] = mapped_column(primary_key= True)
    storeProductId: Mapped[int] = mapped_column(
        ForeignKey("store_product.storeProductId"),
        nullable=False
    )
    offerType: Mapped[str] = mapped_column(String(15), nullable=False)
    offerPrice: Mapped[Decimal | None] = mapped_column(
        Numeric(precision=10, scale=2), 
        nullable=True, 
        default=0
    )
    currency: Mapped[str] = mapped_column(String(10), nullable=True)
    isActive: Mapped[bool] = mapped_column(default=True)
    createdAt: Mapped[datetime] = mapped_column(server_default=func.now())
    updatedAt: Mapped[datetime] = mapped_column(
        server_default=func.now(), 
        onupdate=func.now()
    )

    storeProduct: Mapped["StoreProduct"] = relationship(
        "StoreProduct",
        back_populates="offers"
    )

    schedules: Mapped[list["OfferSchedule"]] = relationship(
        "OfferSchedule",
        back_populates="offer"
    )

class OfferSchedule(db.Model):
    __tablename__ = "offer_schedule"
    offerScheduleId: Mapped[int] = mapped_column(primary_key= True)
    offerId: Mapped[int] = mapped_column(
        ForeignKey("offer.offerId")
    )
    dayOfWeek: Mapped[int] = mapped_column(Integer, nullable=False)

    createdAt: Mapped[datetime] = mapped_column(server_default=func.now())

    offer: Mapped["Offer"] = relationship(
        "Offer",
        back_populates="schedules"
    )

class Favorite(db.Model):
    __tablename__ = "favorite"
    favoriteId: Mapped[int] = mapped_column(primary_key=True)
    userId: Mapped[int] = mapped_column(ForeignKey("users.userId"))
    productId: Mapped[int] = mapped_column(ForeignKey("product.productId"))
    createdAt: Mapped[datetime] = mapped_column(server_default=func.now())
    user: Mapped["User"] = relationship("User", back_populates="favorites")
    product: Mapped["Product"] = relationship("Product", back_populates="favorites")
    __table_args__ = (
        db.UniqueConstraint("userId", "productId", name="uq_user_product_favorite"),
    )


class ShoppingList(db.Model):
    __tablename__ = "shopping_list"
    shoppingListId: Mapped[int] = mapped_column(primary_key=True)
    userId: Mapped[int] = mapped_column(ForeignKey("users.userId"))
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    subTotal: Mapped[Decimal] = mapped_column(
        Numeric(precision=10, scale=2), nullable=False, default=0
    )
    total: Mapped[Decimal] = mapped_column(
        Numeric(precision=10, scale=2), nullable=False, default=0
    )
    createdAt: Mapped[datetime] = mapped_column(server_default=func.now())
    updatedAt: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now()
    )

    user: Mapped["User"] = relationship("User", back_populates="shoppingList")

    items: Mapped[list["ShoppingListItem"]] = relationship(
        "ShoppingListItem", back_populates="shoppingList"
    )


class ShoppingListItem(db.Model):
    __tablename__ = "shopping_list_item"
    shoppingListItemId: Mapped[int] = mapped_column(primary_key=True)
    shoppingListId: Mapped[int] = mapped_column(
        ForeignKey("shopping_list.shoppingListId")
    )
    productId: Mapped[int] = mapped_column(
        ForeignKey("product.productId"), nullable=False
    )
    selectedStoreProductId: Mapped[int] = mapped_column(
        ForeignKey("store_product.storeProductId"), nullable=True
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    unitPrice: Mapped[Decimal] = mapped_column(
        Numeric(precision=10, scale=2), nullable=False, default=0
    )
    totalPrice: Mapped[Decimal] = mapped_column(
        Numeric(precision=10, scale=2), nullable=False, default=0
    )
    createdAt: Mapped[datetime] = mapped_column(server_default=func.now())
    updatedAt: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now()
    )

    shoppingList: Mapped["ShoppingList"] = relationship(
        "ShoppingList", back_populates="items"
    )

    product: Mapped["Product"] = relationship(
        "Product", back_populates="shoppingListItems"
    )

    selectedStoreProduct: Mapped["StoreProduct"] = relationship(
        "StoreProduct", back_populates="shoppingListItems"
    )
