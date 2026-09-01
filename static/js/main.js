// ============================================================
// NAIJACART - MAIN BUTTON CONTROLLER
// ============================================================

document.addEventListener("DOMContentLoaded", () => {

    // ----------------------------------------------------------
    // HELPERS
    // ----------------------------------------------------------

    const $ = (selector) => document.querySelector(selector);
    const $$ = (selector) => document.querySelectorAll(selector);

    function show(element) {
        if (element) {
            element.hidden = false;
            element.classList.add("active");
        }
    }

    function hide(element) {
        if (element) {
            element.hidden = true;
            element.classList.remove("active");
        }
    }

    function scrollToSection(id) {
        const section = document.getElementById(id);

        if (section) {
            section.scrollIntoView({
                behavior: "smooth",
                block: "start"
            });
        }
    }

    function toast(message) {
        const toastBox = $("#toast");

        if (!toastBox) return;

        toastBox.textContent = message;
        toastBox.hidden = false;

        clearTimeout(window.naijaToastTimer);

        window.naijaToastTimer = setTimeout(() => {
            toastBox.hidden = true;
        }, 2500);
    }


    // ==========================================================
    // SHOP NOW
    // ==========================================================

    const shopNow = $("#start-shopping");

    if (shopNow) {
        shopNow.addEventListener("click", () => {
            scrollToSection("products");
        });
    }


    // ==========================================================
    // EXPLORE CATEGORIES
    // ==========================================================

    $$(".hero-secondary").forEach(button => {
        button.addEventListener("click", () => {
            scrollToSection("categories");
        });
    });


    // ==========================================================
    // VIEW ALL
    // ==========================================================

    $$(".view-all-btn").forEach(button => {
        button.addEventListener("click", () => {

            // Select "All Products"
            const allButton =
                document.querySelector('.category-card[data-category="all"]');

            if (allButton) {
                allButton.click();
            }

            scrollToSection("products");
        });
    });


    // ==========================================================
    // CATEGORY BUTTONS
    // ==========================================================

    $$(".category-card").forEach(button => {

        button.addEventListener("click", () => {

            // Remove active class
            $$(".category-card").forEach(card => {
                card.classList.remove("active");
            });

            // Activate clicked category
            button.classList.add("active");

            const category = button.dataset.category;

            // If products.js already handles categories,
            // its event can continue working.
            document.dispatchEvent(
                new CustomEvent("naijacart:category", {
                    detail: {
                        category: category
                    }
                })
            );

            scrollToSection("products");
        });

    });


    // ==========================================================
    // CART OPEN
    // ==========================================================

    const cartButton = $("#cart-btn");
    const cartPanel = $("#cart-panel");
    const cartOverlay = $("#cart-overlay");

    if (cartButton) {

        cartButton.addEventListener("click", () => {

            show(cartPanel);
            show(cartOverlay);

            document.body.classList.add("cart-open");

        });

    }


    // ==========================================================
    // CART CLOSE
    // ==========================================================

    const closeCart = $("#close-cart");

    function closeCartPanel() {

        hide(cartPanel);
        hide(cartOverlay);

        document.body.classList.remove("cart-open");

    }

    if (closeCart) {
        closeCart.addEventListener("click", closeCartPanel);
    }

    if (cartOverlay) {
        cartOverlay.addEventListener("click", closeCartPanel);
    }


    // ==========================================================
    // CHECKOUT
    // ==========================================================

    const checkoutButton = $("#checkout-btn");
    const checkoutModal = $("#checkout-modal");

    if (checkoutButton) {

        checkoutButton.addEventListener("click", () => {

            show(checkoutModal);

            closeCartPanel();

        });

    }


    // ==========================================================
    // CLOSE CHECKOUT
    // ==========================================================

    const closeCheckout = $("#close-checkout");
    const checkoutOverlay = $("#checkout-overlay");

    function closeCheckoutModal() {
        hide(checkoutModal);
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


    // ==========================================================
    // PRODUCT MODAL
    // ==========================================================

    const productModal = $("#product-modal");
    const closeProductModal = $("#close-modal");
    const productModalOverlay = $("#modal-overlay");

    function closeProduct() {
        hide(productModal);
    }

    if (closeProductModal) {
        closeProductModal.addEventListener(
            "click",
            closeProduct
        );
    }

    if (productModalOverlay) {
        productModalOverlay.addEventListener(
            "click",
            closeProduct
        );
    }


    // ==========================================================
    // BUY NOW
    // ==========================================================

    const buyNow = $("#modal-buy-now");

    if (buyNow) {

        buyNow.addEventListener("click", () => {

            hide(productModal);
            show(checkoutModal);

        });

    }


    // ==========================================================
    // ADD TO CART
    // ==========================================================

    const modalAddCart = $("#modal-add-cart");

    if (modalAddCart) {

        modalAddCart.addEventListener("click", () => {

            toast("Product added to cart 🛒");

        });

    }


    // ==========================================================
    // SIGN IN
    // ==========================================================

    const signInButtons = $$(
        "#signin-btn, #close-auth"
    );

    const authModal = $("#auth-modal");

    if ($("#signin-btn")) {

        $("#signin-btn").addEventListener("click", () => {

            show(authModal);

        });

    }


    // ==========================================================
    // CLOSE AUTH
    // ==========================================================

    $$(".auth-close").forEach(button => {

        button.addEventListener("click", () => {

            hide(authModal);

        });

    });


    // ==========================================================
    // AUTH OVERLAY
    // ==========================================================

    $$(".auth-overlay").forEach(overlay => {

        overlay.addEventListener("click", () => {

            hide(authModal);

        });

    });


    // ==========================================================
    // CREATE ACCOUNT
    // ==========================================================

    $$("#show-register").forEach(button => {

        button.addEventListener("click", () => {

            const loginView = $("#login-view");
            const registerView = $("#register-view");

            if (loginView) {
                loginView.hidden = true;
            }

            if (registerView) {
                registerView.hidden = false;
            }

        });

    });


    // ==========================================================
    // BACK TO LOGIN
    // ==========================================================

    $$("#show-login").forEach(button => {

        button.addEventListener("click", () => {

            const loginView = $("#login-view");
            const registerView = $("#register-view");

            if (registerView) {
                registerView.hidden = true;
            }

            if (loginView) {
                loginView.hidden = false;
            }

        });

    });


    // ==========================================================
    // LOGIN FORM
    // ==========================================================

    $$("#login-form").forEach(form => {

        form.addEventListener("submit", event => {

            event.preventDefault();

            const email =
                form.querySelector("#login-email")?.value.trim();

            const password =
                form.querySelector("#login-password")?.value.trim();

            if (!email || !password) {
                toast("Please fill in all fields.");
                return;
            }

            toast("Signing in...");

            // Your auth.js can handle the real API login.
            document.dispatchEvent(
                new CustomEvent("naijacart:login", {
                    detail: {
                        email,
                        password
                    }
                })
            );

        });

    });


    // ==========================================================
    // REGISTER FORM
    // ==========================================================

    $$("#register-form").forEach(form => {

        form.addEventListener("submit", event => {

            event.preventDefault();

            const name =
                form.querySelector("#register-name")?.value.trim();

            const email =
                form.querySelector("#register-email")?.value.trim();

            const password =
                form.querySelector("#register-password")?.value;

            const confirm =
                form.querySelector("#register-confirm")?.value;

            const phone =
                form.querySelector("#register-phone")?.value.trim();

            const address =
                form.querySelector("#register-address")?.value.trim();


            if (
                !name ||
                !email ||
                !password ||
                !confirm ||
                !phone ||
                !address
            ) {

                toast("Please fill in all fields.");

                return;

            }


            if (password !== confirm) {

                toast("Passwords do not match.");

                return;

            }


            toast("Creating your account...");


            // Let auth.js/backend handle actual registration.
            document.dispatchEvent(
                new CustomEvent("naijacart:register", {
                    detail: {
                        name,
                        email,
                        password,
                        phone,
                        address
                    }
                })
            );

        });

    });


    // ==========================================================
    // CHECKOUT FORM
    // ==========================================================

    const checkoutForm = $("#checkout-form");

    if (checkoutForm) {

        checkoutForm.addEventListener("submit", event => {

            event.preventDefault();

            const name =
                $("#customer-name")?.value.trim();

            const phone =
                $("#customer-phone")?.value.trim();

            const email =
                $("#customer-email")?.value.trim();

            const address =
                $("#customer-address")?.value.trim();


            if (!name || !phone || !email || !address) {

                toast("Please complete your delivery details.");

                return;

            }


            hide(checkoutModal);

            const successModal = $("#success-modal");

            if (successModal) {

                const orderNumber = $("#order-number");

                if (orderNumber) {

                    const randomNumber =
                        Math.floor(100000 + Math.random() * 900000);

                    orderNumber.textContent =
                        `NC-${randomNumber}`;

                }

                show(successModal);

            }

        });

    }


    // ==========================================================
    // CONTINUE SHOPPING
    // ==========================================================

    const continueShopping = $("#continue-shopping");
    const successModal = $("#success-modal");

    if (continueShopping) {

        continueShopping.addEventListener("click", () => {

            hide(successModal);

            scrollToSection("products");

        });

    }


    // ==========================================================
    // PRODUCT SORT
    // ==========================================================

    const sortProducts = $("#sort-products");

    if (sortProducts) {

        sortProducts.addEventListener("change", () => {

            document.dispatchEvent(
                new CustomEvent("naijacart:sort", {
                    detail: {
                        sort: sortProducts.value
                    }
                })
            );

        });

    }


    // ==========================================================
    // SEARCH
    // ==========================================================

    const searchForm = $("#search-form");
    const searchInput = $("#search");

    if (searchForm) {

        searchForm.addEventListener("submit", event => {

            event.preventDefault();

            const searchValue =
                searchInput?.value.trim().toLowerCase();

            if (!searchValue) {

                toast("Enter something to search.");

                return;

            }


            document.dispatchEvent(
                new CustomEvent("naijacart:search", {
                    detail: {
                        query: searchValue
                    }
                })
            );

            scrollToSection("products");

        });

    }


    // ==========================================================
    // BECOME A SELLER
    // ==========================================================

    $$(".seller-btn").forEach(button => {

        button.addEventListener("click", () => {

            toast("Seller registration coming soon.");

        });

    });


    // ==========================================================
    // FOOTER LINKS
    // ==========================================================

    $$(".footer-column a").forEach(link => {

        link.addEventListener("click", event => {

            const href = link.getAttribute("href");

            if (!href || href === "#") {

                event.preventDefault();

                toast(
                    `${link.textContent.trim()} page coming soon.`
                );

            }

        });

    });


    // ==========================================================
    // SOCIAL LINKS
    // ==========================================================

    $$(".social-links a").forEach(link => {

        link.addEventListener("click", event => {

            event.preventDefault();

            toast(
                `${link.getAttribute("aria-label")} link coming soon.`
            );

        });

    });


    // ==========================================================
    // ESC KEY - CLOSE MODALS
    // ==========================================================

    document.addEventListener("keydown", event => {

        if (event.key !== "Escape") return;

        closeCartPanel();
        closeProduct();
        closeCheckoutModal();
        hide(authModal);
        hide(successModal);

    });


    // ==========================================================
    // CURRENT YEAR
    // ==========================================================

    const currentYear = $("#current-year");

    if (currentYear) {
        currentYear.textContent = new Date().getFullYear();
    }


    // ==========================================================
    // DONE
    // ==========================================================

    console.log("🇳🇬 NaijaCart main.js loaded successfully.");

});