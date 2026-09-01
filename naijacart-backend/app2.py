from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import hashlib
import secrets
from functools import wraps
from pathlib import Path

# ============================================================
# NAIJACART BACKEND
# ============================================================

app = Flask(__name__)
CORS(app)

BASE_DIR = Path(__file__).resolve().parent
DATABASE = BASE_DIR / "database.db"


# ============================================================
# DATABASE
# ============================================================

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_database():

    conn = get_db()
    cursor = conn.cursor()

    # USERS
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            phone TEXT,
            address TEXT,
            is_admin INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # PRODUCTS
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL,
            stock INTEGER NOT NULL DEFAULT 0,
            image TEXT,
            description TEXT,
            seller TEXT DEFAULT 'NaijaCart Seller',
            rating REAL DEFAULT 4.5,
            badge TEXT DEFAULT '',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()

    # ========================================================
    # CREATE ADMIN ACCOUNT
    # ========================================================

    admin_email = "admin@naijacart.com"

    existing = cursor.execute(
        "SELECT id FROM users WHERE email = ?",
        (admin_email,)
    ).fetchone()

    if not existing:

        password = hash_password("Admin@12345")

        cursor.execute("""
            INSERT INTO users
            (name, email, password, is_admin)
            VALUES (?, ?, ?, 1)
        """, (
            "NaijaCart Admin",
            admin_email,
            password
        ))

        conn.commit()

        print()
        print("======================================")
        print("ADMIN ACCOUNT CREATED")
        print("Email: admin@naijacart.com")
        print("Password: Admin@12345")
        print("======================================")
        print()

    conn.close()


# ============================================================
# PASSWORD
# ============================================================

def hash_password(password):

    return hashlib.sha256(
        password.encode("utf-8")
    ).hexdigest()


# ============================================================
# SIMPLE TOKEN STORAGE
# ============================================================

tokens = {}


# ============================================================
# AUTH DECORATOR
# ============================================================

def admin_required(function):

    @wraps(function)
    def wrapper(*args, **kwargs):

        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return jsonify({
                "success": False,
                "message": "Admin authentication required."
            }), 401

        if not auth_header.startswith("Bearer "):
            return jsonify({
                "success": False,
                "message": "Invalid authorization."
            }), 401

        token = auth_header.replace(
            "Bearer ",
            "",
            1
        )

        user_id = tokens.get(token)

        if not user_id:

            return jsonify({
                "success": False,
                "message": "Invalid or expired session."
            }), 401

        conn = get_db()

        user = conn.execute("""
            SELECT *
            FROM users
            WHERE id = ?
            AND is_admin = 1
        """, (user_id,)).fetchone()

        conn.close()

        if not user:

            return jsonify({
                "success": False,
                "message": "Admin access denied."
            }), 403

        return function(*args, **kwargs)

    return wrapper


# ============================================================
# HOME
# ============================================================

@app.route("/")
def home():

    return jsonify({
        "success": True,
        "message": "NaijaCart API is running."
    })


# ============================================================
# ADMIN LOGIN
# ============================================================

@app.route("/api/admin/login", methods=["POST"])
def admin_login():

    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "message": "No login data received."
        }), 400

    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:

        return jsonify({
            "success": False,
            "message": "Email and password are required."
        }), 400

    conn = get_db()

    user = conn.execute("""
        SELECT *
        FROM users
        WHERE email = ?
    """, (email,)).fetchone()

    conn.close()

    if not user:

        return jsonify({
            "success": False,
            "message": "Invalid login details."
        }), 401

    if user["is_admin"] != 1:

        return jsonify({
            "success": False,
            "message": "This account is not an administrator."
        }), 403

    password_hash = hash_password(password)

    if password_hash != user["password"]:

        return jsonify({
            "success": False,
            "message": "Invalid login details."
        }), 401

    token = secrets.token_urlsafe(32)

    tokens[token] = user["id"]

    return jsonify({
        "success": True,
        "token": token,
        "admin": {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"]
        }
    })


# ============================================================
# ADMIN LOGOUT
# ============================================================

@app.route("/api/admin/logout", methods=["POST"])
def admin_logout():

    auth_header = request.headers.get("Authorization")

    if auth_header and auth_header.startswith("Bearer "):

        token = auth_header.replace(
            "Bearer ",
            "",
            1
        )

        tokens.pop(token, None)

    return jsonify({
        "success": True,
        "message": "Logged out successfully."
    })


# ============================================================
# GET ALL PRODUCTS
# ============================================================

@app.route("/api/products", methods=["GET"])
def get_products():

    conn = get_db()

    products = conn.execute("""
        SELECT *
        FROM products
        ORDER BY id DESC
    """).fetchall()

    conn.close()

    result = [
        dict(product)
        for product in products
    ]

    return jsonify({
        "success": True,
        "products": result
    })


# ============================================================
# GET SINGLE PRODUCT
# ============================================================

@app.route("/api/products/<int:product_id>", methods=["GET"])
def get_product(product_id):

    conn = get_db()

    product = conn.execute("""
        SELECT *
        FROM products
        WHERE id = ?
    """, (product_id,)).fetchone()

    conn.close()

    if not product:

        return jsonify({
            "success": False,
            "message": "Product not found."
        }), 404

    return jsonify({
        "success": True,
        "product": dict(product)
    })


# ============================================================
# ADD PRODUCT
# ============================================================

@app.route("/api/admin/products", methods=["POST"])
@admin_required
def add_product():

    data = request.get_json()

    if not data:

        return jsonify({
            "success": False,
            "message": "No product data received."
        }), 400

    name = str(data.get("name", "")).strip()
    category = str(data.get("category", "")).strip()
    description = str(
        data.get("description", "")
    ).strip()

    image = str(
        data.get("image", "")
    ).strip()

    seller = str(
        data.get("seller", "NaijaCart Seller")
    ).strip()

    try:

        price = float(data.get("price", 0))
        stock = int(data.get("stock", 0))
        rating = float(data.get("rating", 4.5))

    except (ValueError, TypeError):

        return jsonify({
            "success": False,
            "message": "Price, stock and rating must be valid numbers."
        }), 400

    badge = str(
        data.get("badge", "")
    ).strip()

    if not name:

        return jsonify({
            "success": False,
            "message": "Product name is required."
        }), 400

    if not category:

        return jsonify({
            "success": False,
            "message": "Product category is required."
        }), 400

    if price < 0:

        return jsonify({
            "success": False,
            "message": "Price cannot be negative."
        }), 400

    if stock < 0:

        return jsonify({
            "success": False,
            "message": "Stock cannot be negative."
        }), 400

    conn = get_db()

    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO products
        (
            name,
            category,
            price,
            stock,
            image,
            description,
            seller,
            rating,
            badge
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        name,
        category,
        price,
        stock,
        image,
        description,
        seller,
        rating,
        badge
    ))

    conn.commit()

    product_id = cursor.lastrowid

    product = conn.execute("""
        SELECT *
        FROM products
        WHERE id = ?
    """, (product_id,)).fetchone()

    conn.close()

    return jsonify({
        "success": True,
        "message": "Product added successfully.",
        "product": dict(product)
    }), 201


# ============================================================
# DELETE PRODUCT
# ============================================================

@app.route(
    "/api/admin/products/<int:product_id>",
    methods=["DELETE"]
)
@admin_required
def delete_product(product_id):

    conn = get_db()

    product = conn.execute("""
        SELECT *
        FROM products
        WHERE id = ?
    """, (product_id,)).fetchone()

    if not product:

        conn.close()

        return jsonify({
            "success": False,
            "message": "Product not found."
        }), 404

    conn.execute("""
        DELETE FROM products
        WHERE id = ?
    """, (product_id,))

    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "message": "Product deleted successfully."
    })


# ============================================================
# RESTOCK PRODUCT
# ============================================================

@app.route(
    "/api/admin/products/<int:product_id>/restock",
    methods=["PATCH"]
)
@admin_required
def restock_product(product_id):

    data = request.get_json() or {}

    try:

        quantity = int(
            data.get("quantity", 0)
        )

    except (ValueError, TypeError):

        return jsonify({
            "success": False,
            "message": "Invalid quantity."
        }), 400

    if quantity <= 0:

        return jsonify({
            "success": False,
            "message": "Restock quantity must be greater than zero."
        }), 400

    conn = get_db()

    product = conn.execute("""
        SELECT *
        FROM products
        WHERE id = ?
    """, (product_id,)).fetchone()

    if not product:

        conn.close()

        return jsonify({
            "success": False,
            "message": "Product not found."
        }), 404

    new_stock = product["stock"] + quantity

    conn.execute("""
        UPDATE products
        SET stock = ?
        WHERE id = ?
    """, (
        new_stock,
        product_id
    ))

    conn.commit()

    updated = conn.execute("""
        SELECT *
        FROM products
        WHERE id = ?
    """, (product_id,)).fetchone()

    conn.close()

    return jsonify({
        "success": True,
        "message": "Product restocked successfully.",
        "product": dict(updated)
    })


# ============================================================
# UPDATE PRODUCT
# ============================================================

@app.route(
    "/api/admin/products/<int:product_id>",
    methods=["PUT"]
)
@admin_required
def update_product(product_id):

    data = request.get_json()

    if not data:

        return jsonify({
            "success": False,
            "message": "No update data received."
        }), 400

    conn = get_db()

    product = conn.execute("""
        SELECT *
        FROM products
        WHERE id = ?
    """, (product_id,)).fetchone()

    if not product:

        conn.close()

        return jsonify({
            "success": False,
            "message": "Product not found."
        }), 404

    name = str(
        data.get("name", product["name"])
    ).strip()

    category = str(
        data.get("category", product["category"])
    ).strip()

    description = str(
        data.get(
            "description",
            product["description"] or ""
        )
    ).strip()

    image = str(
        data.get(
            "image",
            product["image"] or ""
        )
    ).strip()

    seller = str(
        data.get(
            "seller",
            product["seller"] or "NaijaCart Seller"
        )
    ).strip()

    try:

        price = float(
            data.get(
                "price",
                product["price"]
            )
        )

        stock = int(
            data.get(
                "stock",
                product["stock"]
            )
        )

        rating = float(
            data.get(
                "rating",
                product["rating"]
            )
        )

    except (ValueError, TypeError):

        conn.close()

        return jsonify({
            "success": False,
            "message": "Invalid price, stock or rating."
        }), 400

    badge = str(
        data.get(
            "badge",
            product["badge"] or ""
        )
    ).strip()

    conn.execute("""
        UPDATE products
        SET
            name = ?,
            category = ?,
            price = ?,
            stock = ?,
            image = ?,
            description = ?,
            seller = ?,
            rating = ?,
            badge = ?
        WHERE id = ?
    """, (
        name,
        category,
        price,
        stock,
        image,
        description,
        seller,
        rating,
        badge,
        product_id
    ))

    conn.commit()

    updated = conn.execute("""
        SELECT *
        FROM products
        WHERE id = ?
    """, (product_id,)).fetchone()

    conn.close()

    return jsonify({
        "success": True,
        "message": "Product updated successfully.",
        "product": dict(updated)
    })


# ============================================================
# ADMIN STATISTICS
# ============================================================

@app.route("/api/admin/stats", methods=["GET"])
@admin_required
def admin_stats():

    conn = get_db()

    total_products = conn.execute("""
        SELECT COUNT(*)
        FROM products
    """).fetchone()[0]

    total_stock = conn.execute("""
        SELECT COALESCE(SUM(stock), 0)
        FROM products
    """).fetchone()[0]

    categories = conn.execute("""
        SELECT COUNT(DISTINCT category)
        FROM products
    """).fetchone()[0]

    low_stock = conn.execute("""
        SELECT COUNT(*)
        FROM products
        WHERE stock <= 5
    """).fetchone()[0]

    conn.close()

    return jsonify({
        "success": True,
        "stats": {
            "products": total_products,
            "stock": total_stock,
            "categories": categories,
            "low_stock": low_stock
        }
    })


# ============================================================
# START SERVER
# ============================================================

if __name__ == "__main__":

    init_database()

    print()
    print("🇳🇬 NaijaCart Backend")
    print("==============================")
    print("Server: http://127.0.0.1:5000")
    print("==============================")
    print()

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )