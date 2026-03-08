#!/usr/bin/env python3
import html
import json
import os
import re
import sqlite3
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

DB_PATH = os.getenv("PRODUCT_API_DB", "store.db")
HOST = os.getenv("PRODUCT_API_HOST", "127.0.0.1")
PORT = int(os.getenv("PRODUCT_API_PORT", "8000"))


class ProductApiHandler(BaseHTTPRequestHandler):
    def send_body(self, code, body, ctype):
        data = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype + "; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        path = urlparse(self.path).path
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            if path == "/api/products":
                rows = conn.execute(
                    "SELECT ProductID, Name AS ProductName, Price, Quantity FROM Products ORDER BY ProductID"
                ).fetchall()
                trs = "".join(
                    f"<tr><td>{r['ProductID']}</td><td>{html.escape(str(r['ProductName']))}</td><td>{r['Price']}</td><td>{r['Quantity']}</td></tr>"
                    for r in rows
                )
                page = (
                    "<!doctype html><html><head><meta charset='utf-8'><title>Products</title></head><body><h1>Products</h1>"
                    "<table border='1' cellpadding='6' cellspacing='0'><tr><th>ProductID</th><th>ProductName</th><th>Price</th><th>Quantity</th></tr>"
                    + trs
                    + "</table></body></html>"
                )
                self.send_body(200, page, "text/html")
                return

            m = re.fullmatch(r"/api/products/(\d+)", path)
            if m:
                pid = int(m.group(1))
                row = conn.execute(
                    "SELECT ProductID, Name AS ProductName, Price, Quantity FROM Products WHERE ProductID = ?",
                    (pid,),
                ).fetchone()
                if not row:
                    self.send_body(404, json.dumps({"error": "Product not found", "ProductID": pid}), "application/json")
                    return
                self.send_body(
                    200,
                    json.dumps(
                        {
                            "ProductID": row["ProductID"],
                            "ProductName": row["ProductName"],
                            "Price": row["Price"],
                            "Quantity": row["Quantity"],
                        }
                    ),
                    "application/json",
                )
                return

        self.send_body(404, json.dumps({"error": "Endpoint not found"}), "application/json")

    def log_message(self, *_):
        pass


if __name__ == "__main__":
    print(f"Product API running at http://{HOST}:{PORT}")
    ThreadingHTTPServer((HOST, PORT), ProductApiHandler).serve_forever()
