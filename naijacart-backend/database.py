import sqlite3

DB_PATH = "./database/naijart.db"

products = {

    "fashion": [
        ("Ankara Shirt", 8500),
        ("Ankara Trousers", 10000),
        ("Native Kaftan", 18000),
        ("Agbada Set", 35000),
        ("Polo Shirt", 7500),
        ("Denim Jeans", 12000),
        ("Sneakers", 25000),
        ("Leather Sandals", 12000),
        ("Crossbody Bag", 15000),
        ("Wrist Watch", 18000),
    ],

    "groceries": [
        ("Premium Rice 5kg", 8500),
        ("Premium Rice 10kg", 16500),
        ("Spaghetti Pack", 1200),
        ("Indomie Noodles", 850),
        ("Semovita 2kg", 3500),
        ("Garri Ijebu", 2500),
        ("Palm Oil 1L", 2500),
        ("Vegetable Oil 1L", 3000),
        ("Tomato Paste", 1800),
        ("Golden Morn", 3500),
    ],

    "electronics": [
        ("Samsung Galaxy A15", 285000),
        ("Redmi Smartphone", 180000),
        ("Tecno Spark", 195000),
        ("Infinix Hot", 210000),
        ("HP Laptop", 450000),
        ("Dell Laptop", 520000),
        ("Bluetooth Earbuds", 18000),
        ("Bluetooth Speaker", 25000),
        ("Power Bank 20000mAh", 30000),
        ("Fast Phone Charger", 12000),
    ],

    "beauty": [
        ("Face Wash", 5000),
        ("Face Moisturizer", 7500),
        ("Vitamin C Serum", 9000),
        ("Sunscreen", 8500),
        ("Body Lotion", 6000),
        ("Body Spray", 7000),
        ("Perfume", 15000),
        ("Hair Shampoo", 5500),
        ("Hair Conditioner", 6000),
        ("Makeup Brush Set", 10000),
    ],

    "home": [
        ("Sofa", 250000),
        ("Office Chair", 65000),
        ("Bed Frame", 150000),
        ("Mattress", 120000),
        ("Bedsheet Set", 18000),
        ("Dining Table", 120000),
        ("Kitchen Knife Set", 15000),
        ("Blender", 35000),
        ("Electric Kettle", 18000),
        ("Standing Fan", 45000),
    ]
}


def get_image(category, index):
    images = {
        "fashion": [
            "https://images.unsplash.com/photo-1551488831-00ddcb6c6bd3?auto=format&fit=crop&w=700&q=80"
        ],

        "groceries": [
            "https://images.unsplash.com/photo-1586201375761-83865001e31c?auto=format&fit=crop&w=700&q=80"
        ],

        "electronics": [
            "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?auto=format&fit=crop&w=700&q=80"
        ],

        "beauty": [
            "https://images.unsplash.com/photo-1556228578-8c89e6adf883?auto=format&fit=crop&w=700&q=80"
        ],

        "home": [
            "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?auto=format&fit=crop&w=700&q=80"
        ]
    }

    return images[category][index % len(images[category])]


def seed_products():

    conn = sqlite3.connect(DB_PATH)

    conn.execute("PRAGMA foreign_keys = ON")

    cursor = conn.cursor()

    # Make sure the seller exists
    cursor.execute("""
        INSERT OR IGNORE INTO sellers
        (id, name, email)
        VALUES (?, ?, ?)
    """, (
        1,
        "NaijaCart Seller",
        "seller@naijacart.com"
    ))

    # Remove old products
    cursor.execute("DELETE FROM products")

    total = 0

    for category, category_products in products.items():

        for index, (name, price) in enumerate(category_products):

            description = (
                f"Quality {name.lower()} "
                f"available from a trusted Nigerian seller."
            )

            image = get_image(category, index)

            cursor.execute("""
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
            """, (
                name,
                category,
                price,
                description,
                image,
                1,
                10
            ))

            total += 1

    conn.commit()

    print("================================")
    print("NAIJACART PRODUCTS")
    print("================================")
    print(f"Products inserted: {total}")
    print("Fashion:      10")
    print("Groceries:    10")
    print("Electronics:  10")
    print("Beauty:       10")
    print("Home:         10")
    print("All Products: 50")
    print("================================")

    conn.close()


if __name__ == "__main__":
    seed_products()