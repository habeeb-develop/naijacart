document.addEventListener("DOMContentLoaded", () => {

    // =====================================================
    // ELEMENTS
    // =====================================================

    const productGrid = document.getElementById("product-grid");
    const productCount = document.getElementById("product-count");
    const emptyState = document.getElementById("empty-state");
    const loadingState = document.getElementById("loading-state");

    const searchInput = document.getElementById("search");
    const searchForm = document.getElementById("search-form");

    const categoryButtons =
        document.querySelectorAll(".category-card");

    const sortProducts =
        document.getElementById("sort-products");

    const startShopping =
        document.getElementById("start-shopping");


    // =====================================================
    // DATA
    // =====================================================

    let products = [];
    let selectedCategory = "all";


    // =====================================================
    // NAIRA
    // =====================================================

    function naira(amount) {
        return "₦" + Number(amount || 0).toLocaleString(
            "en-NG",
            {
                minimumFractionDigits: 0,
                maximumFractionDigits: 2
            }
        );
    }


    // =====================================================
    // ESCAPE HTML
    // =====================================================

    function escapeHTML(value) {

        if (value === null || value === undefined) {
            return "";
        }

        return String(value)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }


    // =====================================================
    // LOAD PRODUCTS FROM FLASK
    // =====================================================

    async function loadProducts() {

        if (loadingState) {
            loadingState.hidden = false;
        }

        if (productGrid) {
            productGrid.innerHTML = "";
        }

        try {

            const response = await fetch("/api/products", {
                method: "GET",
                headers: {
                    "Accept": "application/json"
                },
                cache: "no-store"
            });

            if (!response.ok) {
                throw new Error(
                    `Server returned HTTP ${response.status}`
                );
            }

            const data = await response.json();

            if (!Array.isArray(data)) {
                throw new Error(
                    data.error || "Invalid product data received."
                );
            }

            products = data.map(product => ({
                id: Number(product.id),
                name: product.name || "Unnamed Product",

                category: String(
                    product.category || "other"
                ).toLowerCase().trim(),

                price: Number(product.price) || 0,

                description:
                    product.description ||
                    "Quality product from a Nigerian seller.",

                image:
                    product.image ||
                    "https://via.placeholder.com/700x500?text=NaijaCart",

                seller_id: product.seller_id,

                stock: Number(product.stock) || 0
            }));

            console.log(
                "NaijaCart products loaded:",
                products
            );

            renderProducts();

        } catch (error) {

            console.error(
                "ERROR LOADING PRODUCTS:",
                error
            );

            if (productGrid) {

                productGrid.innerHTML = `
                    <div class="product-error"
                         style="
                            grid-column:1/-1;
                            padding:40px;
                            text-align:center;
                         ">

                        <h3>Unable to load products</h3>

                        <p>
                            ${escapeHTML(error.message)}
                        </p>

                        <button
                            type="button"
                            onclick="location.reload()"
                        >
                            Try Again
                        </button>

                    </div>
                `;
            }

        } finally {

            if (loadingState) {
                loadingState.hidden = true;
            }
        }
    }


    // =====================================================
    // FILTER + SORT
    // =====================================================

    function getVisibleProducts() {

        const searchTerm = searchInput
            ? searchInput.value.trim().toLowerCase()
            : "";

        let result = products.filter(product => {

            const matchesCategory =
                selectedCategory === "all" ||
                product.category === selectedCategory;

            const searchableText = (
                product.name +
                " " +
                product.category +
                " " +
                product.description
            ).toLowerCase();

            const matchesSearch =
                searchableText.includes(searchTerm);

            return matchesCategory && matchesSearch;
        });


        const sortValue =
            sortProducts
                ? sortProducts.value
                : "newest";


        if (sortValue === "price-low") {

            result.sort(
                (a, b) => a.price - b.price
            );

        } else if (sortValue === "price-high") {

            result.sort(
                (a, b) => b.price - a.price
            );

        } else if (sortValue === "name") {

            result.sort(
                (a, b) =>
                    a.name.localeCompare(b.name)
            );

        } else {

            result.sort(
                (a, b) => b.id - a.id
            );
        }

        return result;
    }


    // =====================================================
    // RENDER PRODUCTS
    // =====================================================

    function renderProducts() {

        if (!productGrid) {
            console.error(
                "ERROR: #product-grid does not exist in HTML."
            );
            return;
        }

        const visibleProducts =
            getVisibleProducts();

        productGrid.innerHTML = "";


        if (productCount) {

            productCount.textContent =
                `${visibleProducts.length} product${
                    visibleProducts.length === 1
                        ? ""
                        : "s"
                }`;
        }


        if (visibleProducts.length === 0) {

            if (emptyState) {
                emptyState.hidden = false;
            }

            return;
        }


        if (emptyState) {
            emptyState.hidden = true;
        }


        visibleProducts.forEach(product => {

            const card =
                document.createElement("article");

            card.className = "product-card";

            card.dataset.id = product.id;
            card.dataset.name = product.name;
            card.dataset.category = product.category;


            card.innerHTML = `

                <div class="product-image">

                    <img
                        src="${escapeHTML(product.image)}"
                        alt="${escapeHTML(product.name)}"
                        loading="lazy"
                        onerror="this.onerror=null;this.src='https://via.placeholder.com/700x500?text=NaijaCart';"
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
                        ${escapeHTML(product.description)}
                    </p>

                    <div class="product-bottom">

                        <strong class="product-price">
                            ${naira(product.price)}
                        </strong>

                        <button
                            type="button"
                            class="add-cart"
                            data-id="${product.id}"
                        >
                            Add to Cart
                        </button>

                    </div>

                </div>
            `;

            productGrid.appendChild(card);
        });


        attachProductEvents();
    }


    // =====================================================
    // PRODUCT EVENTS
    // =====================================================

    function attachProductEvents() {

        document
            .querySelectorAll(".add-cart")
            .forEach(button => {

                button.addEventListener(
                    "click",
                    event => {

                        event.stopPropagation();

                        const id =
                            Number(button.dataset.id);

                        const product =
                            products.find(
                                item =>
                                    item.id === id
                            );

                        if (product) {
                            addToCart(product);
                        }
                    }
                );
            });


        document
            .querySelectorAll(".product-card")
            .forEach(card => {

                card.addEventListener(
                    "click",
                    event => {

                        if (
                            event.target.closest(".add-cart")
                        ) {
                            return;
                        }

                        const id =
                            Number(card.dataset.id);

                        const product =
                            products.find(
                                item =>
                                    item.id === id
                            );

                        if (product) {
                            openProductModal(product);
                        }
                    }
                );
            });
    }


    // =====================================================
    // CATEGORIES
    // =====================================================

    categoryButtons.forEach(button => {

        button.addEventListener(
            "click",
            () => {

                categoryButtons.forEach(item => {
                    item.classList.remove("active");
                });

                button.classList.add("active");

                selectedCategory =
                    String(
                        button.dataset.category || "all"
                    ).toLowerCase().trim();

                renderProducts();

                const productsSection =
                    document.getElementById("products");

                if (productsSection) {

                    productsSection.scrollIntoView({
                        behavior: "smooth",
                        block: "start"
                    });
                }
            }
        );
    });


    // =====================================================
    // SEARCH
    // =====================================================

    if (searchInput) {

        searchInput.addEventListener(
            "input",
            renderProducts
        );
    }


    if (searchForm) {

        searchForm.addEventListener(
            "submit",
            event => {

                event.preventDefault();
                renderProducts();
            }
        );
    }


    // =====================================================
    // SORT
    // =====================================================

    if (sortProducts) {

        sortProducts.addEventListener(
            "change",
            renderProducts
        );
    }


    // =====================================================
    // START SHOPPING
    // =====================================================

    if (startShopping) {

        startShopping.addEventListener(
            "click",
            () => {

                const productsSection =
                    document.getElementById("products");

                if (productsSection) {

                    productsSection.scrollIntoView({
                        behavior: "smooth"
                    });
                }
            }
        );
    }


    // =====================================================
    // CART
    // =====================================================

    let cart = [];

    try {

        cart =
            JSON.parse(
                localStorage.getItem(
                    "naijacart_cart"
                )
            ) || [];

    } catch {

        cart = [];
    }


    const cartButton =
        document.getElementById("cart-btn");

    const cartPanel =
        document.getElementById("cart-panel");

    const cartOverlay =
        document.getElementById("cart-overlay");

    const closeCart =
        document.getElementById("close-cart");

    const cartItems =
        document.getElementById("cart-items");

    const cartCount =
        document.getElementById("cart-count");

    const cartTotal =
        document.getElementById("cart-total");


    function saveCart() {

        localStorage.setItem(
            "naijacart_cart",
            JSON.stringify(cart)
        );
    }


    function renderCart() {

        if (!cartItems) {
            return;
        }

        cartItems.innerHTML = "";


        if (cart.length === 0) {

            cartItems.innerHTML = `
                <p>Your cart is empty.</p>
            `;

        } else {

            cart.forEach(item => {

                const div =
                    document.createElement("div");

                div.className = "cart-item";

                div.innerHTML = `

                    <div class="cart-item-image">

                        ${
                            item.image
                                ? `
                                    <img
                                        src="${escapeHTML(item.image)}"
                                        alt="${escapeHTML(item.name)}"
                                    >
                                `
                                : "🛍️"
                        }

                    </div>

                    <div class="cart-item-info">

                        <h4>
                            ${escapeHTML(item.name)}
                        </h4>

                        <strong>
                            ${naira(item.price)}
                        </strong>

                        <div>
                            Quantity: ${item.quantity}
                        </div>

                        <button
                            type="button"
                            class="remove-item"
                            data-id="${item.id}"
                        >
                            Remove
                        </button>

                    </div>
                `;

                cartItems.appendChild(div);
            });
        }


        let totalItems = 0;
        let totalPrice = 0;


        cart.forEach(item => {

            totalItems +=
                Number(item.quantity) || 0;

            totalPrice +=
                Number(item.price || 0) *
                Number(item.quantity || 0);
        });


        if (cartCount) {
            cartCount.textContent = totalItems;
        }

        if (cartTotal) {
            cartTotal.textContent =
                naira(totalPrice);
        }


        saveCart();
    }


    function addToCart(product) {

        const existing =
            cart.find(
                item =>
                    Number(item.id) ===
                    Number(product.id)
            );


        if (existing) {

            existing.quantity++;

        } else {

            cart.push({
                id: product.id,
                name: product.name,
                price: product.price,
                image: product.image,
                quantity: 1
            });
        }


        renderCart();

        showToast(
            `${product.name} added to cart`
        );

        openCart();
    }


    if (cartItems) {

        cartItems.addEventListener(
            "click",
            event => {

                if (
                    event.target.classList.contains(
                        "remove-item"
                    )
                ) {

                    const id =
                        Number(
                            event.target.dataset.id
                        );

                    cart =
                        cart.filter(
                            item =>
                                Number(item.id) !== id
                        );

                    renderCart();
                }
            }
        );
    }


    function openCart() {

        if (cartPanel) {
            cartPanel.hidden = false;

            requestAnimationFrame(() => {
                cartPanel.classList.add("open");
            });
        }

        if (cartOverlay) {
            cartOverlay.hidden = false;

            requestAnimationFrame(() => {
                cartOverlay.classList.add("show");
            });
        }
    }


    function closeCartPanel() {

        if (cartPanel) {
            cartPanel.classList.remove("open");
        }

        if (cartOverlay) {
            cartOverlay.classList.remove("show");
        }

        setTimeout(() => {

            if (cartPanel) {
                cartPanel.hidden = true;
            }

            if (cartOverlay) {
                cartOverlay.hidden = true;
            }

        }, 250);
    }


    if (cartButton) {
        cartButton.addEventListener(
            "click",
            openCart
        );
    }

    if (closeCart) {
        closeCart.addEventListener(
            "click",
            closeCartPanel
        );
    }

    if (cartOverlay) {
        cartOverlay.addEventListener(
            "click",
            closeCartPanel
        );
    }


    // =====================================================
    // PRODUCT MODAL
    // =====================================================

    const productModal =
        document.getElementById("product-modal");

    const modalOverlay =
        document.getElementById("modal-overlay");

    const closeModal =
        document.getElementById("close-modal");

    const modalImage =
        document.getElementById(
            "modal-product-image"
        );

    const modalCategory =
        document.getElementById(
            "modal-product-category"
        );

    const modalTitle =
        document.getElementById(
            "modal-product-title"
        );

    const modalDescription =
        document.getElementById(
            "modal-product-description"
        );

    const modalPrice =
        document.getElementById(
            "modal-product-price"
        );

    const modalSeller =
        document.getElementById(
            "modal-product-seller"
        );

    const modalAddCart =
        document.getElementById(
            "modal-add-cart"
        );

    const modalBuyNow =
        document.getElementById(
            "modal-buy-now"
        );


    let selectedProduct = null;


    function openProductModal(product) {

        selectedProduct = product;


        if (modalImage) {
            modalImage.src = product.image;
            modalImage.alt = product.name;
        }

        if (modalCategory) {
            modalCategory.textContent =
                product.category;
        }

        if (modalTitle) {
            modalTitle.textContent =
                product.name;
        }

        if (modalDescription) {
            modalDescription.textContent =
                product.description;
        }

        if (modalPrice) {
            modalPrice.textContent =
                naira(product.price);
        }

        if (modalSeller) {
            modalSeller.textContent =
                "Nigerian Seller";
        }


        if (productModal) {

            productModal.hidden = false;

            requestAnimationFrame(() => {
                productModal.classList.add("show");
            });
        }
    }


    function closeProductModal() {

        if (!productModal) {
            return;
        }

        productModal.classList.remove("show");

        setTimeout(() => {
            productModal.hidden = true;
        }, 200);
    }


    if (closeModal) {
        closeModal.addEventListener(
            "click",
            closeProductModal
        );
    }

    if (modalOverlay) {
        modalOverlay.addEventListener(
            "click",
            closeProductModal
        );
    }


    if (modalAddCart) {

        modalAddCart.addEventListener(
            "click",
            () => {

                if (selectedProduct) {

                    addToCart(selectedProduct);
                    closeProductModal();
                }
            }
        );
    }


    if (modalBuyNow) {

        modalBuyNow.addEventListener(
            "click",
            () => {

                if (selectedProduct) {

                    addToCart(selectedProduct);
                    closeProductModal();
                    openCart();
                }
            }
        );
    }


    // =====================================================
    // TOAST
    // =====================================================

    const toast =
        document.getElementById("toast");

    let toastTimer;


    function showToast(message) {

        if (!toast) {
            return;
        }

        toast.textContent = message;
        toast.hidden = false;

        clearTimeout(toastTimer);

        toastTimer =
            setTimeout(() => {
                toast.hidden = true;
            }, 2500);
    }


    // =====================================================
    // AUTH
    // =====================================================

    const signinButton =
        document.getElementById("signin-btn");

    const authModal =
        document.getElementById("auth-modal");

    const authOverlay =
        document.getElementById("auth-overlay");

    const closeAuth =
        document.getElementById("close-auth");

    const loginView =
        document.getElementById("login-view");

    const registerView =
        document.getElementById("register-view");

    const showRegister =
        document.getElementById("show-register");

    const showLogin =
        document.getElementById("show-login");


    function openAuth() {

        if (!authModal) {
            return;
        }

        authModal.hidden = false;

        requestAnimationFrame(() => {
            authModal.classList.add("show");
        });
    }


    function closeAuthModal() {

        if (!authModal) {
            return;
        }

        authModal.classList.remove("show");

        setTimeout(() => {
            authModal.hidden = true;
        }, 200);
    }


    if (signinButton) {
        signinButton.addEventListener(
            "click",
            openAuth
        );
    }

    if (closeAuth) {
        closeAuth.addEventListener(
            "click",
            closeAuthModal
        );
    }

    if (authOverlay) {
        authOverlay.addEventListener(
            "click",
            closeAuthModal
        );
    }


    if (showRegister) {

        showRegister.addEventListener(
            "click",
            () => {

                if (loginView) {
                    loginView.hidden = true;
                }

                if (registerView) {
                    registerView.hidden = false;
                }
            }
        );
    }


    if (showLogin) {

        showLogin.addEventListener(
            "click",
            () => {

                if (registerView) {
                    registerView.hidden = true;
                }

                if (loginView) {
                    loginView.hidden = false;
                }
            }
        );
    }


    // =====================================================
    // LOGIN
    // =====================================================

    const loginForm =
        document.getElementById("login-form");

    if (loginForm) {

        loginForm.addEventListener(
            "submit",
            event => {

                event.preventDefault();

                showToast(
                    "Sign-in submitted"
                );
            }
        );
    }


    // =====================================================
    // REGISTER
    // =====================================================

    const registerForm =
        document.getElementById(
            "register-form"
        );

    if (registerForm) {

        registerForm.addEventListener(
            "submit",
            event => {

                event.preventDefault();

                const password =
                    document.getElementById(
                        "register-password"
                    );

                const confirm =
                    document.getElementById(
                        "register-confirm"
                    );


                if (
                    password &&
                    confirm &&
                    password.value !== confirm.value
                ) {

                    alert(
                        "Passwords do not match."
                    );

                    return;
                }


                showToast(
                    "Account created successfully"
                );
            }
        );
    }


    // =====================================================
    // CHECKOUT
    // =====================================================

    const checkoutButton =
        document.getElementById(
            "checkout-btn"
        );

    const checkoutModal =
        document.getElementById(
            "checkout-modal"
        );

    const checkoutOverlay =
        document.getElementById(
            "checkout-overlay"
        );

    const closeCheckout =
        document.getElementById(
            "close-checkout"
        );


    function openCheckout() {

        if (cart.length === 0) {

            alert(
                "Your cart is empty."
            );

            return;
        }


        const subtotal =
            cart.reduce(
                (total, item) =>
                    total +
                    (
                        Number(item.price) *
                        Number(item.quantity)
                    ),
                0
            );


        const delivery = 0;


        const checkoutSubtotal =
            document.getElementById(
                "checkout-subtotal"
            );

        const checkoutDelivery =
            document.getElementById(
                "checkout-delivery"
            );

        const checkoutTotal =
            document.getElementById(
                "checkout-total"
            );


        if (checkoutSubtotal) {
            checkoutSubtotal.textContent =
                naira(subtotal);
        }

        if (checkoutDelivery) {
            checkoutDelivery.textContent =
                naira(delivery);
        }

        if (checkoutTotal) {
            checkoutTotal.textContent =
                naira(
                    subtotal + delivery
                );
        }


        closeCartPanel();


        if (checkoutModal) {

            checkoutModal.hidden = false;

            requestAnimationFrame(() => {
                checkoutModal.classList.add("show");
            });
        }
    }


    function closeCheckoutModal() {

        if (!checkoutModal) {
            return;
        }

        checkoutModal.classList.remove("show");

        setTimeout(() => {
            checkoutModal.hidden = true;
        }, 200);
    }


    if (checkoutButton) {

        checkoutButton.addEventListener(
            "click",
            openCheckout
        );
    }

    if (closeCheckout) {

        closeCheckout.addEventListener(
            "click",
            closeCheckoutModal
        );
    }

    if (checkoutOverlay) {

        checkoutOverlay.addEventListener(
            "click",
            closeCheckoutModal
        );
    }


    // =====================================================
    // CHECKOUT FORM
    // =====================================================

    const checkoutForm =
        document.getElementById(
            "checkout-form"
        );

    const successModal =
        document.getElementById(
            "success-modal"
        );

    const continueShopping =
        document.getElementById(
            "continue-shopping"
        );


    if (checkoutForm) {

        checkoutForm.addEventListener(
            "submit",
            event => {

                event.preventDefault();


                const orderNumber =
                    document.getElementById(
                        "order-number"
                    );


                const randomNumber =
                    Math.floor(
                        100000 +
                        Math.random() * 900000
                    );


                if (orderNumber) {

                    orderNumber.textContent =
                        "NC-" +
                        randomNumber;
                }


                closeCheckoutModal();


                if (successModal) {

                    successModal.hidden = false;

                    requestAnimationFrame(() => {
                        successModal.classList.add(
                            "show"
                        );
                    });
                }


                cart = [];

                saveCart();
                renderCart();
            }
        );
    }


    if (continueShopping) {

        continueShopping.addEventListener(
            "click",
            () => {

                if (successModal) {

                    successModal.classList.remove(
                        "show"
                    );

                    setTimeout(() => {
                        successModal.hidden = true;
                    }, 200);
                }
            }
        );
    }


    // =====================================================
    // YEAR
    // =====================================================

    const currentYear =
        document.getElementById(
            "current-year"
        );

    if (currentYear) {
        currentYear.textContent =
            new Date().getFullYear();
    }


    // =====================================================
    // INITIALIZE
    // =====================================================

    renderCart();
    loadProducts();

});