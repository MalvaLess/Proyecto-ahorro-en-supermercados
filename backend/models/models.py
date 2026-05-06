from flask_sql_alchemy import SQLAlchemy
db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "user"
    userId: Mapped[int] = mapped_column(primary_key=True)
    firstName: Mapped[str] = mapped_column(String(50))
    lastName: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(50), unique=True)
    passwordHash: Mapped[str] = mapped_column(String(255))
    isActive: Mapped[bool] = mapped_column()
    lastLoginAt: Mapped[datetime] = mapped_column()
    createdAt: Mapped[datetime] = mapped_column()
    updatedAt: Mapped[datetime] = mapped_column()

class StoreChain(db.Model):
    __tablename__ = "store_chain"
    storeChainId: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    isActive: Mapped[bool] = mapped_column()
    createdAt: Mapped[datetime] = mapped_column()
    updatedAt: Mapped[datetime] = mapped_column()

class Store(db.Model):
    __tablename__ = "store"
    storeId: Mapped[int] = mapped_column(primary_key=True)
    #storeChainId
    address: Mapped[str] = mapped_column(String(255))
    latitude: Mapped[float] = mapped_column(Numeric(precision=10, scale=7))
    longitude: Mapped[float] = mapped_column(Numeric(precision=10, scale=7))
    isActive: Mapped[bool] = mapped_column()
    createdAt: Mapped[datetime] = mapped_column()
    updatedAt: Mapped[datetime] = mapped_column()

class Brand(db.Model):
    __tablename__ = "brand"
    brandId: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    createdAt: Mapped[datetime] = mapped_column()
    updatedAt: Mapped[datetime] = mapped_column()

class Category(db.Model):
    __tablename__ = "category"
    categoryId: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    createdAt: Mapped[datetime] = mapped_column()
    updatedAt: Mapped[datetime] = mapped_column()

class Product(db.Model):
    __tablename__ = "product"
    productId: Mapped[int] = mapped_column(primary_key=True)
    #brandId
    name: Mapped[str] = mapped_column(String(50))
    normalizedName: Mapped[str] = mapped_column(String(50))
    ean: Mapped[str] = mapped_column(String(50))
    description: Mapped[str] = mapped_column(String(50))
    weightValue: Mapped[float] = mapped_column(Numeric(precision=10, scale=2))
    unit: Mapped[str] = mapped_column(String(5))
    format: Mapped[str] = mapped_column(String(50))
    imageURL: Mapped[str] = mapped_column(String(255))
    isActive: Mapped[bool] = mapped_column() 
    createdAt: Mapped[datetime] = mapped_column()
    updatedAt: Mapped[datetime] = mapped_column()


class ProductCategory(db.Model):
    __tablename__ = "product_category"
    productCategoryId: Mapped[int] = mapped_column(primary_key=True)
    #productId
    #categoryId

class StoreProduct(db.Model):
    __tablename__ = "store_product"
    storeProductId: Mapped[int] = mapped_column(primary_key=True)
    #storeId
    #productId
    externalSku: Mapped[str] = mapped_column(String(50))
    externalName: Mapped[str] = mapped_column(String(50))
    externalBrand: Mapped[str] = mapped_column(String(50))
    isAvailable: Mapped[bool] = mapped_column()
    createdAt: Mapped[datetime] = mapped_column()
    updatedAt: Mapped[datetime] = mapped_column()

class PriceSnapshot(db.Model):
    __tablename__ = "price_snapshot"
    priceSnapshotId: Mapped[int] = mapped_column(primary_key=True)
    #storeProductId
    price: Mapped[float] = mapped_column(Numeric(precision=10, scale=2))
    currency: Mapped[str] = mapped_column(String(50))
    capturedAt: Mapped[datetime] = mapped_column()
    createdAt: Mapped[datetime] = mapped_column()


class Favorite(db.Model):
    __tablename__ = "favorite"
    favoriteId: Mapped[int] = mapped_column(primary_key=True)
    #userId
    #productId
    createdAt: Mapped[datetime] = mapped_column()

class ShoppingList(db.Model):
    __tablename__ = "shopping_list"
    shoppingListId: Mapped[int] = mapped_column(primary_key=True)
    #userId
    name: mapped_column(String(50))
    subTotal: Mapped[float] = mapped_column(Numeric(precision=10, scale=2))
    total: Mapped[float] = mapped_column(Numeric(precision=10, scale=2))
    createdAt: Mapped[datetime] = mapped_column()
    updatedAt: Mapped[datetime] = mapped_column()

class ShoppingListItem(db.Model):
    __tablename__ = "shopping_list_item"
    shoppingListItemId:
    #shoppingListId
    #productId
    #selectedStoreProductId
    quantity: Mapped[int] = mapped_column()
    unitPrice: Mapped[float] = mapped_column(Numeric(precision=10, scale=2))
    totalPrice: Mapped[float] = mapped_column(Numeric(precision=10, scale=2))
    createdAt: Mapped[datetime] = mapped_column()
    updatedAt: Mapped[datetime] = mapped_column()