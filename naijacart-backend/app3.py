from flask import Flask, render_template, request, url_for

app = Flask(__name__)


# =========================
# HOME PAGE
# =========================
@app.route("/")
def home():
    return render_template("index.html", shop="NaijaCart")


# =========================
# ABOUT PAGE
# =========================
@app.route("/about")
def about():
    return "About NaijaCart"


# =========================
# CONTACT PAGE
# =========================
@app.route("/contact")
def contact():
    return "Reach us in Lagos"


# =========================
# SINGLE PRODUCT
# Example: /product/rice
# =========================
@app.route("/product/<product_name>")
def product(product_name):
    return f"You are viewing: {product_name}"


# =========================
# ORDER
# Example: /order/123
# =========================
@app.route("/order/<int:order_id>")
def order(order_id):
    return f"Order number {order_id}"


# =========================
# CHECKOUT
# =========================
@app.route("/checkout", methods=["GET", "POST"])
def checkout():
    if request.method == "POST":
        return "Processing your order..."

    return "Please review your cart"


# =========================
# PRODUCTS PAGE
# =========================
@app.route("/products")
def products():
    items = [
        {"name": "Bag of Rice", "price": 85000},
        {"name": "Groundnut Oil (5L)", "price": 12500},
        {"name": "Indomie (Carton)", "price": 8200},
    ]

    return render_template("products.html", items=items)


# =========================
# RUN FLASK
# =========================
if __name__ == "__main__":
    app.run(debug=True)