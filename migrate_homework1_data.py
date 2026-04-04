#!/usr/bin/env python3
import os
import sqlite3

try:
    import mysql.connector
except ImportError:
    mysql = None
else:
    mysql = mysql.connector

try:
    import redis
except ImportError:
    redis = None

try:
    from pymongo import MongoClient
except ImportError:
    MongoClient = None


SOURCE = os.getenv("STOREAPP_MIGRATE_SOURCE", "sqlite").strip().lower()
SQLITE_PATH = os.getenv("STOREAPP_SQLITE_PATH", "store.db")
MYSQL_CONFIG = {
    "host": os.getenv("STOREAPP_DB_HOST", "localhost"),
    "port": int(os.getenv("STOREAPP_DB_PORT", "3306")),
    "database": os.getenv("STOREAPP_DB_NAME", "storeapp"),
    "user": os.getenv("STOREAPP_DB_USER", "root"),
    "password": os.getenv("STOREAPP_DB_PASSWORD", ""),
}
REDIS_CONFIG = {
    "host": os.getenv("STOREAPP_REDIS_HOST", "localhost"),
    "port": int(os.getenv("STOREAPP_REDIS_PORT", "6379")),
    "decode_responses": True,
    "username": os.getenv("STOREAPP_REDIS_USER") or None,
    "password": os.getenv("STOREAPP_REDIS_PASSWORD") or None,
    "db": int(os.getenv("STOREAPP_REDIS_DB", "0")),
}
MONGO_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
MONGO_DB = os.getenv("STOREAPP_MONGO_DB", "storeapp")
MONGO_COLLECTION = os.getenv("STOREAPP_MONGO_COLLECTION", "orders")


def source_connection():
    if SOURCE == "sqlite":
        conn = sqlite3.connect(SQLITE_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    if SOURCE == "mysql":
        if mysql is None:
            raise RuntimeError("Install mysql-connector-python to migrate from MySQL.")
        return mysql.connect(**MYSQL_CONFIG)
    raise RuntimeError("STOREAPP_MIGRATE_SOURCE must be sqlite or mysql.")


def redis_connection():
    if redis is None:
        raise RuntimeError("Install redis to migrate product data.")
    return redis.Redis(**REDIS_CONFIG)


def orders_collection():
    if MongoClient is None:
        raise RuntimeError("Install pymongo to migrate order data.")
    return MongoClient(MONGO_URI)[MONGO_DB][MONGO_COLLECTION]


def fetch_all(conn, query):
    cursor = conn.cursor(dictionary=True) if SOURCE == "mysql" else conn.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    cursor.close()
    if SOURCE == "mysql":
        return rows
    return [dict(row) for row in rows]


def migrate_products(conn):
    products = fetch_all(conn, "SELECT ProductID, Name, Price, Quantity, SellerID FROM Products")
    r = redis_connection()
    for product in products:
        r.hset(
            f"product:{int(product['ProductID'])}",
            mapping={
                "ProductID": int(product["ProductID"]),
                "ProductName": product["Name"],
                "Price": float(product["Price"]),
                "Quantity": float(product["Quantity"]),
                "SellerID": int(product["SellerID"] or 0),
            },
        )
    print(f"Migrated {len(products)} products to Redis.")


def migrate_orders(conn):
    orders = fetch_all(conn, "SELECT OrderID, OrderDate, CustomerID, TotalCost, TotalTax FROM Orders")
    lines = fetch_all(conn, "SELECT OrderID, ProductID, Quantity, Cost FROM OrderLine")
    details_by_order = {}
    for line in lines:
        details_by_order.setdefault(int(line["OrderID"]), []).append(
            {
                "ProductID": int(line["ProductID"]),
                "Quantity": float(line["Quantity"]),
                "Cost": float(line["Cost"]),
            }
        )

    collection = orders_collection()
    for order in orders:
        doc = {
            "OrderID": int(order["OrderID"]),
            "UserID": int(order["CustomerID"] or 0),
            "OrderDate": str(order["OrderDate"]),
            "TotalCost": float(order["TotalCost"] or 0.0),
            "TotalTax": float(order["TotalTax"] or 0.0),
            "Details": details_by_order.get(int(order["OrderID"]), []),
        }
        collection.replace_one({"OrderID": doc["OrderID"]}, doc, upsert=True)
    print(f"Migrated {len(orders)} orders to MongoDB.")


if __name__ == "__main__":
    with source_connection() as connection:
        migrate_products(connection)
        migrate_orders(connection)
