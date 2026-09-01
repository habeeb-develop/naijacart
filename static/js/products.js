const productGrid = document.getElementById("product-grid");
const productCount = document.getElementById("product-count");
const emptyState = document.getElementById("empty-state");

let allProducts = [];
let currentCategory = "all";


// ==========================================
// LOAD PRODUCTS FROM FLASK
// ==========================================
async function loadProducts() {
    try {
        productGrid.innerHTML = `
            <div style="padding:30px;text-align:center;">
                Loading products...
            </div>
        `;

        const response = await fetch("/api/products");

        if (!response.ok) {
            throw new Error("Could not load products");
        }

        allProducts = await response.json();

        console.log("Products loaded:", allProducts);

        displayProducts(allProducts);

    } catch (error) {
        console.error("PRODUCT ERROR:", error);

        productGrid.innerHTML = `
            <div style="padding:30px;text-align:center;">
                <h3>Unable to load products</h3>
                <p>${error.message}</p>
            </div>
        `;
    }
}


// ==========================================
// DISPLAY PRODUCTS
// ==========================================
function displayProducts(products) {

    productGrid.innerHTML = "";

    if (!products || products.length === 0) {
        productGrid.innerHTML = "";
        emptyState.hidden = false;
        productCount.textContent = "0 products";
        return;
    }

    emptyState.hidden = true;

    productCount.textContent =
        `${products.length} product${products.length === 1 ? "" : "s"}`;


    products.forEach(product => {

        const card = document.createElement("article");

        card.className = "product-card";

        card.innerHTML = `
            <div class="product-image-wrapper">

                <img
                    src="${product.image}"
                    alt="${escapeHTML(product.name)}"
                    class="product-image"
                    loading="lazy"
                    onerror="this.src='https://via.placeholder.com/700x700?text=NaijaCart'"
                >

            </div>

            <div class="product-info">

                <span class="product-category">
                    ${escapeHTML(product.category)}
                </span>

                <h3 class="product-title">
                    ${escapeHTML(product.name)}
                </h3>

                <p class="product-description">
                    ${escapeHTML(product.description || "")}
                </p>

                <div class="product-bottom">

                    <strong class="product-price">
                        ₦${Number(product.price).toLocaleString("en-NG")}
                    </strong>

                    <button
                        class="add-to-cart-btn"
                        data-product-id="${product.id}"
                    >
                        Add to Cart
                    </button>

                </div>

            </div>
        `;

        productGrid.appendChild(card);
    });
}


// ==========================================
// CATEGORY FILTER
// ==========================================
function filterProducts(category) {

    currentCategory = category;

    if (category === "all") {
        displayProducts(allProducts);
        return;
    }

    const filtered = allProducts.filter(
        product =>
            product.category.toLowerCase() === category.toLowerCase()
    );

    displayProducts(filtered);
}


// ==========================================
// CATEGORY BUTTONS
// ==========================================
document.querySelectorAll(".category-card").forEach(button => {

    button.addEventListener("click", () => {

        document
            .querySelectorAll(".category-card")
            .forEach(btn => btn.classList.remove("active"));

        button.classList.add("active");

        const category = button.dataset.category;

        filterProducts(category);

        document
            .getElementById("products")
            .scrollIntoView({
                behavior: "smooth"
            });
    });

});


// ==========================================
// SEARCH
// ==========================================
const searchForm = document.getElementById("search-form");
const searchInput = document.getElementById("search");

if (searchForm) {

    searchForm.addEventListener("submit", event => {

        event.preventDefault();

        const searchTerm =
            searchInput.value.trim().toLowerCase();

        if (!searchTerm) {
            filterProducts(currentCategory);
            return;
        }

        const results = allProducts.filter(product => {

            return (
                product.name.toLowerCase().includes(searchTerm) ||
                product.category.toLowerCase().includes(searchTerm) ||
                (product.description || "")
                    .toLowerCase()
                    .includes(searchTerm)
            );

        });

        displayProducts(results);

        document
            .getElementById("products")
            .scrollIntoView({
                behavior: "smooth"
            });
    });

}


// ==========================================
// ESCAPE HTML
// ==========================================
function escapeHTML(value) {

    const div = document.createElement("div");

    div.textContent = value ?? "";

    return div.innerHTML;
}


// ==========================================
// START
// ==========================================
loadProducts();