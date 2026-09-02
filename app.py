from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash
)

import sqlite3
import os
import uuid
import requests
import random
import resend

from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from functools import wraps
from datetime import datetime, timedelta

from dotenv import load_dotenv

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

load_dotenv(BASE_DIR / ".env")


# ============================================================
# APPLICATION
# ============================================================

app = Flask(__name__)

app.secret_key = os.environ.get(
    "SECRET_KEY",
    ""
).strip()

if not app.secret_key:
    raise RuntimeError(
        "SECRET_KEY is missing. Add SECRET_KEY to your "
        "Railway Variables or local .env file."
    )


# ============================================================
# DATABASE
# ============================================================

DATABASE_DIR = BASE_DIR / "database"

DATABASE_DIR.mkdir(
    parents=True,
    exist_ok=True
)

DATABASE = DATABASE_DIR / "naijacart.db"


# ============================================================
# PAGINATION
# ============================================================

PRODUCTS_PER_PAGE = 8


# ============================================================
# MAILBOXLAYER
# ============================================================

MAILBOXLAYER_ACCESS_KEY = os.environ.get(
    "MAILBOXLAYER_ACCESS_KEY",
    ""
).strip()

MAILBOXLAYER_URL = (
    "https://apilayer.net/api/check"
)


# ============================================================
# RESEND EMAIL CONFIGURATION
# ============================================================

RESEND_API_KEY = os.environ.get(
    "RESEND_API_KEY",
    ""
).strip()

RESEND_FROM_EMAIL = os.environ.get(
    "RESEND_FROM_EMAIL",
    ""
).strip()

RESEND_FROM_NAME = os.environ.get(
    "RESEND_FROM_NAME",
    "NaijaCart"
).strip()


# ============================================================
# EMAIL OTP SETTINGS
# ============================================================

OTP_EXPIRY_MINUTES = 10


# ============================================================
# PAYSTACK CONFIGURATION
# ============================================================

PAYSTACK_SECRET_KEY = os.environ.get(
    "PAYSTACK_SECRET_KEY",
    ""
).strip()

PAYSTACK_BASE_URL = (
    "https://api.paystack.co"
)

PAYSTACK_INITIALIZE_URL = (
    f"{PAYSTACK_BASE_URL}/transaction/initialize"
)

PAYSTACK_VERIFY_URL = (
    f"{PAYSTACK_BASE_URL}/transaction/verify"
)


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_db():

    conn = sqlite3.connect(
        str(DATABASE),
        timeout=30
    )

    conn.row_factory = sqlite3.Row

    conn.execute(
        "PRAGMA foreign_keys = ON"
    )

    conn.execute(
        "PRAGMA busy_timeout = 30000"
    )

    return conn


# ============================================================
# DATABASE INITIALIZATION
# ============================================================

def init_db():

    conn = get_db()

    conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            phone TEXT,
            address TEXT,
            role TEXT NOT NULL DEFAULT 'customer',
            email_verified INTEGER NOT NULL DEFAULT 0,
            verification_code TEXT,
            verification_expires_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL,
            description TEXT,
            image TEXT,
            seller_id INTEGER,
            stock INTEGER NOT NULL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (seller_id)
                REFERENCES users(id)
                ON DELETE SET NULL
        );

        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            customer_name TEXT,
            customer_phone TEXT,
            customer_email TEXT,
            customer_address TEXT,
            delivery_address TEXT,
            subtotal REAL DEFAULT 0,
            delivery REAL DEFAULT 0,
            total REAL DEFAULT 0,
            status TEXT DEFAULT 'Pending',
            paystack_reference TEXT,
            payment_status TEXT DEFAULT 'unpaid',
            paid_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id)
                REFERENCES users(id)
                ON DELETE SET NULL
        );

        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            product_name TEXT NOT NULL,
            price REAL NOT NULL,
            quantity INTEGER NOT NULL,
            FOREIGN KEY (order_id)
                REFERENCES orders(id)
                ON DELETE CASCADE,
            FOREIGN KEY (product_id)
                REFERENCES products(id)
        );

        CREATE TABLE IF NOT EXISTS wishlist (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, product_id),
            FOREIGN KEY (user_id)
                REFERENCES users(id)
                ON DELETE CASCADE,
            FOREIGN KEY (product_id)
                REFERENCES products(id)
                ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            rating INTEGER NOT NULL CHECK(rating BETWEEN 1 AND 5),
            title TEXT NOT NULL,
            comment TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id)
                REFERENCES users(id)
                ON DELETE CASCADE,
            FOREIGN KEY (product_id)
                REFERENCES products(id)
                ON DELETE CASCADE
        );
    """)

    # ========================================================
    # USERS MIGRATION
    # ========================================================

    user_columns = {
        row["name"]
        for row in conn.execute(
            "PRAGMA table_info(users)"
        ).fetchall()
    }

    if "email_verified" not in user_columns:
        conn.execute("""
            ALTER TABLE users
            ADD COLUMN email_verified INTEGER NOT NULL DEFAULT 0
        """)

    if "verification_code" not in user_columns:
        conn.execute("""
            ALTER TABLE users
            ADD COLUMN verification_code TEXT
        """)

    if "verification_expires_at" not in user_columns:
        conn.execute("""
            ALTER TABLE users
            ADD COLUMN verification_expires_at TIMESTAMP
        """)

    # ========================================================
    # ORDERS MIGRATION
    # ========================================================

    order_columns = {
        row["name"]
        for row in conn.execute(
            "PRAGMA table_info(orders)"
        ).fetchall()
    }

    if "payment_method" not in order_columns:
        conn.execute("""
            ALTER TABLE orders
            ADD COLUMN payment_method TEXT DEFAULT 'paystack'
        """)

    if "delivery_method" not in order_columns:
        conn.execute("""
            ALTER TABLE orders
            ADD COLUMN delivery_method TEXT DEFAULT 'home_delivery'
        """)

    if "customer_address" not in order_columns:
        conn.execute("""
            ALTER TABLE orders
            ADD COLUMN customer_address TEXT
        """)

    if "delivery_address" not in order_columns:
        conn.execute("""
            ALTER TABLE orders
            ADD COLUMN delivery_address TEXT
        """)

    if "subtotal" not in order_columns:
        conn.execute("""
            ALTER TABLE orders
            ADD COLUMN subtotal REAL DEFAULT 0
        """)

    if "delivery" not in order_columns:
        conn.execute("""
            ALTER TABLE orders
            ADD COLUMN delivery REAL DEFAULT 0
        """)

    if "total" not in order_columns:
        conn.execute("""
            ALTER TABLE orders
            ADD COLUMN total REAL DEFAULT 0
        """)

    if "paystack_reference" not in order_columns:
        conn.execute("""
            ALTER TABLE orders
            ADD COLUMN paystack_reference TEXT
        """)

    if "payment_status" not in order_columns:
        conn.execute("""
            ALTER TABLE orders
            ADD COLUMN payment_status TEXT DEFAULT 'unpaid'
        """)

    if "paid_at" not in order_columns:
        conn.execute("""
            ALTER TABLE orders
            ADD COLUMN paid_at TIMESTAMP
        """)

    conn.execute("""
        CREATE INDEX IF NOT EXISTS
        idx_orders_paystack_reference
        ON orders(paystack_reference)
    """)

    # ========================================================
    # OLD NULL EMAIL VERIFICATION VALUES
    # ========================================================

    conn.execute("""
        UPDATE users
        SET email_verified = 1
        WHERE email_verified IS NULL
    """)

    # ========================================================
    # ADMIN ACCOUNT
    # ========================================================

    admin_email = "admin@naijacart.com"

    admin_password = os.environ.get(
        "ADMIN_PASSWORD",
        ""
    )

    admin = conn.execute(
        """
        SELECT id
        FROM users
        WHERE LOWER(email) = ?
        """,
        (admin_email,)
    ).fetchone()

    if admin is None:

        if not admin_password:
            print(
                "WARNING: ADMIN_PASSWORD is not configured. "
                "Admin account will not be created."
            )
        else:
            conn.execute(
                """
                INSERT INTO users
                (
                    name,
                    email,
                    password,
                    phone,
                    address,
                    role,
                    email_verified
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    "NaijaCart Administrator",
                    admin_email,
                    generate_password_hash(admin_password),
                    "08000000000",
                    "Lagos, Nigeria",
                    "admin",
                    1
                )
            )

    else:

        conn.execute(
            """
            UPDATE users
            SET
                role = 'admin',
                email_verified = 1
            WHERE LOWER(email) = ?
            """,
            (admin_email,)
        )

    # ========================================================
    # DEMO SELLER
    # ========================================================

    seller_email = "seller@naijacart.local"

    seller_password = os.environ.get(
        "SELLER_PASSWORD",
        ""
    )

    seller = conn.execute(
        """
        SELECT id
        FROM users
        WHERE LOWER(email) = ?
        """,
        (seller_email,)
    ).fetchone()

    if seller is None:

        if not seller_password:
            print(
                "WARNING: SELLER_PASSWORD is not configured. "
                "Seller account will not be created."
            )
        else:
            conn.execute(
                """
                INSERT INTO users
                (
                    name,
                    email,
                    password,
                    phone,
                    address,
                    role,
                    email_verified
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    "NaijaCart Seller",
                    seller_email,
                    generate_password_hash(seller_password),
                    "08000000000",
                    "Lagos, Nigeria",
                    "seller",
                    1
                )
            )

    else:

        conn.execute(
            """
            UPDATE users
            SET
                role = 'seller',
                email_verified = 1
            WHERE LOWER(email) = ?
            """,
            (seller_email,)
        )

    conn.commit()
    conn.close()


# ============================================================
# MAILBOXLAYER EMAIL VALIDATION
# ============================================================

def validate_email_with_mailboxlayer(email):

    email = email.strip().lower()

    if not email:
        return False

    if email.count("@") != 1:
        return False

    local_part, domain = email.rsplit("@", 1)

    if not local_part:
        return False

    if not domain:
        return False

    if "." not in domain:
        return False

    if domain.startswith("."):
        return False

    if domain.endswith("."):
        return False

    if not MAILBOXLAYER_ACCESS_KEY:

        print(
            "WARNING: MAILBOXLAYER_ACCESS_KEY is missing."
        )

        return True

    try:

        response = requests.get(
            MAILBOXLAYER_URL,
            params={
                "access_key": MAILBOXLAYER_ACCESS_KEY,
                "email": email,
                "smtp": "1",
                "format": "1"
            },
            timeout=15
        )

        response.raise_for_status()

        result = response.json()

        if result.get("error"):

            print(
                "MAILBOXLAYER ERROR:",
                result["error"]
            )

            return True

        format_valid = result.get(
            "format_valid"
        )

        mx_found = result.get(
            "mx_found"
        )

        if (
            format_valid is True
            and mx_found is True
        ):
            return True

        if (
            str(format_valid).lower() == "true"
            and str(mx_found).lower() == "true"
        ):
            return True

        if (
            str(format_valid) == "1"
            and str(mx_found) == "1"
        ):
            return True

        print(
            "MAILBOXLAYER INCOMPLETE VALIDATION:",
            result
        )

        return True

    except requests.RequestException as error:

        print(
            "MAILBOXLAYER CONNECTION ERROR:",
            error
        )

        return True

    except Exception as error:

        print(
            "MAILBOXLAYER ERROR:",
            error
        )

        return True


# ============================================================
# GENERATE 6 DIGIT OTP
# ============================================================

def generate_verification_code():

    return str(
        random.randint(
            100000,
            999999
        )
    )


# ============================================================
# SEND VERIFICATION EMAIL WITH RESEND
# ============================================================

def send_verification_email(
    recipient_email,
    recipient_name,
    verification_code
):

    if not RESEND_API_KEY:

        raise RuntimeError(
            "RESEND_API_KEY is missing. "
            "Add RESEND_API_KEY to Railway Variables."
        )

    if not RESEND_FROM_EMAIL:

        raise RuntimeError(
            "RESEND_FROM_EMAIL is missing. "
            "Add your verified Resend sender email "
            "to Railway Variables."
        )

    resend.api_key = RESEND_API_KEY

    subject = (
        "Your NaijaCart verification code"
    )

    text_content = f"""
Hello {recipient_name},

Welcome to NaijaCart!

Your 6-digit email verification code is:

{verification_code}

This code will expire in {OTP_EXPIRY_MINUTES} minutes.

If you did not create a NaijaCart account, you can ignore this email.

Regards,
NaijaCart Team
""".strip()

    html_content = f"""
<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">

    <meta
        name="viewport"
        content="width=device-width, initial-scale=1.0"
    >

    <title>NaijaCart Verification</title>
</head>

<body
    style="
        margin:0;
        padding:0;
        background:#f4f7f6;
        font-family:Arial,sans-serif;
    "
>

    <div
        style="
            max-width:600px;
            margin:40px auto;
            background:#ffffff;
            border-radius:16px;
            padding:35px;
            box-shadow:0 10px 30px rgba(0,0,0,.08);
        "
    >

        <h1
            style="
                color:#006b57;
                margin-bottom:10px;
            "
        >
            NaijaCart
        </h1>

        <h2>
            Verify your email
        </h2>

        <p>
            Hello {recipient_name},
        </p>

        <p>
            Thanks for creating your NaijaCart account.
            Enter the verification code below to confirm
            your email address.
        </p>

        <div
            style="
                margin:30px 0;
                padding:22px;
                text-align:center;
                background:#e8f6f2;
                border-radius:12px;
            "
        >

            <div
                style="
                    font-size:36px;
                    font-weight:bold;
                    letter-spacing:8px;
                    color:#006b57;
                "
            >
                {verification_code}
            </div>

        </div>

        <p>
            This code expires in
            <strong>
                {OTP_EXPIRY_MINUTES} minutes
            </strong>.
        </p>

        <p
            style="
                color:#777;
                font-size:14px;
            "
        >
            If you did not create this account,
            you can safely ignore this email.
        </p>

        <hr>

        <p
            style="
                color:#777;
                font-size:13px;
            "
        >
            © NaijaCart
        </p>

    </div>

</body>

</html>
"""

    try:

        response = resend.Emails.send({
            "from": f"{RESEND_FROM_NAME} <{RESEND_FROM_EMAIL}>",
            "to": [recipient_email],
            "subject": subject,
            "text": text_content,
            "html": html_content
        })

        print(
            "Verification email sent successfully."
        )

        print(
            "Resend response:",
            response
        )

        return response

    except Exception as error:

        print(
            "RESEND EMAIL ERROR:",
            error
        )

        raise RuntimeError(
            f"Resend could not send the verification email: {error}"
        ) from error


# ============================================================
# SEND OTP HELPER
# ============================================================

def create_and_send_verification_code(user_id):

    code = generate_verification_code()

    expires_at = (
        datetime.utcnow()
        + timedelta(
            minutes=OTP_EXPIRY_MINUTES
        )
    )

    conn = get_db()

    user = conn.execute(
        """
        SELECT
            id,
            name,
            email
        FROM users
        WHERE id = ?
        """,
        (user_id,)
    ).fetchone()

    if user is None:

        conn.close()

        raise RuntimeError(
            "User account could not be found."
        )

    conn.execute(
        """
        UPDATE users
        SET
            verification_code = ?,
            verification_expires_at = ?
        WHERE id = ?
        """,
        (
            code,
            expires_at.isoformat(),
            user_id
        )
    )

    conn.commit()
    conn.close()

    try:

        send_verification_email(
            recipient_email=user["email"],
            recipient_name=user["name"],
            verification_code=code
        )

    except Exception:

        conn = get_db()

        conn.execute(
            """
            UPDATE users
            SET
                verification_code = NULL,
                verification_expires_at = NULL
            WHERE id = ?
            """,
            (user_id,)
        )

        conn.commit()
        conn.close()

        raise


# ============================================================
# REDIRECT BACK HELPER
# ============================================================

def redirect_back(anchor=None):

    target = request.referrer or url_for("home")

    if anchor:

        if "#" in target:
            target = target.split("#", 1)[0]

        target = f"{target}#{anchor}"

    return redirect(target)


# ============================================================
# LOGIN REQUIRED
# ============================================================

def login_required(route_function):

    @wraps(route_function)
    def wrapper(*args, **kwargs):

        if not session.get("user_id"):

            flash(
                "Please sign in first."
            )

            return redirect(
                url_for("home")
            )

        return route_function(
            *args,
            **kwargs
        )

    return wrapper


# ============================================================
# ADMIN REQUIRED
# ============================================================

def admin_required(route_function):

    @wraps(route_function)
    def wrapper(*args, **kwargs):

        user_id = session.get(
            "user_id"
        )

        user_role = session.get(
            "user_role"
        )

        if (
            not user_id
            or user_role != "admin"
        ):

            flash(
                "Please log in as administrator first."
            )

            return redirect(
                url_for("admin_login")
            )

        conn = get_db()

        user = conn.execute(
            """
            SELECT *
            FROM users
            WHERE id = ?
            AND role = 'admin'
            """,
            (user_id,)
        ).fetchone()

        conn.close()

        if user is None:

            session.clear()

            flash(
                "Administrator account not found."
            )

            return redirect(
                url_for("admin_login")
            )

        return route_function(
            *args,
            **kwargs
        )

    return wrapper


# ============================================================
# SELLER REQUIRED
# ============================================================

def seller_required(route_function):

    @wraps(route_function)
    def wrapper(*args, **kwargs):

        user_id = session.get(
            "user_id"
        )

        if not user_id:

            flash(
                "Please log in first."
            )

            return redirect(
                url_for("home")
            )

        conn = get_db()

        user = conn.execute(
            """
            SELECT *
            FROM users
            WHERE id = ?
            """,
            (user_id,)
        ).fetchone()

        conn.close()

        if user is None:

            session.clear()

            return redirect(
                url_for("home")
            )

        if user["role"] not in (
            "seller",
            "admin"
        ):

            flash(
                "You need seller access."
            )

            return redirect(
                url_for("home")
            )

        return route_function(
            *args,
            **kwargs
        )

    return wrapper


# ============================================================
# CART
# ============================================================

def current_cart():

    if "cart" not in session:

        session["cart"] = {}

    return session["cart"]


# ============================================================
# CART ITEMS
# ============================================================

def cart_items():

    cart = current_cart()

    if not cart:

        return [], 0, 0

    quantities = {}
    ids = []

    for product_id, quantity in cart.items():

        try:

            product_id = int(product_id)
            quantity = int(quantity)

        except (
            TypeError,
            ValueError
        ):

            continue

        if quantity > 0:

            ids.append(product_id)

            quantities[product_id] = quantity

    if not ids:

        session["cart"] = {}
        session.modified = True

        return [], 0, 0

    placeholders = ",".join(
        "?" for _ in ids
    )

    conn = get_db()

    products = conn.execute(
        f"""
        SELECT
            id,
            name,
            category,
            price,
            description,
            image,
            stock
        FROM products
        WHERE id IN ({placeholders})
        """,
        ids
    ).fetchall()

    conn.close()

    items = []
    subtotal = 0.0
    valid_cart = {}

    for product in products:

        product_id = product["id"]

        quantity = quantities.get(
            product_id,
            0
        )

        available_stock = max(
            int(product["stock"]),
            0
        )

        quantity = min(
            quantity,
            available_stock
        )

        if quantity <= 0:
            continue

        valid_cart[
            str(product_id)
        ] = quantity

        line_total = (
            float(product["price"])
            * quantity
        )

        subtotal += line_total

        items.append({
            "product": product,
            "quantity": quantity,
            "line_total": line_total
        })

    if valid_cart != cart:

        session["cart"] = valid_cart
        session.modified = True

    count = sum(
        item["quantity"]
        for item in items
    )

    return (
        items,
        subtotal,
        count
    )


# ============================================================
# GLOBAL CART CONTEXT
# ============================================================

@app.context_processor
def inject_cart():

    items, subtotal, count = cart_items()

    wishlist_count = 0

    user_id = session.get("user_id")

    if user_id:

        conn = get_db()

        wishlist_count = conn.execute(
            """
            SELECT COUNT(*)
            FROM wishlist
            WHERE user_id = ?
            """,
            (user_id,)
        ).fetchone()[0]

        conn.close()

    return {
        "cart_items": items,
        "cart_subtotal": subtotal,
        "cart_count": count,
        "cart_total": subtotal,
        "wishlist_count": wishlist_count
    }


# ============================================================
# HOME
# ============================================================

@app.route("/")
def home():

    category = request.args.get(
        "category",
        "all"
    ).strip().lower()

    search = request.args.get(
        "q",
        ""
    ).strip()

    sort = request.args.get(
        "sort",
        "newest"
    ).strip()

    try:

        page = int(
            request.args.get(
                "page",
                1
            )
        )

    except (
        TypeError,
        ValueError
    ):

        page = 1

    if page < 1:
        page = 1

    per_page = PRODUCTS_PER_PAGE

    conn = get_db()

    query = """
        SELECT
            products.*,
            users.name AS seller_name
        FROM products
        LEFT JOIN users
            ON products.seller_id = users.id
        WHERE 1 = 1
    """

    count_query = """
        SELECT COUNT(*) AS total
        FROM products
        LEFT JOIN users
            ON products.seller_id = users.id
        WHERE 1 = 1
    """

    params = []
    count_params = []

    if category != "all":

        query += """
            AND LOWER(products.category) = ?
        """

        count_query += """
            AND LOWER(products.category) = ?
        """

        params.append(category)
        count_params.append(category)

    if search:

        query += """
            AND (
                products.name LIKE ?
                OR products.category LIKE ?
                OR products.description LIKE ?
            )
        """

        count_query += """
            AND (
                products.name LIKE ?
                OR products.category LIKE ?
                OR products.description LIKE ?
            )
        """

        search_value = f"%{search}%"

        params.extend([
            search_value,
            search_value,
            search_value
        ])

        count_params.extend([
            search_value,
            search_value,
            search_value
        ])

    if sort == "price-low":

        query += """
            ORDER BY products.price ASC
        """

    elif sort == "price-high":

        query += """
            ORDER BY products.price DESC
        """

    elif sort == "name":

        query += """
            ORDER BY products.name
            COLLATE NOCASE ASC
        """

    else:

        query += """
            ORDER BY products.id DESC
        """

    total_products = conn.execute(
        count_query,
        count_params
    ).fetchone()["total"]

    total_pages = max(
        1,
        (
            total_products
            + per_page
            - 1
        )
        // per_page
    )

    if page > total_pages:
        page = total_pages

    offset = (
        page - 1
    ) * per_page

    query += """
        LIMIT ? OFFSET ?
    """

    params.extend([
        per_page,
        offset
    ])

    products = conn.execute(
        query,
        params
    ).fetchall()

    categories = conn.execute(
        """
        SELECT DISTINCT category
        FROM products
        ORDER BY category
        """
    ).fetchall()

    conn.close()

    start_product = (
        offset + 1
        if total_products > 0
        else 0
    )

    end_product = min(
        offset + per_page,
        total_products
    )

    return render_template(
        "index.html",
        shop="NaijaCart",
        products=products,
        categories=categories,
        selected_category=category,
        search_query=search,
        selected_sort=sort,
        page=page,
        current_page=page,
        per_page=per_page,
        total_products=total_products,
        total_pages=total_pages,
        has_previous=page > 1,
        has_next=page < total_pages,
        previous_page=page - 1,
        next_page=page + 1,
        start_product=start_product,
        end_product=end_product
    )


# ============================================================
# REGISTER
# ============================================================

@app.route(
    "/register",
    methods=["POST"]
)
def register():

    name = request.form.get(
        "name",
        ""
    ).strip()

    email = request.form.get(
        "email",
        ""
    ).strip().lower()

    phone = request.form.get(
        "phone",
        ""
    ).strip()

    password = request.form.get(
        "password",
        ""
    )

    if not name or not email or not password:

        flash(
            "Name, email and password are required."
        )

        return redirect(
            url_for("home")
        )

    if len(password) < 6:

        flash(
            "Password must contain at least 6 characters."
        )

        return redirect(
            url_for("home")
        )

    if not validate_email_with_mailboxlayer(email):

        flash(
            "Please enter a valid email address."
        )

        return redirect(
            url_for("home")
        )

    conn = get_db()

    existing = conn.execute(
        """
        SELECT *
        FROM users
        WHERE LOWER(email) = ?
        """,
        (email,)
    ).fetchone()

    if existing:

        if (
            existing["role"] == "customer"
            and int(existing["email_verified"] or 0) == 0
        ):

            conn.close()

            try:

                create_and_send_verification_code(
                    existing["id"]
                )

                session[
                    "verification_user_id"
                ] = existing["id"]

                flash(
                    "Your account already exists but "
                    "is not verified. A new code has been sent."
                )

                return redirect(
                    url_for("verify_email")
                )

            except Exception as error:

                print(
                    "RESEND VERIFICATION ERROR:",
                    error
                )

                flash(
                    f"We could not send the verification email: {error}"
                )

                return redirect(
                    url_for("home")
                )

        conn.close()

        flash(
            "An account with this email already exists."
        )

        return redirect(
            url_for("home")
        )

    try:

        cursor = conn.execute(
            """
            INSERT INTO users
            (
                name,
                email,
                password,
                phone,
                role,
                email_verified
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                name,
                email,
                generate_password_hash(password),
                phone,
                "customer",
                0
            )
        )

        user_id = cursor.lastrowid

        conn.commit()
        conn.close()

        create_and_send_verification_code(
            user_id
        )

        session[
            "verification_user_id"
        ] = user_id

        session.modified = True

        flash(
            "Account created! "
            "A 6-digit verification code has been sent "
            "to your email."
        )

        return redirect(
            url_for("verify_email")
        )

    except Exception as error:

        try:
            conn.rollback()
            conn.close()
        except Exception:
            pass

        print(
            "REGISTRATION ERROR:",
            error
        )

        flash(
            f"Could not complete registration: {error}"
        )

        return redirect(
            url_for("home")
        )


# ============================================================
# VERIFY EMAIL
# ============================================================

@app.route(
    "/verify-email",
    methods=["GET", "POST"]
)
def verify_email():

    user_id = session.get(
        "verification_user_id"
    )

    if not user_id:

        flash(
            "There is no email verification in progress."
        )

        return redirect(
            url_for("home")
        )

    conn = get_db()

    user = conn.execute(
        """
        SELECT *
        FROM users
        WHERE id = ?
        """,
        (user_id,)
    ).fetchone()

    conn.close()

    if user is None:

        session.pop(
            "verification_user_id",
            None
        )

        flash(
            "Account not found."
        )

        return redirect(
            url_for("home")
        )

    if int(user["email_verified"] or 0) == 1:

        session.pop(
            "verification_user_id",
            None
        )

        flash(
            "Your email is already verified."
        )

        return redirect(
            url_for("home")
        )

    if request.method == "POST":

        code = request.form.get(
            "code",
            ""
        ).strip()

        if not code:

            flash(
                "Please enter your 6-digit verification code."
            )

            return redirect(
                url_for("verify_email")
            )

        if (
            len(code) != 6
            or not code.isdigit()
        ):

            flash(
                "Verification code must contain exactly 6 digits."
            )

            return redirect(
                url_for("verify_email")
            )

        stored_code = user[
            "verification_code"
        ]

        expires_at = user[
            "verification_expires_at"
        ]

        if not stored_code:

            flash(
                "No verification code is active. "
                "Please request a new code."
            )

            return redirect(
                url_for("verify_email")
            )

        if code != str(stored_code):

            flash(
                "Incorrect verification code."
            )

            return redirect(
                url_for("verify_email")
            )

        if not expires_at:

            flash(
                "Your verification code has expired."
            )

            return redirect(
                url_for("verify_email")
            )

        try:

            expiry_datetime = datetime.fromisoformat(
                str(expires_at)
            )

        except ValueError:

            flash(
                "Your verification code has expired. "
                "Please request a new one."
            )

            return redirect(
                url_for("verify_email")
            )

        if datetime.utcnow() > expiry_datetime:

            flash(
                "Your verification code has expired. "
                "Please request a new one."
            )

            return redirect(
                url_for("verify_email")
            )

        conn = get_db()

        conn.execute(
            """
            UPDATE users
            SET
                email_verified = 1,
                verification_code = NULL,
                verification_expires_at = NULL
            WHERE id = ?
            """,
            (user_id,)
        )

        conn.commit()

        verified_user = conn.execute(
            """
            SELECT *
            FROM users
            WHERE id = ?
            """,
            (user_id,)
        ).fetchone()

        conn.close()

        session.clear()

        session["user_id"] = (
            verified_user["id"]
        )

        session["user_name"] = (
            verified_user["name"]
        )

        session["user_role"] = (
            verified_user["role"]
        )

        flash(
            "Email verified successfully! "
            "Welcome to NaijaCart."
        )

        return redirect(
            url_for("home")
        )

    return render_template(
        "verify_email.html",
        email=user["email"]
    )


# ============================================================
# RESEND VERIFICATION
# ============================================================

@app.route(
    "/resend-verification",
    methods=["POST"]
)
def resend_verification():

    user_id = session.get(
        "verification_user_id"
    )

    if not user_id:

        flash(
            "There is no account waiting for verification."
        )

        return redirect(
            url_for("home")
        )

    conn = get_db()

    user = conn.execute(
        """
        SELECT *
        FROM users
        WHERE id = ?
        """,
        (user_id,)
    ).fetchone()

    conn.close()

    if user is None:

        session.pop(
            "verification_user_id",
            None
        )

        flash(
            "Account not found."
        )

        return redirect(
            url_for("home")
        )

    if int(user["email_verified"] or 0) == 1:

        flash(
            "This email is already verified."
        )

        return redirect(
            url_for("home")
        )

    try:

        create_and_send_verification_code(
            user_id
        )

        flash(
            "A new 6-digit verification code "
            "has been sent to your email."
        )

    except Exception as error:

        print(
            "RESEND EMAIL ERROR:",
            error
        )

        flash(
            f"We could not send the verification code: {error}"
        )

    return redirect(
        url_for("verify_email")
    )


# ============================================================
# CUSTOMER LOGIN
# ============================================================

@app.route(
    "/login",
    methods=["POST"]
)
def login():

    email = request.form.get(
        "email",
        ""
    ).strip().lower()

    password = request.form.get(
        "password",
        ""
    )

    if not email or not password:

        flash(
            "Please enter your email and password."
        )

        return redirect(
            url_for("home")
        )

    conn = get_db()

    user = conn.execute(
        """
        SELECT *
        FROM users
        WHERE LOWER(email) = ?
        """,
        (email,)
    ).fetchone()

    conn.close()

    if (
        user is None
        or not check_password_hash(
            user["password"],
            password
        )
    ):

        flash(
            "Invalid email or password."
        )

        return redirect(
            url_for("home")
        )

    if (
        user["role"] == "customer"
        and int(user["email_verified"] or 0) != 1
    ):

        session.clear()

        session[
            "verification_user_id"
        ] = user["id"]

        try:

            create_and_send_verification_code(
                user["id"]
            )

            flash(
                "Please verify your email first. "
                "A new 6-digit code has been sent."
            )

        except Exception as error:

            print(
                "LOGIN VERIFICATION EMAIL ERROR:",
                error
            )

            flash(
                f"Please verify your email first. "
                f"We could not send a new code: {error}"
            )

        return redirect(
            url_for("verify_email")
        )

    session.clear()

    session["user_id"] = (
        user["id"]
    )

    session["user_name"] = (
        user["name"]
    )

    session["user_role"] = (
        user["role"]
    )

    flash(
        f"Welcome, {user['name']}!"
    )

    if user["role"] == "admin":

        return redirect(
            url_for("admin_dashboard")
        )

    return redirect(
        url_for("home")
    )


# ============================================================
# LOGOUT
# ============================================================

@app.route("/logout")
def logout():

    session.clear()

    flash(
        "You have been logged out."
    )

    return redirect(
        url_for("home")
    )


# ============================================================
# CONTACT
# ============================================================

@app.route(
    "/contact",
    methods=["POST"]
)
def contact():

    name = request.form.get(
        "name",
        ""
    ).strip()

    email = request.form.get(
        "email",
        ""
    ).strip()

    message = request.form.get(
        "message",
        ""
    ).strip()

    if not name or not email or not message:

        flash(
            "Please complete the contact form."
        )

        return redirect(
            url_for("home")
        )

    flash(
        "Your message has been received. Thank you."
    )

    return redirect(
        url_for("home")
    )


# ============================================================
# ADMIN LOGIN
# ============================================================

@app.route(
    "/admin/login",
    methods=["GET", "POST"]
)
def admin_login():

    if session.get(
        "user_role"
    ) == "admin":

        return redirect(
            url_for("admin_dashboard")
        )

    if request.method == "POST":

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )

        if not email or not password:

            flash(
                "Please enter your email and password."
            )

            return redirect(
                url_for("admin_login")
            )

        conn = get_db()

        user = conn.execute(
            """
            SELECT *
            FROM users
            WHERE LOWER(email) = ?
            AND role = 'admin'
            """,
            (email,)
        ).fetchone()

        conn.close()

        if (
            user is None
            or not check_password_hash(
                user["password"],
                password
            )
        ):

            flash(
                "Invalid administrator email or password."
            )

            return redirect(
                url_for("admin_login")
            )

        session.clear()

        session["user_id"] = (
            user["id"]
        )

        session["user_name"] = (
            user["name"]
        )

        session["user_role"] = "admin"

        flash(
            "Welcome to the NaijaCart Admin Dashboard."
        )

        return redirect(
            url_for("admin_dashboard")
        )

    return render_template(
        "admin_login.html"
    )


# ============================================================
# ADMIN DASHBOARD
# ============================================================

@app.route("/admin")
@admin_required
def admin_dashboard():

    conn = get_db()

    total_products = conn.execute(
        """
        SELECT COUNT(*) AS count
        FROM products
        """
    ).fetchone()["count"]

    total_orders = conn.execute(
        """
        SELECT COUNT(*) AS count
        FROM orders
        """
    ).fetchone()["count"]

    pending_orders = conn.execute(
        """
        SELECT COUNT(*) AS count
        FROM orders
        WHERE status = 'Pending'
        """
    ).fetchone()["count"]

    processing_orders = conn.execute(
        """
        SELECT COUNT(*) AS count
        FROM orders
        WHERE status = 'Processing'
        """
    ).fetchone()["count"]

    shipped_orders = conn.execute(
        """
        SELECT COUNT(*) AS count
        FROM orders
        WHERE status = 'Shipped'
        """
    ).fetchone()["count"]

    completed_orders = conn.execute(
        """
        SELECT COUNT(*) AS count
        FROM orders
        WHERE status = 'Completed'
        """
    ).fetchone()["count"]

    cancelled_orders = conn.execute(
        """
        SELECT COUNT(*) AS count
        FROM orders
        WHERE status = 'Cancelled'
        """
    ).fetchone()["count"]

    total_customers = conn.execute(
        """
        SELECT COUNT(*) AS count
        FROM users
        WHERE role = 'customer'
        """
    ).fetchone()["count"]

    total_sellers = conn.execute(
        """
        SELECT COUNT(*) AS count
        FROM users
        WHERE role = 'seller'
        """
    ).fetchone()["count"]

    total_sales = conn.execute(
        """
        SELECT COALESCE(SUM(total), 0) AS total
        FROM orders
        WHERE payment_status = 'paid'
        AND status != 'Cancelled'
        """
    ).fetchone()["total"]

    low_stock = conn.execute(
        """
        SELECT
            products.*,
            users.name AS seller_name
        FROM products
        LEFT JOIN users
            ON products.seller_id = users.id
        WHERE products.stock <= 5
        ORDER BY products.stock ASC
        LIMIT 10
        """
    ).fetchall()

    recent_orders = conn.execute(
        """
        SELECT *
        FROM orders
        ORDER BY id DESC
        LIMIT 10
        """
    ).fetchall()

    recent_products = conn.execute(
        """
        SELECT
            products.*,
            users.name AS seller_name
        FROM products
        LEFT JOIN users
            ON products.seller_id = users.id
        ORDER BY products.id DESC
        LIMIT 10
        """
    ).fetchall()

    conn.close()

    return render_template(
        "admin.html",
        total_products=total_products,
        total_orders=total_orders,
        pending_orders=pending_orders,
        processing_orders=processing_orders,
        shipped_orders=shipped_orders,
        completed_orders=completed_orders,
        cancelled_orders=cancelled_orders,
        total_customers=total_customers,
        total_sellers=total_sellers,
        total_sales=total_sales,
        recent_orders=recent_orders,
        recent_products=recent_products,
        low_stock=low_stock
    )


# ============================================================
# ADMIN ORDERS
# ============================================================

@app.route("/admin/orders")
@admin_required
def admin_orders():

    conn = get_db()

    orders = conn.execute(
        """
        SELECT *
        FROM orders
        ORDER BY id DESC
        """
    ).fetchall()

    conn.close()

    return render_template(
        "admin_orders.html",
        orders=orders
    )


# ============================================================
# ADMIN ORDER DETAILS
# ============================================================

@app.route(
    "/admin/orders/<int:order_id>"
)
@admin_required
def admin_order_detail(order_id):

    conn = get_db()

    order = conn.execute(
        """
        SELECT *
        FROM orders
        WHERE id = ?
        """,
        (order_id,)
    ).fetchone()

    if order is None:

        conn.close()

        flash(
            "Order not found."
        )

        return redirect(
            url_for("admin_orders")
        )

    items = conn.execute(
        """
        SELECT *
        FROM order_items
        WHERE order_id = ?
        ORDER BY id
        """,
        (order_id,)
    ).fetchall()

    conn.close()

    return render_template(
        "admin_order_detail.html",
        order=order,
        items=items
    )


# ============================================================
# UPDATE ORDER STATUS
# ============================================================

@app.post(
    "/admin/orders/<int:order_id>/status"
)
@admin_required
def update_order_status(order_id):

    status = request.form.get(
        "status",
        "Pending"
    ).strip()

    allowed_statuses = {
        "Pending",
        "Processing",
        "Shipped",
        "Completed",
        "Cancelled"
    }

    if status not in allowed_statuses:

        flash(
            "Invalid order status."
        )

        return redirect(
            url_for("admin_orders")
        )

    conn = get_db()

    order = conn.execute(
        """
        SELECT id
        FROM orders
        WHERE id = ?
        """,
        (order_id,)
    ).fetchone()

    if order is None:

        conn.close()

        flash(
            "Order not found."
        )

        return redirect(
            url_for("admin_orders")
        )

    conn.execute(
        """
        UPDATE orders
        SET status = ?
        WHERE id = ?
        """,
        (
            status,
            order_id
        )
    )

    conn.commit()
    conn.close()

    flash(
        f"Order #{order_id} updated to {status}."
    )

    return redirect(
        url_for("admin_orders")
    )


# ============================================================
# ADMIN PRODUCTS
# ============================================================

@app.route(
    "/admin/products",
    methods=["GET", "POST"]
)
@admin_required
def admin_products():

    if request.method == "POST":

        name = request.form.get(
            "name",
            ""
        ).strip()

        category = request.form.get(
            "category",
            ""
        ).strip().lower()

        price_text = request.form.get(
            "price",
            ""
        ).strip()

        description = request.form.get(
            "description",
            ""
        ).strip()

        image = request.form.get(
            "image",
            ""
        ).strip()

        stock_text = request.form.get(
            "stock",
            ""
        ).strip()

        allowed_categories = {
            "fashion",
            "groceries",
            "electronics",
            "beauty",
            "home"
        }

        if not name:

            flash(
                "Product name is required."
            )

            return redirect(
                url_for("admin_products")
            )

        if category not in allowed_categories:

            flash(
                "Please select a valid category."
            )

            return redirect(
                url_for("admin_products")
            )

        try:

            price = float(
                price_text.replace(
                    ",",
                    ""
                )
            )

            if price < 0:
                raise ValueError

        except (
            ValueError,
            TypeError
        ):

            flash(
                "Enter a valid price."
            )

            return redirect(
                url_for("admin_products")
            )

        try:

            stock = int(
                stock_text
            )

            if stock < 0:
                raise ValueError

        except (
            ValueError,
            TypeError
        ):

            flash(
                "Enter a valid stock quantity."
            )

            return redirect(
                url_for("admin_products")
            )

        conn = get_db()

        conn.execute(
            """
            INSERT INTO products
            (
                name,
                category,
                price,
                description,
                image,
                seller_id,
                stock
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                name,
                category,
                price,
                description,
                image,
                session["user_id"],
                stock
            )
        )

        conn.commit()
        conn.close()

        flash(
            f"{name} was added successfully."
        )

        return redirect(
            url_for("admin_products")
        )

    conn = get_db()

    products = conn.execute(
        """
        SELECT
            products.*,
            users.name AS seller_name
        FROM products
        LEFT JOIN users
            ON products.seller_id = users.id
        ORDER BY products.id DESC
        """
    ).fetchall()

    conn.close()

    return render_template(
        "admin_products.html",
        products=products
    )


# ============================================================
# EDIT PRODUCT
# ============================================================

@app.route(
    "/admin/products/edit/<int:product_id>",
    methods=["GET", "POST"]
)
@admin_required
def edit_product(product_id):

    conn = get_db()

    product = conn.execute(
        """
        SELECT *
        FROM products
        WHERE id = ?
        """,
        (product_id,)
    ).fetchone()

    conn.close()

    if product is None:

        flash(
            "Product not found."
        )

        return redirect(
            url_for("admin_products")
        )

    if request.method == "POST":

        name = request.form.get(
            "name",
            ""
        ).strip()

        category = request.form.get(
            "category",
            ""
        ).strip().lower()

        description = request.form.get(
            "description",
            ""
        ).strip()

        image = request.form.get(
            "image",
            ""
        ).strip()

        try:

            price = float(
                request.form.get(
                    "price",
                    "0"
                ).replace(
                    ",",
                    ""
                )
            )

            stock = int(
                request.form.get(
                    "stock",
                    "0"
                )
            )

        except (
            ValueError,
            TypeError
        ):

            flash(
                "Invalid price or stock."
            )

            return redirect(
                url_for(
                    "edit_product",
                    product_id=product_id
                )
            )

        allowed_categories = {
            "fashion",
            "groceries",
            "electronics",
            "beauty",
            "home"
        }

        if (
            not name
            or category not in allowed_categories
            or price < 0
            or stock < 0
        ):

            flash(
                "Please enter valid product information."
            )

            return redirect(
                url_for(
                    "edit_product",
                    product_id=product_id
                )
            )

        conn = get_db()

        conn.execute(
            """
            UPDATE products
            SET
                name = ?,
                category = ?,
                price = ?,
                description = ?,
                image = ?,
                stock = ?
            WHERE id = ?
            """,
            (
                name,
                category,
                price,
                description,
                image,
                stock,
                product_id
            )
        )

        conn.commit()
        conn.close()

        flash(
            "Product updated successfully."
        )

        return redirect(
            url_for("admin_products")
        )

    return render_template(
        "admin_edit_product.html",
        product=product
    )


# ============================================================
# DELETE PRODUCT
# ============================================================

@app.post(
    "/admin/products/delete/<int:product_id>"
)
@admin_required
def delete_product(product_id):

    conn = get_db()

    product = conn.execute(
        """
        SELECT id
        FROM products
        WHERE id = ?
        """,
        (product_id,)
    ).fetchone()

    if product is None:

        conn.close()

        flash(
            "Product not found."
        )

        return redirect(
            url_for("admin_products")
        )

    order_item = conn.execute(
        """
        SELECT id
        FROM order_items
        WHERE product_id = ?
        LIMIT 1
        """,
        (product_id,)
    ).fetchone()

    if order_item:

        conn.close()

        flash(
            "This product cannot be deleted because "
            "it is already part of an order."
        )

        return redirect(
            url_for("admin_products")
        )

    conn.execute(
        """
        DELETE FROM products
        WHERE id = ?
        """,
        (product_id,)
    )

    conn.commit()
    conn.close()

    flash(
        "Product deleted successfully."
    )

    return redirect(
        url_for("admin_products")
    )


# ============================================================
# ADMIN CUSTOMERS
# ============================================================

@app.route("/admin/customers")
@admin_required
def admin_customers():

    conn = get_db()

    customers = conn.execute(
        """
        SELECT
            id,
            name,
            email,
            phone,
            address,
            email_verified,
            created_at
        FROM users
        WHERE role = 'customer'
        ORDER BY id DESC
        """
    ).fetchall()

    conn.close()

    return render_template(
        "admin_customers.html",
        customers=customers
    )


# ============================================================
# ADMIN SELLERS
# ============================================================

@app.route("/admin/sellers")
@admin_required
def admin_sellers():

    conn = get_db()

    sellers = conn.execute(
        """
        SELECT
            users.id,
            users.name,
            users.email,
            users.phone,
            users.address,
            users.created_at,
            COUNT(products.id) AS product_count
        FROM users
        LEFT JOIN products
            ON products.seller_id = users.id
        WHERE users.role = 'seller'
        GROUP BY users.id
        ORDER BY users.id DESC
        """
    ).fetchall()

    conn.close()

    return render_template(
        "admin_sellers.html",
        sellers=sellers
    )


# ============================================================
# ADMIN LOGOUT
# ============================================================

@app.route("/admin/logout")
def admin_logout():

    session.clear()

    flash(
        "You have been logged out of the admin area."
    )

    return redirect(
        url_for("home")
    )


# ============================================================
# GET PRODUCT
# ============================================================

def get_product(product_id):

    conn = get_db()

    product = conn.execute(
        """
        SELECT *
        FROM products
        WHERE id = ?
        """,
        (product_id,)
    ).fetchone()

    conn.close()

    return product


# ============================================================
# ADD TO CART
# ============================================================

@app.post(
    "/cart/add/<int:product_id>"
)
def add_to_cart(product_id):

    product = get_product(
        product_id
    )

    if product is None:

        flash(
            "Product not found."
        )

        return redirect(
            url_for("home")
        )

    if int(product["stock"]) <= 0:

        flash(
            "This product is out of stock."
        )

        return redirect_back(
            f"product-{product_id}"
        )

    cart = current_cart()

    key = str(
        product_id
    )

    try:

        current_quantity = int(
            cart.get(
                key,
                0
            )
        )

    except (
        TypeError,
        ValueError
    ):

        current_quantity = 0

    if current_quantity >= int(
        product["stock"]
    ):

        flash(
            "You cannot add more than "
            "the available stock."
        )

        return redirect_back(
            f"product-{product_id}"
        )

    cart[key] = (
        current_quantity + 1
    )

    session.modified = True

    flash(
        f"{product['name']} added to your cart."
    )

    return redirect_back(
        f"product-{product_id}"
    )


# ============================================================
# UPDATE CART
# ============================================================

@app.post(
    "/cart/update/<int:product_id>"
)
def update_cart(product_id):

    product = get_product(
        product_id
    )

    if product is None:

        flash(
            "Product not found."
        )

        return redirect(
            url_for("cart")
        )

    try:

        quantity = int(
            request.form.get(
                "quantity",
                1
            )
        )

    except (
        TypeError,
        ValueError
    ):

        quantity = 1

    cart = current_cart()

    key = str(
        product_id
    )

    if quantity <= 0:

        cart.pop(
            key,
            None
        )

    else:

        quantity = min(
            quantity,
            max(
                int(product["stock"]),
                0
            )
        )

        if quantity <= 0:

            cart.pop(
                key,
                None
            )

        else:

            cart[key] = quantity

    session.modified = True

    return redirect(
        url_for("cart")
    )


# ============================================================
# REMOVE FROM CART
# ============================================================

@app.post(
    "/cart/remove/<int:product_id>"
)
def remove_from_cart(product_id):

    cart = current_cart()

    cart.pop(
        str(product_id),
        None
    )

    session.modified = True

    flash(
        "Product removed from cart."
    )

    return redirect(
        url_for("cart")
    )


# ============================================================
# CLEAR CART
# ============================================================

@app.post("/cart/clear")
def clear_cart():

    session["cart"] = {}

    session.modified = True

    return redirect(
        url_for("cart")
    )


# ============================================================
# CART PAGE
# ============================================================

@app.route("/cart")
def cart():

    items, subtotal, count = cart_items()

    delivery = (
        0
        if subtotal == 0
        else 2500
    )

    total = (
        subtotal
        + delivery
    )

    return render_template(
        "cart.html",
        items=items,
        subtotal=subtotal,
        delivery=delivery,
        total=total,
        count=count
    )


# ============================================================
# PAYSTACK HEADERS
# ============================================================

def get_paystack_headers():

    return {
        "Authorization":
            f"Bearer {PAYSTACK_SECRET_KEY}",

        "Content-Type":
            "application/json"
    }


# ============================================================
# NAIRA TO KOBO
# ============================================================

def naira_to_kobo(amount):

    value = Decimal(
        str(amount)
    ).quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP
    )

    return int(
        value * 100
    )


# ============================================================
# CREATE PAYSTACK TRANSACTION
# ============================================================

def create_paystack_transaction(
    order_id,
    email,
    amount
):

    if not PAYSTACK_SECRET_KEY:

        raise RuntimeError(
            "PAYSTACK_SECRET_KEY is missing. "
            "Add it to your Railway Variables."
        )

    reference = (
        f"NAIJA-{order_id}-"
        f"{uuid.uuid4().hex[:12].upper()}"
    )

    payload = {
        "email": email,
        "amount": naira_to_kobo(
            amount
        ),
        "currency": "NGN",
        "reference": reference,
        "callback_url": url_for(
            "paystack_callback",
            _external=True
        ),
        "metadata": {
            "order_id": str(
                order_id
            )
        }
    }

    try:

        response = requests.post(
            PAYSTACK_INITIALIZE_URL,
            json=payload,
            headers=get_paystack_headers(),
            timeout=30
        )

    except requests.RequestException as error:

        raise RuntimeError(
            f"Could not connect to Paystack: {error}"
        ) from error

    try:

        result = response.json()

    except ValueError as error:

        raise RuntimeError(
            "Paystack returned an invalid response."
        ) from error

    if (
        response.status_code >= 400
        or not result.get("status")
    ):

        raise RuntimeError(
            result.get(
                "message",
                "Paystack could not initialize the payment."
            )
        )

    data = result.get(
        "data"
    ) or {}

    authorization_url = data.get(
        "authorization_url"
    )

    paystack_reference = data.get(
        "reference"
    )

    if (
        not authorization_url
        or not paystack_reference
    ):

        raise RuntimeError(
            "Paystack did not return a payment URL."
        )

    return (
        authorization_url,
        paystack_reference
    )


# ============================================================
# CHECKOUT
# ============================================================

@app.post("/checkout")
def checkout():

    items, _, count = cart_items()

    if not items:

        flash(
            "Your cart is empty."
        )

        return redirect(
            url_for("cart")
        )

    customer_name = request.form.get(
        "customer_name",
        ""
    ).strip()

    customer_phone = request.form.get(
        "customer_phone",
        ""
    ).strip()

    customer_email = request.form.get(
        "customer_email",
        ""
    ).strip().lower()

    customer_address = request.form.get(
        "customer_address",
        ""
    ).strip()

    payment_method = request.form.get(
        "payment_method",
        "paystack"
    ).strip().lower()

    if payment_method not in (
        "paystack",
        "cod"
    ):

        payment_method = "paystack"

    delivery_method = request.form.get(
        "delivery_method",
        "home_delivery"
    ).strip().lower()

    if delivery_method not in (
        "home_delivery",
    ):

        delivery_method = "home_delivery"

    if not customer_name:

        flash(
            "Please enter your name."
        )

        return redirect(
            url_for("cart")
        )

    if not customer_phone:

        flash(
            "Please enter your phone number."
        )

        return redirect(
            url_for("cart")
        )

    if not validate_email_with_mailboxlayer(
        customer_email
    ):

        flash(
            "Please enter a valid email address."
        )

        return redirect(
            url_for("cart")
        )

    if not customer_address:

        flash(
            "Please enter your delivery address."
        )

        return redirect(
            url_for("cart")
        )

    delivery = 2500.0

    user_id = session.get(
        "user_id"
    )

    conn = None
    order_id = None

    try:

        conn = get_db()

        conn.execute(
            "BEGIN IMMEDIATE"
        )

        verified_items = []
        authoritative_subtotal = 0.0

        for item in items:

            product_id = int(
                item["product"]["id"]
            )

            quantity = int(
                item["quantity"]
            )

            if quantity <= 0:
                continue

            product = conn.execute(
                """
                SELECT
                    id,
                    name,
                    price,
                    stock
                FROM products
                WHERE id = ?
                """,
                (product_id,)
            ).fetchone()

            if product is None:

                raise RuntimeError(
                    f"Product #{product_id} "
                    "no longer exists."
                )

            stock = int(
                product["stock"]
            )

            if stock < quantity:

                raise RuntimeError(
                    f"Not enough stock for "
                    f"{product['name']}. "
                    f"Only {stock} left."
                )

            price = float(
                product["price"]
            )

            authoritative_subtotal += (
                price * quantity
            )

            verified_items.append(
                (
                    product,
                    quantity
                )
            )

        if not verified_items:

            raise RuntimeError(
                "Your cart contains no valid products."
            )

        total = (
            authoritative_subtotal
            + delivery
        )

        cursor = conn.execute(
            """
            INSERT INTO orders
            (
                user_id,
                customer_name,
                customer_phone,
                customer_email,
                customer_address,
                delivery_address,
                subtotal,
                delivery,
                total,
                status,
                payment_status,
                payment_method,
                delivery_method
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                customer_name,
                customer_phone,
                customer_email,
                customer_address,
                customer_address,
                authoritative_subtotal,
                delivery,
                total,
                "Pending",
                "unpaid",
                payment_method,
                delivery_method
            )
        )

        order_id = cursor.lastrowid

        if not order_id:

            raise RuntimeError(
                "Unable to create order."
            )

        for product, quantity in verified_items:

            conn.execute(
                """
                INSERT INTO order_items
                (
                    order_id,
                    product_id,
                    product_name,
                    price,
                    quantity
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    order_id,
                    product["id"],
                    product["name"],
                    float(
                        product["price"]
                    ),
                    quantity
                )
            )

        # ====================================================
        # PAYMENT ON DELIVERY
        # ====================================================

        if payment_method == "cod":

            for product, quantity in verified_items:

                conn.execute(
                    """
                    UPDATE products
                    SET stock = stock - ?
                    WHERE id = ?
                    """,
                    (
                        quantity,
                        product["id"]
                    )
                )

            conn.execute(
                """
                UPDATE orders
                SET
                    status = 'Confirmed - Payment on Delivery',
                    payment_status = 'pending_cod'
                WHERE id = ?
                """,
                (order_id,)
            )

            conn.commit()
            conn.close()
            conn = None

            session["cart"] = {}

            session.pop(
                "pending_order_id",
                None
            )

            session.pop(
                "pending_payment_reference",
                None
            )

            session.modified = True

            return redirect(
                url_for(
                    "payment_success",
                    order_id=order_id
                )
            )

        # ====================================================
        # PAYSTACK
        # ====================================================

        conn.commit()

        conn.close()
        conn = None

        authorization_url, reference = (
            create_paystack_transaction(
                order_id=order_id,
                email=customer_email,
                amount=total
            )
        )

        conn = get_db()

        conn.execute(
            """
            UPDATE orders
            SET
                paystack_reference = ?,
                payment_status = 'pending'
            WHERE id = ?
            """,
            (
                reference,
                order_id
            )
        )

        conn.commit()

        conn.close()
        conn = None

        session[
            "pending_order_id"
        ] = int(
            order_id
        )

        session[
            "pending_payment_reference"
        ] = reference

        session.modified = True

        return redirect(
            authorization_url
        )

    except sqlite3.Error as error:

        if conn is not None:

            try:
                conn.rollback()
            except Exception:
                pass

            try:
                conn.close()
            except Exception:
                pass

        print(
            "SQLITE CHECKOUT ERROR:",
            error
        )

        flash(
            "Checkout database error. "
            "Please try again."
        )

        return redirect(
            url_for("cart")
        )

    except Exception as error:

        if conn is not None:

            try:
                conn.rollback()
            except Exception:
                pass

            try:
                conn.close()
            except Exception:
                pass

        print(
            "CHECKOUT / PAYMENT ERROR:",
            error
        )

        if order_id:

            try:

                conn2 = get_db()

                conn2.execute(
                    """
                    UPDATE orders
                    SET
                        payment_status = 'failed',
                        status = 'Payment Failed'
                    WHERE id = ?
                    AND payment_status != 'paid'
                    """,
                    (order_id,)
                )

                conn2.commit()
                conn2.close()

            except Exception as db_error:

                print(
                    "PAYMENT FAILURE UPDATE ERROR:",
                    db_error
                )

        flash(
            str(error)
        )

        return redirect(
            url_for("cart")
        )


# ============================================================
# PAYSTACK CALLBACK
# ============================================================

@app.route("/paystack/callback")
def paystack_callback():

    reference = request.args.get(
        "reference",
        ""
    ).strip()

    if not reference:

        flash(
            "No Paystack payment reference was received."
        )

        return redirect(
            url_for("payment_failed")
        )

    if not PAYSTACK_SECRET_KEY:

        flash(
            "Paystack is not configured on the server."
        )

        return redirect(
            url_for("payment_failed")
        )

    conn = None

    try:

        response = requests.get(
            f"{PAYSTACK_VERIFY_URL}/{reference}",
            headers={
                "Authorization":
                    f"Bearer {PAYSTACK_SECRET_KEY}"
            },
            timeout=30
        )

        try:

            result = response.json()

        except ValueError as error:

            raise RuntimeError(
                "Paystack returned an invalid "
                "verification response."
            ) from error

        if (
            response.status_code >= 400
            or not result.get("status")
        ):

            raise RuntimeError(
                result.get(
                    "message",
                    "Paystack could not verify this payment."
                )
            )

        payment = result.get(
            "data"
        ) or {}

        payment_status = str(
            payment.get(
                "status",
                ""
            )
        ).lower()

        if payment_status != "success":

            flash(
                "Payment was not successful."
            )

            return redirect(
                url_for("payment_failed")
            )

        verified_reference = str(
            payment.get(
                "reference",
                ""
            )
        ).strip()

        if verified_reference != reference:

            raise RuntimeError(
                "Payment reference verification failed."
            )

        conn = get_db()

        order = conn.execute(
            """
            SELECT *
            FROM orders
            WHERE paystack_reference = ?
            """,
            (reference,)
        ).fetchone()

        if order is None:

            conn.close()
            conn = None

            flash(
                "The payment was verified, "
                "but the order was not found."
            )

            return redirect(
                url_for("payment_failed")
            )

        if str(
            order["payment_status"]
        ).lower() == "paid":

            order_id = order["id"]

            conn.close()
            conn = None

            session["cart"] = {}

            session.pop(
                "pending_order_id",
                None
            )

            session.pop(
                "pending_payment_reference",
                None
            )

            session.modified = True

            return redirect(
                url_for(
                    "payment_success",
                    order_id=order_id
                )
            )

        expected_amount = naira_to_kobo(
            order["total"]
        )

        paid_amount = int(
            payment.get(
                "amount",
                0
            )
        )

        if paid_amount != expected_amount:

            raise RuntimeError(
                "Payment amount verification failed."
            )

        order_items = conn.execute(
            """
            SELECT
                product_id,
                product_name,
                quantity
            FROM order_items
            WHERE order_id = ?
            """,
            (order["id"],)
        ).fetchall()

        for item in order_items:

            product = conn.execute(
                """
                SELECT
                    id,
                    name,
                    stock
                FROM products
                WHERE id = ?
                """,
                (item["product_id"],)
            ).fetchone()

            if product is None:

                raise RuntimeError(
                    f"Product #{item['product_id']} "
                    "no longer exists."
                )

            if int(
                product["stock"]
            ) < int(
                item["quantity"]
            ):

                raise RuntimeError(
                    f"Not enough stock for "
                    f"{product['name']}."
                )

        for item in order_items:

            conn.execute(
                """
                UPDATE products
                SET stock = stock - ?
                WHERE id = ?
                """,
                (
                    item["quantity"],
                    item["product_id"]
                )
            )

        conn.execute(
            """
            UPDATE orders
            SET
                payment_status = 'paid',
                status = 'Processing',
                paid_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (order["id"],)
        )

        conn.commit()

        order_id = order["id"]

        conn.close()
        conn = None

        session["cart"] = {}

        session.pop(
            "pending_order_id",
            None
        )

        session.pop(
            "pending_payment_reference",
            None
        )

        session.modified = True

        return redirect(
            url_for(
                "payment_success",
                order_id=order_id
            )
        )

    except requests.RequestException as error:

        print(
            "PAYSTACK VERIFICATION REQUEST ERROR:",
            error
        )

        if conn is not None:

            try:
                conn.close()
            except Exception:
                pass

        flash(
            "Could not connect to Paystack "
            "to verify your payment."
        )

        return redirect(
            url_for("payment_failed")
        )

    except sqlite3.Error as error:

        if conn is not None:

            try:
                conn.rollback()
            except Exception:
                pass

            try:
                conn.close()
            except Exception:
                pass

        print(
            "PAYSTACK CALLBACK DATABASE ERROR:",
            error
        )

        flash(
            "There was a database error "
            "while confirming your payment."
        )

        return redirect(
            url_for("payment_failed")
        )

    except Exception as error:

        if conn is not None:

            try:
                conn.rollback()
            except Exception:
                pass

            try:
                conn.close()
            except Exception:
                pass

        print(
            "PAYSTACK CALLBACK ERROR:",
            error
        )

        flash(
            "We could not confirm your payment."
        )

        return redirect(
            url_for("payment_failed")
        )


# ============================================================
# WISHLIST
# ============================================================

@app.route("/wishlist")
@login_required
def wishlist():

    conn = get_db()

    items = conn.execute(
        """
        SELECT
            products.*,
            wishlist.id AS wishlist_id,
            wishlist.created_at AS saved_at
        FROM wishlist
        INNER JOIN products
            ON wishlist.product_id = products.id
        WHERE wishlist.user_id = ?
        ORDER BY wishlist.id DESC
        """,
        (session["user_id"],)
    ).fetchall()

    conn.close()

    return render_template(
        "wishlist.html",
        wishlist=items
    )


@app.post("/wishlist/add/<int:product_id>")
@login_required
def add_to_wishlist(product_id):

    conn = get_db()

    product = conn.execute(
        """
        SELECT id
        FROM products
        WHERE id = ?
        """,
        (product_id,)
    ).fetchone()

    if product is None:

        conn.close()

        flash(
            "Product not found."
        )

        return redirect(
            url_for("home")
        )

    conn.execute(
        """
        INSERT OR IGNORE INTO wishlist
        (user_id, product_id)
        VALUES (?, ?)
        """,
        (
            session["user_id"],
            product_id
        )
    )

    conn.commit()
    conn.close()

    flash(
        "Product added to your wishlist."
    )

    return redirect_back(
        f"product-{product_id}"
    )


@app.post("/wishlist/remove/<int:product_id>")
@login_required
def remove_from_wishlist(product_id):

    conn = get_db()

    conn.execute(
        """
        DELETE FROM wishlist
        WHERE user_id = ?
        AND product_id = ?
        """,
        (
            session["user_id"],
            product_id
        )
    )

    conn.commit()
    conn.close()

    flash(
        "Product removed from your wishlist."
    )

    return redirect(
        url_for("wishlist")
    )


@app.post("/wishlist/toggle/<int:product_id>")
@login_required
def toggle_wishlist(product_id):

    conn = get_db()

    existing = conn.execute(
        """
        SELECT id
        FROM wishlist
        WHERE user_id = ?
        AND product_id = ?
        """,
        (
            session["user_id"],
            product_id
        )
    ).fetchone()

    if existing:

        conn.execute(
            """
            DELETE FROM wishlist
            WHERE id = ?
            """,
            (existing["id"],)
        )

        message = (
            "Product removed from your wishlist."
        )

    else:

        conn.execute(
            """
            INSERT OR IGNORE INTO wishlist
            (user_id, product_id)
            VALUES (?, ?)
            """,
            (
                session["user_id"],
                product_id
            )
        )

        message = (
            "Product added to your wishlist."
        )

    conn.commit()
    conn.close()

    flash(message)

    return redirect_back(
        f"product-{product_id}"
    )


# ============================================================
# CUSTOMER REVIEWS
# ============================================================

@app.route("/reviews")
def reviews():

    conn = get_db()

    review_rows = conn.execute(
        """
        SELECT
            reviews.*,
            users.name,
            products.name AS product_name
        FROM reviews
        INNER JOIN users
            ON reviews.user_id = users.id
        INNER JOIN products
            ON reviews.product_id = products.id
        ORDER BY reviews.id DESC
        """
    ).fetchall()

    products = conn.execute(
        """
        SELECT
            id,
            name
        FROM products
        ORDER BY name COLLATE NOCASE
        """
    ).fetchall()

    conn.close()

    return render_template(
        "reviews.html",
        reviews=review_rows,
        products=products
    )


@app.post("/reviews/submit")
@login_required
def submit_review():

    try:

        product_id = int(
            request.form.get(
                "product_id",
                "0"
            )
        )

        rating = int(
            request.form.get(
                "rating",
                "0"
            )
        )

    except (
        ValueError,
        TypeError
    ):

        flash(
            "Please select a valid product and rating."
        )

        return redirect(
            url_for("reviews")
        )

    title = request.form.get(
        "title",
        ""
    ).strip()

    comment = request.form.get(
        "comment",
        ""
    ).strip()

    if not 1 <= rating <= 5:

        flash(
            "Please select a rating from 1 to 5 stars."
        )

        return redirect(
            url_for("reviews")
        )

    if not title or not comment:

        flash(
            "Please provide a review title and comment."
        )

        return redirect(
            url_for("reviews")
        )

    conn = get_db()

    product = conn.execute(
        """
        SELECT
            id
        FROM products
        WHERE id = ?
        """,
        (product_id,)
    ).fetchone()

    if product is None:

        conn.close()

        flash(
            "Product not found."
        )

        return redirect(
            url_for("reviews")
        )

    purchased = conn.execute(
        """
        SELECT 1
        FROM orders
        INNER JOIN order_items
            ON orders.id = order_items.order_id
        WHERE orders.user_id = ?
        AND order_items.product_id = ?
        AND orders.payment_status IN
            ('paid', 'pending_cod')
        LIMIT 1
        """,
        (
            session["user_id"],
            product_id
        )
    ).fetchone()

    if purchased is None:

        conn.close()

        flash(
            "You can only review products you have purchased."
        )

        return redirect(
            url_for("reviews")
        )

    already_reviewed = conn.execute(
        """
        SELECT id
        FROM reviews
        WHERE user_id = ?
        AND product_id = ?
        """,
        (
            session["user_id"],
            product_id
        )
    ).fetchone()

    if already_reviewed:

        conn.close()

        flash(
            "You have already reviewed this product."
        )

        return redirect(
            url_for("reviews")
        )

    conn.execute(
        """
        INSERT INTO reviews
        (
            user_id,
            product_id,
            rating,
            title,
            comment
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            session["user_id"],
            product_id,
            rating,
            title,
            comment
        )
    )

    conn.commit()

    new_review = conn.execute(
        """
        SELECT id
        FROM reviews
        WHERE user_id = ?
        AND product_id = ?
        ORDER BY id DESC
        LIMIT 1
        """,
        (
            session["user_id"],
            product_id
        )
    ).fetchone()

    conn.close()

    flash(
        "Thank you! Your review has been submitted."
    )

    if new_review:

        return redirect(
            url_for("reviews")
            + f"#review-{new_review['id']}"
        )

    return redirect(
        url_for("reviews")
        + "#reviews"
    )


# ============================================================
# HOME DELIVERY
# ============================================================

@app.route("/delivery")
def delivery_page():

    return render_template(
        "delivery.html"
    )


# ============================================================
# PAYMENT ON DELIVERY
# ============================================================

@app.route("/payment-on-delivery")
def payment_on_delivery():

    return render_template(
        "payment_on_delivery.html"
    )


# ============================================================
# PAYMENT SUCCESS
# ============================================================

@app.route(
    "/payment-success/<int:order_id>"
)
def payment_success(order_id):

    conn = get_db()

    order = conn.execute(
        """
        SELECT *
        FROM orders
        WHERE id = ?
        """,
        (order_id,)
    ).fetchone()

    items = conn.execute(
        """
        SELECT *
        FROM order_items
        WHERE order_id = ?
        ORDER BY id
        """,
        (order_id,)
    ).fetchall()

    conn.close()

    if order is None:

        flash(
            "Order not found."
        )

        return redirect(
            url_for("home")
        )

    return render_template(
        "payment_success.html",
        order=order,
        items=items
    )


# ============================================================
# PAYMENT FAILED
# ============================================================

@app.route("/payment-failed")
def payment_failed():

    return render_template(
        "payment_failed.html"
    )


# ============================================================
# PAYMENT CANCELLED
# ============================================================

@app.route(
    "/payment-cancelled/<int:order_id>"
)
def payment_cancelled(order_id):

    conn = get_db()

    conn.execute(
        """
        UPDATE orders
        SET
            payment_status = 'cancelled',
            status = 'Payment Cancelled'
        WHERE id = ?
        AND payment_status != 'paid'
        """,
        (order_id,)
    )

    conn.commit()
    conn.close()

    flash(
        "Payment was cancelled."
    )

    return redirect(
        url_for("cart")
    )


# ============================================================
# INITIALIZE DATABASE
# ============================================================

init_db()


# ============================================================
# RUN APPLICATION
# ============================================================

if __name__ == "__main__":

    port = int(
        os.environ.get(
            "PORT",
            "5000"
        )
    )

    print()
    print("=" * 70)
    print("                         NAIJACART")
    print("=" * 70)

    print()
    print("DATABASE")
    print("-" * 70)

    print(
        f"Database: {DATABASE}"
    )

    print()
    print("PAYSTACK")
    print("-" * 70)

    print(
        "Paystack configured:",
        "YES"
        if PAYSTACK_SECRET_KEY
        else "NO"
    )

    print()
    print("MAILBOXLAYER")
    print("-" * 70)

    print(
        "Mailboxlayer configured:",
        "YES"
        if MAILBOXLAYER_ACCESS_KEY
        else "NO"
    )

    print()
    print("RESEND")
    print("-" * 70)

    print(
        "Resend configured:",
        "YES"
        if RESEND_API_KEY and RESEND_FROM_EMAIL
        else "NO"
    )

    print(
        "Resend From Email:",
        RESEND_FROM_EMAIL or "NOT SET"
    )

    print(
        "Resend From Name:",
        RESEND_FROM_NAME
    )

    print()
    print("WEBSITE")
    print("-" * 70)

    print(
        f"Port: {port}"
    )

    print()
    print("=" * 70)
    print("NaijaCart server is running.")
    print("=" * 70)
    print()

    app.run(
        debug=False,
        host="0.0.0.0",
        port=port
    )