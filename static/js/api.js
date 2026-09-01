// ============================================================
// NAIJACART - API
// js/api.js
// ============================================================

const BASE = "http://127.0.0.1:5000/api";


// ------------------------------------------------------------
// AUTH HEADERS
// ------------------------------------------------------------

function authHeaders() {

    const token = localStorage.getItem("nc_token");

    return token
        ? {
            Authorization: `Bearer ${token}`
        }
        : {};
}


// ------------------------------------------------------------
// MAIN REQUEST FUNCTION
// ------------------------------------------------------------

async function request(
    path,
    {
        method = "GET",
        body
    } = {}
) {

    const response = await fetch(`${BASE}${path}`, {

        method,

        headers: {
            "Content-Type": "application/json",
            ...authHeaders()
        },

        body:
            body === undefined
                ? undefined
                : JSON.stringify(body)

    });


    let data = null;

    try {

        data = await response.json();

    } catch {

        data = null;

    }


    if (!response.ok) {

        const message =
            data?.message ||
            data?.error ||
            `Request failed (${response.status})`;

        throw new Error(message);

    }


    return data;
}


// ============================================================
// DEMO PRODUCTS
// ============================================================

const demoProducts = [

    {
        id: 1,
        name: "Ankara Smart Outfit",
        category: "fashion",
        price: 28500,
        image:
            "https://images.unsplash.com/photo-1490481651871-ab68de25d43d?auto=format&fit=crop&w=700&q=80",
        description:
            "A clean Nigerian-inspired outfit for everyday style.",
        seller: "Lagos Fashion Hub",
        createdAt: "2026-08-20"
    },

    {
        id: 2,
        name: "Classic Sneakers",
        category: "fashion",
        price: 32000,
        image:
            "https://images.unsplash.com/photo-1542291026-7eec264c27ff?auto=format&fit=crop&w=700&q=80",
        description:
            "Comfortable sneakers for everyday movement.",
        seller: "Naija Kicks",
        createdAt: "2026-08-19"
    },

    {
        id: 3,
        name: "Premium Rice 5kg",
        category: "groceries",
        price: 12500,
        image:
            "https://images.unsplash.com/photo-1586201375761-83865001e31c?auto=format&fit=crop&w=700&q=80",
        description:
            "Quality rice for your home kitchen.",
        seller: "Fresh Basket NG",
        createdAt: "2026-08-18"
    },

    {
        id: 4,
        name: "Wireless Headphones",
        category: "electronics",
        price: 45000,
        image:
            "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=700&q=80",
        description:
            "Wireless audio with a comfortable fit.",
        seller: "Tech Naija",
        createdAt: "2026-08-17"
    },

    {
        id: 5,
        name: "Smartphone 128GB",
        category: "electronics",
        price: 185000,
        image:
            "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?auto=format&fit=crop&w=700&q=80",
        description:
            "A modern smartphone for work and entertainment.",
        seller: "Lagos Gadgets",
        createdAt: "2026-08-16"
    },

    {
        id: 6,
        name: "Skincare Starter Set",
        category: "beauty",
        price: 18000,
        image:
            "https://images.unsplash.com/photo-1556229010-6c3f2c9ca5f8?auto=format&fit=crop&w=700&q=80",
        description:
            "Simple daily skincare essentials.",
        seller: "Beauty Corner NG",
        createdAt: "2026-08-15"
    },

    {
        id: 7,
        name: "Modern Living Room Chair",
        category: "home",
        price: 85000,
        image:
            "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?auto=format&fit=crop&w=700&q=80",
        description:
            "A comfortable chair for a modern home.",
        seller: "HomeStyle Nigeria",
        createdAt: "2026-08-14"
    },

    {
        id: 8,
        name: "Premium Tote Bag",
        category: "fashion",
        price: 16500,
        image:
            "https://images.unsplash.com/photo-1548036328-c9fa89d128fa?auto=format&fit=crop&w=700&q=80",
        description:
            "A practical everyday fashion bag.",
        seller: "Style Market NG",
        createdAt: "2026-08-13"
    }

];


// ============================================================
// GET PRODUCTS
// ============================================================

export async function getProducts() {

    try {

        const data = await request("/products");

        const products =
            Array.isArray(data)
                ? data
                : (
                    data?.products ||
                    data?.data ||
                    []
                );


        if (products.length) {

            return products;

        }

    } catch (error) {

        console.info(
            "Backend unavailable. Using demo products.",
            error.message
        );

    }


    return demoProducts;
}


// ============================================================
// LOGIN
// ============================================================

export async function login(credentials) {

    try {

        const data = await request(
            "/auth/login",
            {
                method: "POST",
                body: credentials
            }
        );


        if (data?.token) {

            localStorage.setItem(
                "nc_token",
                data.token
            );

        }


        return data;

    } catch (error) {

        const users =
            JSON.parse(
                localStorage.getItem("nc_users") || "[]"
            );


        const user = users.find(
            u =>
                u.email.toLowerCase() ===
                credentials.email.toLowerCase() &&
                u.password === credentials.password
        );


        if (!user) {

            throw new Error(
                "Invalid email or password."
            );

        }


        const safeUser = {
            id: user.id,
            name: user.name,
            email: user.email
        };


        localStorage.setItem(
            "nc_user",
            JSON.stringify(safeUser)
        );


        return {
            user: safeUser
        };

    }

}


// ============================================================
// REGISTER
// ============================================================

export async function register(user) {

    try {

        const data = await request(
            "/auth/register",
            {
                method: "POST",
                body: user
            }
        );


        if (data?.token) {

            localStorage.setItem(
                "nc_token",
                data.token
            );

        }


        return data;

    } catch (error) {

        const users =
            JSON.parse(
                localStorage.getItem("nc_users") || "[]"
            );


        const exists = users.some(
            u =>
                u.email.toLowerCase() ===
                user.email.toLowerCase()
        );


        if (exists) {

            throw new Error(
                "An account with this email already exists."
            );

        }


        const savedUser = {

            ...user,

            id: Date.now()

        };


        users.push(savedUser);


        localStorage.setItem(
            "nc_users",
            JSON.stringify(users)
        );


        const safeUser = {

            id: savedUser.id,

            name: savedUser.name,

            email: savedUser.email

        };


        localStorage.setItem(
            "nc_user",
            JSON.stringify(safeUser)
        );


        return {

            user: safeUser

        };

    }

}


// ============================================================
// CREATE ORDER
// ============================================================

export async function createOrder(order) {

    try {

        return await request(
            "/orders",
            {
                method: "POST",
                body: order
            }
        );

    } catch (error) {

        console.info(
            "Backend order endpoint unavailable. Demo mode.",
            error.message
        );


        return {

            orderId:
                `NC-${Math.floor(
                    100000 +
                    Math.random() * 900000
                )}`,

            demo: true

        };

    }

}


// ============================================================
// EXPORTS
// ============================================================

export {
    BASE,
    request
};