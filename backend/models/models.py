from flask_sql_alchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, Numeric, String, ForeignKey

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "user"
    userId: Mapped[int] = mapped_column(primary_key=True)
    firstName: Mapped[str] = mapped_column(String(50), nullable=False)
    lastName: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    passwordHash: Mapped[str] = mapped_column(String(255), nullable=False)
    isActive: Mapped[bool] = mapped_column(default=True)
    lastLoginAt: Mapped[datetime] = mapped_column()
    createdAt: Mapped[datetime] = mapped_column(server_default=func.now())
    updatedAt: Mapped[datetime] = mapped_column()

class StoreChain(db.Model):
    __tablename__ = "store_chain"
    storeChainId: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    isActive: Mapped[bool] = mapped_column(default=True)
    createdAt: Mapped[datetime] = mapped_column(server_default=func.now())
    updatedAt: Mapped[datetime] = mapped_column()

class Store(db.Model):
    __tablename__ = "store"
    storeId: Mapped[int] = mapped_column(primary_key=True)
    storeChainId: Mapped[int] = mapped_column(ForeignKey("store_chain.storeChainId"))
    address: Mapped[str] = mapped_column(String(255), nullable=False)
    latitude: Mapped[float] = mapped_column(Numeric(precision=10, scale=7), nullable=False)
    longitude: Mapped[float] = mapped_column(Numeric(precision=10, scale=7), nullable=False)
    isActive: Mapped[bool] = mapped_column(default=True)
    createdAt: Mapped[datetime] = mapped_column(server_default=func.now())
    updatedAt: Mapped[datetime] = mapped_column()

class Brand(db.Model):
    __tablename__ = "brand"
    brandId: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    createdAt: Mapped[datetime] = mapped_column(server_default=func.now())
    updatedAt: Mapped[datetime] = mapped_column()

class Category(db.Model):
    __tablename__ = "category"
    categoryId: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    createdAt: Mapped[datetime] = mapped_column(server_default=func.now())
    updatedAt: Mapped[datetime] = mapped_column()

class Product(db.Model):
    __tablename__ = "product"
    productId: Mapped[int] = mapped_column(primary_key=True)
    brandId: Mapped[int] = mapped_column(ForeignKey("brand.brandId"))
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    normalizedName: Mapped[str] = mapped_column(String(50), nullable=False)
    ean: Mapped[str] = mapped_column(String(50), nullable=True)
    description: Mapped[str] = mapped_column(String(50), nullable=True)
    weightValue: Mapped[float] = mapped_column(Numeric(precision=10, scale=2), nullable=True)
    unit: Mapped[str] = mapped_column(String(5), nullable=False)
    format: Mapped[str] = mapped_column(String(50), nullable=True)
    imageURL: Mapped[str] = mapped_column(String(255), nullable=True)
    isActive: Mapped[bool] = mapped_column(default=True)
    createdAt: Mapped[datetime] = mapped_column(server_default=func.now())
    updatedAt: Mapped[datetime] = mapped_column()


class ProductCategory(db.Model):
    __tablename__ = "product_category"
    productCategoryId: Mapped[int] = mapped_column(primary_key=True)
    productId: Mapped[int] = mapped_column(ForeignKey("product.productId"))
    categoryId: Mapped[int] = mapped_column(ForeignKey("category.categoryId"))

class StoreProduct(db.Model):
    __tablename__ = "store_product"
    storeProductId: Mapped[int] = mapped_column(primary_key=True)
    storeId: Mapped[int] = mapped_column(ForeignKey("store.storeId"))
    productId: Mapped[int] = mapped_column(ForeignKey("product.productId"))
    externalSku: Mapped[str] = mapped_column(String(50), nullable=True)
    externalName: Mapped[str] = mapped_column(String(50), nullable=True)
    externalBrand: Mapped[str] = mapped_column(String(50), nullable=True)
    isAvailable: Mapped[bool] = mapped_column(default=True)
    createdAt: Mapped[datetime] = mapped_column(server_default=func.now())
    updatedAt: Mapped[datetime] = mapped_column()

class PriceSnapshot(db.Model):
    __tablename__ = "price_snapshot"
    priceSnapshotId: Mapped[int] = mapped_column(primary_key=True)
    storeProductId: Mapped[int] = mapped_column(ForeignKey("store_product.storeProductId"))
    price: Mapped[float] = mapped_column(Numeric(precision=10, scale=2), nullable=False)
    currency: Mapped[str] = mapped_column(String(50), nullable=False)
    capturedAt: Mapped[datetime] = mapped_column()
    createdAt: Mapped[datetime] = mapped_column(server_default=func.now())

class Favorite(db.Model):
    __tablename__ = "favorite"
    favoriteId: Mapped[int] = mapped_column(primary_key=True)
    userId: Mapped[int] = mapped_column(ForeignKey("user.userId"))
    productId: Mapped[int] = mapped_column(ForeignKey("producto.productId"))
    createdAt: Mapped[datetime] = mapped_column()

class ShoppingList(db.Model):
    __tablename__ = "shopping_list"
    shoppingListId: Mapped[int] = mapped_column(primary_key=True)
    userId: Mapped[int] = mapped_column(ForeignKey("user.userId"))
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    subTotal: Mapped[float] = mapped_column(Numeric(precision=10, scale=2), nullable=False)
    total: Mapped[float] = mapped_column(Numeric(precision=10, scale=2), nullable=False)
    createdAt: Mapped[datetime] = mapped_column(server_default=func.now())
    updatedAt: Mapped[datetime] = mapped_column()

class ShoppingListItem(db.Model):
    __tablename__ = "shopping_list_item"
    shoppingListItemId: Mapped[int] = mapped_column(primary_key=True)
    shoppingListId: Mapped[int] = mapped_column(ForeignKey("shopping_list.shoppingListId"))
    productId: Mapped[int] = mapped_column(ForeignKey("product.producId"))
    selectedStoreProductId: Mapped[int] = mapped_column(ForeignKey("store_product.storeProductId"), nullable=True)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unitPrice: Mapped[float] = mapped_column(Numeric(precision=10, scale=2), nullable=False)
    totalPrice: Mapped[float] = mapped_column(Numeric(precision=10, scale=2), nullable=False)
    createdAt: Mapped[datetime] = mapped_column(server_default=func.now())
    updatedAt: Mapped[datetime] = mapped_column()