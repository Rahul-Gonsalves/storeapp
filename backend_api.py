#!/usr/bin/env python3
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

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
    from pymongo import DESCENDING, MongoClient
except ImportError:
    DESCENDING = -1
    MongoClient = None


HOST = os.getenv("STOREAPP_API_HOST", "127.0.0.1")
PORT = int(os.getenv("STOREAPP_API_PORT", "9000"))

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


def mysql_connection():
    if mysql is None:
        raise RuntimeError("Install mysql-connector-python to use the user service.")
    return mysql.connect(**MYSQL_CONFIG)


def redis_connection():
    if redis is None:
        raise RuntimeError("Install redis to use the product service.")
    return redis.Redis(**REDIS_CONFIG)


def order_collection():
    if MongoClient is None:
        raise RuntimeError("Install pymongo to use the order service.")
    return MongoClient(MONGO_URI)[MONGO_DB][MONGO_COLLECTION]


def get_user_by_id(user_id):
    with mysql_connection() as conn:
        cur = conn.cursor(dictionary=True)
        cur.execute(
            "SELECT UserID, UserName, Password, DisplayName FROM Users WHERE UserID = %s",
            (user_id,),
        )
        row = cur.fetchone()
        cur.close()
        return row


def get_user_by_credentials(username, password):
    with mysql_connection() as conn:
        cur = conn.cursor(dictionary=True)
        cur.execute(
            "SELECT UserID, UserName, Password, DisplayName FROM Users WHERE UserName = %s AND Password = %s",
            (username, password),
        )
        row = cur.fetchone()
        cur.close()
        return row


def get_product(product_id):
    data = redis_connection().hgetall(f"product:{product_id}")
    if not data:
        return None
    return {
        "ProductID": int(data["ProductID"]),
        "ProductName": data["ProductName"],
        "Price": float(data["Price"]),
        "Quantity": float(data["Quantity"]),
        "SellerID": int(data.get("SellerID", 0)),
    }


def save_product(product_id, payload):
    if payload.get("ProductID") not in (None, product_id):
        raise ValueError("ProductID in URL and JSON body must match.")
    product = {
        "ProductID": product_id,
        "ProductName": str(payload["ProductName"]),
        "Price": float(payload["Price"]),
        "Quantity": float(payload["Quantity"]),
        "SellerID": int(payload.get("SellerID", 0)),
    }
    redis_connection().hset(f"product:{product_id}", mapping=product)
    return product


def get_order(order_id):
    doc = order_collection().find_one({"OrderID": order_id}, {"_id": 0})
    return None if doc is None else doc


def save_order(order_id, payload):
    if payload.get("OrderID") not in (None, order_id):
        raise ValueError("OrderID in URL and JSON body must match.")
    order = {
        "OrderID": order_id,
        "UserID": int(payload["UserID"]),
        "OrderDate": str(payload["OrderDate"]),
        "TotalCost": float(payload["TotalCost"]),
        "TotalTax": float(payload["TotalTax"]),
        "Details": [
            {
                "ProductID": int(line["ProductID"]),
                "Quantity": float(line["Quantity"]),
                "Cost": float(line["Cost"]),
            }
            for line in payload.get("Details", [])
        ],
    }
    order_collection().replace_one({"OrderID": order_id}, order, upsert=True)
    return order


def get_orders_by_user(user_id):
    docs = order_collection().find({"UserID": user_id}, {"_id": 0}).sort("OrderID", 1)
    return list(docs)


def get_next_order_id():
    doc = order_collection().find_one(sort=[("OrderID", DESCENDING)], projection={"OrderID": 1, "_id": 0})
    return 1 if doc is None else int(doc["OrderID"]) + 1


class StoreApiHandler(BaseHTTPRequestHandler):
    def send_json(self, status, payload):
        data = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def read_json(self):
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length).decode("utf-8") if length else "{}"
        return json.loads(raw)

    def do_GET(self):
        path = urlparse(self.path).path
        try:
            if path == "/health":
                self.send_json(200, {"status": "ok"})
                return
            if path.startswith("/users/") and path.count("/") == 2:
                user = get_user_by_id(int(path.split("/")[-1]))
                self.send_json(200 if user else 404, user or {"error": "User not found"})
                return
            if path.startswith("/products/") and path.count("/") == 2:
                product = get_product(int(path.split("/")[-1]))
                self.send_json(200 if product else 404, product or {"error": "Product not found"})
                return
            if path == "/orders/next-id":
                self.send_json(200, {"nextOrderID": get_next_order_id()})
                return
            if path.startswith("/orders/user/") and path.count("/") == 3:
                self.send_json(200, get_orders_by_user(int(path.split("/")[-1])))
                return
            if path.startswith("/orders/") and path.count("/") == 2:
                order = get_order(int(path.split("/")[-1]))
                self.send_json(200 if order else 404, order or {"error": "Order not found"})
                return
            self.send_json(404, {"error": "Endpoint not found"})
        except ValueError as exc:
            self.send_json(400, {"error": str(exc)})
        except Exception as exc:
            self.send_json(500, {"error": str(exc)})

    def do_POST(self):
        path = urlparse(self.path).path
        try:
            payload = self.read_json()
            if path == "/users/login":
                user = get_user_by_credentials(payload.get("username", ""), payload.get("password", ""))
                self.send_json(200 if user else 404, user or {"error": "User not found"})
                return
            if path.startswith("/products/") and path.count("/") == 2:
                self.send_json(200, save_product(int(path.split("/")[-1]), payload))
                return
            if path.startswith("/orders/") and path.count("/") == 2:
                self.send_json(200, save_order(int(path.split("/")[-1]), payload))
                return
            self.send_json(404, {"error": "Endpoint not found"})
        except KeyError as exc:
            self.send_json(400, {"error": f"Missing field: {exc.args[0]}"})
        except ValueError as exc:
            self.send_json(400, {"error": str(exc)})
        except Exception as exc:
            self.send_json(500, {"error": str(exc)})

    def log_message(self, *_):
        pass


if __name__ == "__main__":
    print(f"Store API listening on http://{HOST}:{PORT}")
    ThreadingHTTPServer((HOST, PORT), StoreApiHandler).serve_forever()
