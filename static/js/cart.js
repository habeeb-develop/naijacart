// ============================================================
// NAIJACART - CART
// js/cart.js
// ============================================================

const CART_KEY = "naijacart_cart";


// ------------------------------------------------------------
// LOAD CART
// ------------------------------------------------------------

function loadCart() {

    try {

        const saved =
            JSON.parse(
                localStorage.getItem(CART_KEY) || "[]"
            );


        return Array.isArray(saved)
            ? saved
            : [];

    } catch {

        return [];

    }

}


let items = loadCart();


// ------------------------------------------------------------
// SAVE CART
// ------------------------------------------------------------

function saveCart() {

    localStorage.setItem(
        CART_KEY,
        JSON.stringify(items)
    );


    window.dispatchEvent(
        new CustomEvent(
            "cart:changed",
            {
                detail: getCart()
            }
        )
    );

}


// ============================================================
// GET CART
// ============================================================

export function getCart() {

    return items.map(
        item => ({
            ...item
        })
    );

}


// ============================================================
// ADD TO CART
// ============================================================

export function addToCart(
    product,
    quantity = 1
) {

    const id = String(product.id);


    const existing =
        items.find(
            item =>
                String(item.id) === id
        );


    if (existing) {

        existing.quantity += quantity;

    } else {

        items.push({

            ...product,

            id,

            quantity

        });

    }


    saveCart();


    return getCart();

}


// ============================================================
// REMOVE
// ============================================================

export function removeFromCart(id) {

    items =
        items.filter(
            item =>
                String(item.id) !==
                String(id)
        );


    saveCart();

}


// ============================================================
// CHANGE QUANTITY
// ============================================================

export function setQuantity(
    id,
    quantity
) {

    const item =
        items.find(
            x =>
                String(x.id) ===
                String(id)
        );


    if (!item) return;


    item.quantity =
        Math.max(
            0,
            Number(quantity) || 0
        );


    if (item.quantity === 0) {

        removeFromCart(id);

    } else {

        saveCart();

    }

}


// ============================================================
// CLEAR
// ============================================================

export function clearCart() {

    items = [];

    saveCart();

}


// ============================================================
// COUNT
// ============================================================

export function cartCount() {

    return items.reduce(
        (total, item) =>
            total + item.quantity,
        0
    );

}


// ============================================================
// TOTAL
// ============================================================

export function cartTotal() {

    return items.reduce(
        (total, item) =>
            total +
            Number(item.price || 0) *
            item.quantity,
        0
    );

}