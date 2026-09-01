import sqlite3
from pathlib import Path
from werkzeug.security import generate_password_hash

# ============================================================
# NAIJACART - SEED DATABASE
# Run:
#     python seed.py
#
# This creates database/max.db and inserts the 50 products.
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
DATABASE_DIR = BASE_DIR / "database"
DATABASE_DIR.mkdir(exist_ok=True)
DATABASE = DATABASE_DIR / "max.db"

conn = sqlite3.connect(DATABASE)
conn.execute("PRAGMA foreign_keys = ON")

# ------------------------------------------------------------
# TABLES
# ------------------------------------------------------------

conn.executescript("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    phone TEXT,
    address TEXT,
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
    stock INTEGER NOT NULL DEFAULT 10,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (seller_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    customer_name TEXT NOT NULL,
    customer_phone TEXT NOT NULL,
    customer_email TEXT NOT NULL,
    delivery_address TEXT NOT NULL,
    subtotal REAL NOT NULL,
    delivery REAL NOT NULL,
    total REAL NOT NULL,
    status TEXT NOT NULL DEFAULT 'Pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS order_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    product_name TEXT NOT NULL,
    price REAL NOT NULL,
    quantity INTEGER NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id)
);
""")

# ------------------------------------------------------------
# CREATE SELLER
# ------------------------------------------------------------

seller = conn.execute(
    "SELECT id FROM users WHERE email = ?",
    ("seller@naijacart.local",)
).fetchone()

if seller:
    seller_id = seller[0]
else:
    cursor = conn.execute(
        """
        INSERT INTO users
        (name, email, password, phone, address)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            "NaijaCart Seller",
            "seller@naijacart.local",
            generate_password_hash("seller123"),
            "08000000000",
            "Lagos, Nigeria"
        )
    )
    seller_id = cursor.lastrowid

# ------------------------------------------------------------
# YOUR 50 PRODUCTS
# ------------------------------------------------------------

products = [
    (1, "Ankara Shirt", "fashion", 8500, "Quality Ankara shirt", "https://images.unsplash.com/photo-1551488831-00ddcb6c6bd3?auto=format&fit=crop&w=700&q=80", 10),
    (2, "Ankara Trousers", "fashion", 10000, "Quality Ankara trousers", "https://images.unsplash.com/photo-1594633312681-425c7b97ccd1?auto=format&fit=crop&w=700&q=80", 10),
    (3, "Native Kaftan", "fashion", 18000, "Quality native kaftan", "https://images.unsplash.com/photo-1594938298603-c8148c4dae35?auto=format&fit=crop&w=700&q=80", 10),
    (4, "Agbada Set", "fashion", 35000, "Quality Nigerian Agbada set", "https://images.unsplash.com/photo-1603252110481-7ba873bf42ab?auto=format&fit=crop&w=700&q=80", 10),
    (5, "Polo Shirt", "fashion", 7500, "Quality polo shirt", "https://images.unsplash.com/photo-1576566588028-4147f3842f27?auto=format&fit=crop&w=700&q=80", 10),
    (6, "Denim Jeans", "fashion", 12000, "Quality denim jeans", "https://images.unsplash.com/photo-1523381210434-271e8be1f52b?auto=format&fit=crop&w=700&q=80", 10),
    (7, "Sneakers", "fashion", 25000, "Quality sneakers", "https://images.unsplash.com/photo-1542291026-7eec264c27ff?auto=format&fit=crop&w=700&q=80", 10),
    (8, "Leather Sandals", "fashion", 12000, "Quality leather sandals", "https://images.unsplash.com/photo-1549298916-b41d501d3772?auto=format&fit=crop&w=700&q=80", 10),
    (9, "Crossbody Bag", "fashion", 15000, "Quality crossbody bag", "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?auto=format&fit=crop&w=700&q=80", 10),
    (10, "Wrist Watch", "fashion", 18000, "Quality wrist watch", "https://images.unsplash.com/photo-1523170335258-f5ed11844a49?auto=format&fit=crop&w=700&q=80", 10),

    (11, "Premium Rice 5kg", "groceries", 8500, "Premium Nigerian rice 5kg", "https://images.unsplash.com/photo-1586201375761-83865001e31c?auto=format&fit=crop&w=700&q=80", 10),
    (12, "Premium Rice 10kg", "groceries", 16500, "Premium Nigerian rice 10kg", "https://images.unsplash.com/photo-1586201375761-83865001e31c?auto=format&fit=crop&w=700&q=80", 10),
    (13, "Spaghetti Pack", "groceries", 1200, "Quality spaghetti pack", "https://images.unsplash.com/photo-1551462147-ff29053bfc14?auto=format&fit=crop&w=700&q=80", 10),
    (14, "Indomie Noodles", "groceries", 850, "Instant noodles", "https://images.unsplash.com/photo-1569718212165-3a8278d5f624?auto=format&fit=crop&w=700&q=80", 10),
    (15, "Semovita 2kg", "groceries", 3500, "Semovita 2kg pack", "https://images.unsplash.com/photo-1586201375761-83865001e31c?auto=format&fit=crop&w=700&q=80", 10),
    (16, "Garri Ijebu", "groceries", 2500, "Premium Garri Ijebu", "https://images.unsplash.com/photo-1601050690597-df0568f70950?auto=format&fit=crop&w=700&q=80", 10),
    (17, "Palm Oil 1L", "groceries", 2500, "Pure palm oil 1 litre", "https://images.unsplash.com/photo-1601050690117-94f5f6fa8bd7?auto=format&fit=crop&w=700&q=80", 10),
    (18, "Vegetable Oil 1L", "groceries", 3000, "Vegetable cooking oil", "https://images.unsplash.com/photo-1601050690597-df0568f70950?auto=format&fit=crop&w=700&q=80", 10),
    (19, "Tomato Paste", "groceries", 1800, "Quality tomato paste", "https://images.unsplash.com/photo-1546470427-e26264be0b0d?auto=format&fit=crop&w=700&q=80", 10),
    (20, "Golden Morn", "groceries", 3500, "Golden Morn cereal", "https://images.unsplash.com/photo-1517093157656-b9eccef91cb1?auto=format&fit=crop&w=700&q=80", 10),

    (21, "Samsung Galaxy A15", "electronics", 285000, "128GB smartphone with excellent battery life", "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?auto=format&fit=crop&w=700&q=80", 10),
    (22, "Redmi Smartphone", "electronics", 180000, "Quality Redmi smartphone", "https://images.unsplash.com/photo-1598327105666-5b89351aff97?auto=format&fit=crop&w=700&q=80", 10),
    (23, "Tecno Spark", "electronics", 195000, "Tecno Spark smartphone", "https://images.unsplash.com/photo-1592899677977-9c10ca588bbd?auto=format&fit=crop&w=700&q=80", 10),
    (24, "Infinix Hot", "electronics", 210000, "Infinix Hot smartphone", "https://images.unsplash.com/photo-1592899677977-9c10ca588bbd?auto=format&fit=crop&w=700&q=80", 10),
    (25, "HP Laptop", "electronics", 450000, "HP laptop computer", "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?auto=format&fit=crop&w=700&q=80", 10),
    (26, "Dell Laptop", "electronics", 520000, "Dell laptop computer", "https://images.unsplash.com/photo-1593642702821-c8da6771f0c6?auto=format&fit=crop&w=700&q=80", 10),
    (27, "Bluetooth Earbuds", "electronics", 18000, "Wireless Bluetooth earbuds", "https://images.unsplash.com/photo-1606220945770-b5b6c2c55bf1?auto=format&fit=crop&w=700&q=80", 10),
    (28, "Bluetooth Speaker", "electronics", 25000, "Portable Bluetooth speaker", "https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?auto=format&fit=crop&w=700&q=80", 10),
    (29, "Power Bank 20000mAh", "electronics", 30000, "20000mAh portable power bank", "https://images.unsplash.com/photo-1609592424937-3f9c7f5f1c8a?auto=format&fit=crop&w=700&q=80", 10),
    (30, "Fast Phone Charger", "electronics", 12000, "Fast charging phone adapter", "https://images.unsplash.com/photo-1583863788434-e58a36330cf0?auto=format&fit=crop&w=700&q=80", 10),

    (31, "Face Wash", "beauty", 5000, "Gentle facial face wash", "https://images.unsplash.com/photo-1556228578-8c89e6adf883?auto=format&fit=crop&w=700&q=80", 10),
    (32, "Face Moisturizer", "beauty", 7500, "Daily face moisturizer", "https://images.unsplash.com/photo-1571781926291-c477ebfd024b?auto=format&fit=crop&w=700&q=80", 10),
    (33, "Vitamin C Serum", "beauty", 9000, "Vitamin C facial serum", "https://images.unsplash.com/photo-1598440947619-2c35fc9aa908?auto=format&fit=crop&w=700&q=80", 10),
    (34, "Sunscreen", "beauty", 8500, "Daily sunscreen", "https://images.unsplash.com/photo-1556229010-6c3f2c9c4c3a?auto=format&fit=crop&w=700&q=80", 10),
    (35, "Body Lotion", "beauty", 6000, "Moisturizing body lotion", "https://images.unsplash.com/photo-1556228720-195a672e8a03?auto=format&fit=crop&w=700&q=80", 10),
    (36, "Body Spray", "beauty", 7000, "Fresh body spray", "https://images.unsplash.com/photo-1541643600914-78b084683601?auto=format&fit=crop&w=700&q=80", 10),
    (37, "Perfume", "beauty", 15000, "Quality perfume", "https://images.unsplash.com/photo-1594035910387-fea47794261f?auto=format&fit=crop&w=700&q=80", 10),
    (38, "Hair Shampoo", "beauty", 5500, "Quality hair shampoo", "https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?auto=format&fit=crop&w=700&q=80", 10),
    (39, "Hair Conditioner", "beauty", 6000, "Hair conditioning product", "https://images.unsplash.com/photo-1595476108010-b4d1f102b1b1?auto=format&fit=crop&w=700&q=80", 10),
    (40, "Makeup Brush Set", "beauty", 10000, "Professional makeup brush set", "https://images.unsplash.com/photo-1596462502278-27bfdc403348?auto=format&fit=crop&w=700&q=80", 10),

    (41, "Sofa", "home", 250000, "Comfortable living room sofa", "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?auto=format&fit=crop&w=700&q=80", 10),
    (42, "Office Chair", "home", 65000, "Comfortable office chair", "https://images.unsplash.com/photo-1586023492125-27b2c045efd7?auto=format&fit=crop&w=700&q=80", 10),
    (43, "Bed Frame", "home", 150000, "Strong bed frame", "https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?auto=format&fit=crop&w=700&q=80", 10),
    (44, "Mattress", "home", 120000, "Comfortable mattress", "https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?auto=format&fit=crop&w=700&q=80", 10),
    (45, "Bedsheet Set", "home", 18000, "Quality bedsheet set", "https://images.unsplash.com/photo-1616486338812-3dadae4b4ace?auto=format&fit=crop&w=700&q=80", 10),
    (46, "Dining Table", "home", 120000, "Modern dining table", "https://images.unsplash.com/photo-1556912167-f556f1f39fdf?auto=format&fit=crop&w=700&q=80", 10),
    (47, "Kitchen Knife Set", "home", 15000, "Kitchen knife set", "https://images.unsplash.com/photo-1556910103-1c02745aae4d?auto=format&fit=crop&w=700&q=80", 10),
    (48, "Blender", "home", 35000, "Electric kitchen blender", "https://images.unsplash.com/photo-1570222094114-d054a817e56b?auto=format&fit=crop&w=700&q=80", 10),
    (49, "Electric Kettle", "home", 18000, "Electric water kettle", "https://images.unsplash.com/photo-1594212699903-ec8a3eca50f5?auto=format&fit=crop&w=700&q=80", 10),
    (50, "Standing Fan", "home", 45000, "Standing electric fan", "https://images.unsplash.com/photo-1527434000150-9f8e0f7e5e4b?auto=format&fit=crop&w=700&q=80", 10),
]

# ------------------------------------------------------------
# INSERT / UPDATE THE 50 PRODUCTS
# ------------------------------------------------------------

# Delete only the products previously seeded by this script,
# then insert the exact 50 products with IDs 1-50.
conn.execute("DELETE FROM products")

conn.executemany(
    """
    INSERT INTO products
    (id, name, category, price, description, image, seller_id, stock)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """,
    [
        (
            product_id,
            name,
            category,
            price,
            description,
            image,
            seller_id,
            stock
        )
        for product_id, name, category, price, description, image, stock
        in products
    ]
)

conn.commit()

# ------------------------------------------------------------
# CHECK RESULT
# ------------------------------------------------------------

total = conn.execute(
    "SELECT COUNT(*) FROM products"
).fetchone()[0]

print()
print("==========================================")
print("       NAIJACART DATABASE SEEDED")
print("==========================================")
print(f"Database: {DATABASE}")
print(f"Products inserted: {total}")
print("Fashion:     10")
print("Groceries:   10")
print("Electronics: 10")
print("Beauty:      10")
print("Home:        10")
print("==========================================")

conn.close()