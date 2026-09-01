import sqlite3
from pathlib import Path

# ============================================================
# DATABASE
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
DATABASE = BASE_DIR / "database" / "naijacart.db"

DATABASE.parent.mkdir(parents=True, exist_ok=True)


# ============================================================
# PRODUCTS
# ============================================================

products = [

    # ========================================================
    # FASHION
    # ========================================================

    (
        "Men's Ankara Shirt",
        "fashion",
        18000,
        "Beautiful Nigerian Ankara shirt suitable for casual and traditional occasions.",
        "https://images.unsplash.com/photo-1596755389378-c31d21fd1273",
        50
    ),

    (
        "Women's Ankara Dress",
        "fashion",
        28000,
        "Stylish Ankara dress made for Nigerian occasions and everyday fashion.",
        "https://images.unsplash.com/photo-1585488433567-4d7b7f8f3f2f",
        35
    ),

    (
        "Men's Native Senator Wear",
        "fashion",
        35000,
        "Classic Nigerian senator outfit with a modern design.",
        "https://images.unsplash.com/photo-1617127365659-c47fa864d8bc",
        25
    ),

    (
        "Unisex Sneakers",
        "fashion",
        32000,
        "Comfortable sneakers suitable for everyday activities.",
        "https://images.unsplash.com/photo-1542291026-7eec264c27ff",
        40
    ),

    (
        "Leather Crossbody Bag",
        "fashion",
        22000,
        "Premium-looking crossbody bag for everyday use.",
        "https://images.unsplash.com/photo-1553062407-98eeb64c6a62",
        30
    ),

    (
        "Men's Polo Shirt",
        "fashion",
        12000,
        "Comfortable polo shirt suitable for casual outings.",
        "https://images.unsplash.com/photo-1625910513413-5fc45b8c0f9f",
        60
    ),

    (
        "Women's Handbag",
        "fashion",
        25000,
        "Elegant handbag suitable for everyday use.",
        "https://images.unsplash.com/photo-1584917865442-de89df76afd3",
        20
    ),

    (
        "Baseball Cap",
        "fashion",
        7000,
        "Simple stylish cap for everyday wear.",
        "https://images.unsplash.com/photo-1521369909029-2afed882baee",
        80
    ),

    (
        "Traditional Nigerian Cap",
        "fashion",
        9000,
        "Classic Nigerian traditional cap.",
        "https://images.unsplash.com/photo-1520975958225-1f61d5a8e4e6",
        45
    ),

    (
        "Women's Casual Sneakers",
        "fashion",
        28000,
        "Comfortable casual sneakers for everyday activities.",
        "https://images.unsplash.com/photo-1543163521-1bf539c55dd2",
        35
    ),


    # ========================================================
    # GROCERIES
    # ========================================================

    (
        "Premium Nigerian Rice 5kg",
        "groceries",
        9500,
        "Premium quality Nigerian rice.",
        "https://images.unsplash.com/photo-1586201375761-83865001e31c",
        100
    ),

    (
        "Beans 5kg",
        "groceries",
        8500,
        "Clean Nigerian beans suitable for household cooking.",
        "https://images.unsplash.com/photo-1551462147-37885acc36f1",
        90
    ),

    (
        "Garri 5kg",
        "groceries",
        6500,
        "High-quality cassava garri.",
        "https://images.unsplash.com/photo-1604908177522-402f4a0c6f4f",
        100
    ),

    (
        "Palm Oil 1 Litre",
        "groceries",
        4500,
        "Fresh Nigerian palm oil for cooking.",
        "https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5",
        70
    ),

    (
        "Groundnut Oil 1 Litre",
        "groceries",
        5000,
        "Quality cooking oil for everyday meals.",
        "https://images.unsplash.com/photo-1620706857370-ff1de0f8d9a3",
        70
    ),

    (
        "Indomie Instant Noodles",
        "groceries",
        8500,
        "Popular instant noodles for quick meals.",
        "https://images.unsplash.com/photo-1569718212165-3a8278d5f624",
        120
    ),

    (
        "Golden Morn Cereal",
        "groceries",
        5500,
        "Popular Nigerian breakfast cereal.",
        "https://images.unsplash.com/photo-1517686469429-8bdb88b9f907",
        60
    ),

    (
        "Tomato Paste Pack",
        "groceries",
        4000,
        "Quality tomato paste for cooking.",
        "https://images.unsplash.com/photo-1547592180-85f173990554",
        80
    ),

    (
        "Nigerian Honey",
        "groceries",
        7000,
        "Natural Nigerian honey.",
        "https://images.unsplash.com/photo-1587049352846-4a222e784d38",
        50
    ),

    (
        "Bottled Water Pack",
        "groceries",
        3000,
        "Pack of bottled drinking water.",
        "https://images.unsplash.com/photo-1548839140-29a749e1cf4d",
        150
    ),


    # ========================================================
    # ELECTRONICS
    # ========================================================

    (
        "Wireless Bluetooth Earbuds",
        "electronics",
        18000,
        "Wireless Bluetooth earbuds with a compact charging case.",
        "https://images.unsplash.com/photo-1590658268037-6bf12165a8df",
        50
    ),

    (
        "Power Bank 20000mAh",
        "electronics",
        25000,
        "High-capacity power bank for phones and other devices.",
        "https://images.unsplash.com/photo-1609592424859-16f3e4e6c5a2",
        45
    ),

    (
        "USB-C Fast Charger",
        "electronics",
        12000,
        "Fast USB-C charger for compatible smartphones and devices.",
        "https://images.unsplash.com/photo-1583863788434-e58a36330cf0",
        70
    ),

    (
        "Bluetooth Speaker",
        "electronics",
        22000,
        "Portable Bluetooth speaker with powerful sound.",
        "https://images.unsplash.com/photo-1608043152269-423dbba4e7e1",
        40
    ),

    (
        "Smart Watch",
        "electronics",
        30000,
        "Modern smartwatch with useful everyday features.",
        "https://images.unsplash.com/photo-1523275335684-37898b6baf30",
        35
    ),

    (
        "Wireless Keyboard",
        "electronics",
        18000,
        "Wireless keyboard for computers and laptops.",
        "https://images.unsplash.com/photo-1587829741301-dc798b83add3",
        30
    ),

    (
        "Wireless Mouse",
        "electronics",
        9000,
        "Comfortable wireless mouse for everyday computer use.",
        "https://images.unsplash.com/photo-1527814050087-3793815479db",
        55
    ),

    (
        "LED Ring Light",
        "electronics",
        15000,
        "LED ring light suitable for content creation and video calls.",
        "https://images.unsplash.com/photo-1611532736597-de2d4265fba3",
        40
    ),

    (
        "Phone Tripod",
        "electronics",
        10000,
        "Adjustable tripod for smartphones.",
        "https://images.unsplash.com/photo-1593697821252-0c9137d9fc45",
        50
    ),

    (
        "Laptop Backpack",
        "electronics",
        20000,
        "Protective backpack suitable for laptops and accessories.",
        "https://images.unsplash.com/photo-1553062407-98eeb64c6a62",
        30
    ),


    # ========================================================
    # BEAUTY
    # ========================================================

    (
        "Body Lotion",
        "beauty",
        7500,
        "Moisturising body lotion for everyday skincare.",
        "https://images.unsplash.com/photo-1556228578-8c89e6adf883",
        70
    ),

    (
        "Face Moisturizer",
        "beauty",
        9000,
        "Daily facial moisturiser.",
        "https://images.unsplash.com/photo-1556228720-195a672e8a03",
        50
    ),

    (
        "Perfume",
        "beauty",
        18000,
        "Elegant fragrance suitable for everyday wear.",
        "https://images.unsplash.com/photo-1541643600914-78b084683601",
        45
    ),

    (
        "Lip Gloss",
        "beauty",
        5000,
        "Glossy lip product suitable for everyday makeup.",
        "https://images.unsplash.com/photo-1586495777744-4413f21062fa",
        80
    ),

    (
        "Makeup Brush Set",
        "beauty",
        12000,
        "Complete makeup brush set.",
        "https://images.unsplash.com/photo-1596462502278-27bfdc403348",
        40
    ),

    (
        "Hair Conditioner",
        "beauty",
        6500,
        "Hair conditioner for everyday hair care.",
        "https://images.unsplash.com/photo-1522338242992-e1a54906a8da",
        55
    ),

    (
        "Shampoo",
        "beauty",
        6000,
        "Gentle shampoo for everyday hair washing.",
        "https://images.unsplash.com/photo-1535585209827-a15fcdbc4c2d",
        60
    ),

    (
        "Body Spray",
        "beauty",
        8000,
        "Fresh everyday body spray.",
        "https://images.unsplash.com/photo-1594035910387-fea47794261f",
        50
    ),

    (
        "Skincare Set",
        "beauty",
        22000,
        "Skincare set containing everyday skincare products.",
        "https://images.unsplash.com/photo-1556229010-aa3f7ff66b06",
        30
    ),

    (
        "Hair Brush",
        "beauty",
        4500,
        "Durable hair brush for everyday styling.",
        "https://images.unsplash.com/photo-1522337360788-8b13dee7a37e",
        70
    ),


    # ========================================================
    # HOME
    # ========================================================

    (
        "Non-Stick Frying Pan",
        "home",
        18000,
        "Durable non-stick frying pan for everyday cooking.",
        "https://images.unsplash.com/photo-1556911220-bff31c812dba",
        35
    ),

    (
        "Kitchen Knife Set",
        "home",
        16000,
        "Kitchen knife set for everyday food preparation.",
        "https://images.unsplash.com/photo-1593618998160-e34014e67546",
        30
    ),

    (
        "Bedsheet Set",
        "home",
        22000,
        "Comfortable bedsheet set for your bedroom.",
        "https://images.unsplash.com/photo-1616627547584-bf28cee262db",
        40
    ),

    (
        "Throw Pillow",
        "home",
        6500,
        "Decorative throw pillow for your home.",
        "https://images.unsplash.com/photo-1584100936595-c0654b55a2a2",
        50
    ),

    (
        "Table Lamp",
        "home",
        14000,
        "Modern table lamp for bedrooms and living spaces.",
        "https://images.unsplash.com/photo-1507473885765-e6ed057f782c",
        35
    ),

    (
        "Wall Clock",
        "home",
        10000,
        "Simple wall clock for home decoration.",
        "https://images.unsplash.com/photo-1563861826100-9cb868fdbe1c",
        45
    ),

    (
        "Laundry Basket",
        "home",
        8500,
        "Strong laundry basket for household use.",
        "https://images.unsplash.com/photo-1582735689369-4fe89db7114c",
        40
    ),

    (
        "Water Bottle",
        "home",
        5000,
        "Reusable water bottle for everyday use.",
        "https://images.unsplash.com/photo-1602143407151-7111542de6e8",
        80
    ),

    (
        "Storage Box",
        "home",
        7500,
        "Useful storage box for organising household items.",
        "https://images.unsplash.com/photo-1586023492125-27b2c045efd7",
        60
    ),

    (
        "Dining Plate Set",
        "home",
        18000,
        "Complete dining plate set for your home.",
        "https://images.unsplash.com/photo-1603199506016-b9a594b593c0",
        35
    )

]


# ============================================================
# CONNECT
# ============================================================

conn = sqlite3.connect(str(DATABASE))

cursor = conn.cursor()


# ============================================================
# MAKE SURE USERS TABLE EXISTS
# ============================================================

cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        phone TEXT,
        address TEXT,
        role TEXT NOT NULL DEFAULT 'customer',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")


# ============================================================
# MAKE SURE PRODUCTS TABLE EXISTS
# ============================================================

cursor.execute("""
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
    )
""")


# ============================================================
# CREATE SELLER
# ============================================================

from werkzeug.security import generate_password_hash


seller_email = "seller@naijacart.local"

seller = cursor.execute(
    """
    SELECT id
    FROM users
    WHERE email = ?
    """,
    (seller_email,)
).fetchone()


if seller is None:

    cursor.execute(
        """
        INSERT INTO users
        (
            name,
            email,
            password,
            role
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            "NaijaCart Seller",
            seller_email,
            generate_password_hash("admin123"),
            "seller"
        )
    )

    seller_id = cursor.lastrowid

else:

    seller_id = seller[0]


# ============================================================
# INSERT PRODUCTS
# ============================================================

added = 0
skipped = 0


for product in products:

    name, category, price, description, image, stock = product

    # Prevent duplicate products
    existing = cursor.execute(
        """
        SELECT id
        FROM products
        WHERE name = ?
        AND category = ?
        """,
        (name, category)
    ).fetchone()


    if existing:

        skipped += 1
        continue


    cursor.execute(
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
            seller_id,
            stock
        )
    )

    added += 1


# ============================================================
# SAVE
# ============================================================

conn.commit()


# ============================================================
# SHOW RESULT
# ============================================================

total = cursor.execute(
    "SELECT COUNT(*) FROM products"
).fetchone()[0]


print()
print("============================================")
print("       NAIJACART PRODUCTS ADDED")
print("============================================")
print()
print(f"Products added : {added}")
print(f"Products skipped: {skipped}")
print(f"Total products : {total}")
print()
print(f"Database       : {DATABASE}")
print()
print("Categories:")
print("  Fashion")
print("  Groceries")
print("  Electronics")
print("  Beauty")
print("  Home")
print()
print("Seller account:")
print("  Email    : seller@naijacart.local")
print("  Password : admin123")
print()
print("============================================")
print()


conn.close()