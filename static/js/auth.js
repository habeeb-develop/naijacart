// ============================================================
// NAIJACART - AUTH
// js/auth.js
// ============================================================

import {
    login,
    register
} from "./api.js";

import {
    $,
    openElement,
    closeElement,
    toast
} from "./ui.js";


let initialized = false;


// ============================================================
// INIT
// ============================================================

export function initAuth() {

    if (initialized) return;

    initialized = true;


    const modal =
        $("#auth-modal");


    const loginView =
        $("#login-view");


    const registerView =
        $("#register-view");


    const openButton =
        $("#signin-btn");


    const overlay =
        $("#auth-overlay");


    // --------------------------------------------------------
    // SHOW LOGIN
    // --------------------------------------------------------

    function showLogin() {

        if (loginView) {

            loginView.hidden = false;

        }


        if (registerView) {

            registerView.hidden = true;

        }

    }


    // --------------------------------------------------------
    // SHOW REGISTER
    // --------------------------------------------------------

    function showRegister() {

        if (loginView) {

            loginView.hidden = true;

        }


        if (registerView) {

            registerView.hidden = false;

        }

    }


    // --------------------------------------------------------
    // OPEN AUTH
    // --------------------------------------------------------

    function openAuth() {

        showLogin();

        openElement(
            modal
        );

    }


    // --------------------------------------------------------
    // CLOSE AUTH
    // --------------------------------------------------------

    function closeAuth() {

        closeElement(
            modal
        );

    }


    // --------------------------------------------------------
    // BUTTONS
    // --------------------------------------------------------

    openButton?.addEventListener(
        "click",
        openAuth
    );


    $("#close-auth")
        ?.addEventListener(
            "click",
            closeAuth
        );


    overlay?.addEventListener(
        "click",
        closeAuth
    );


    $("#show-register")
        ?.addEventListener(
            "click",
            event => {

                event.preventDefault();

                showRegister();

            }
        );


    $("#show-login")
        ?.addEventListener(
            "click",
            event => {

                event.preventDefault();

                showLogin();

            }
        );


    // --------------------------------------------------------
    // LOGIN
    // --------------------------------------------------------

    $("#login-form")
        ?.addEventListener(
            "submit",
            async event => {

                event.preventDefault();


                const email =
                    $("#login-email")
                        .value
                        .trim();


                const password =
                    $("#login-password")
                        .value;


                const button =
                    event.currentTarget
                        .querySelector(
                            'button[type="submit"]'
                        );


                if (button) {

                    button.disabled = true;

                    button.textContent =
                        "Signing In...";

                }


                try {

                    const result =
                        await login({

                            email,

                            password

                        });


                    localStorage.setItem(
                        "nc_user",
                        JSON.stringify(
                            result.user ||
                            {
                                email
                            }
                        )
                    );


                    toast(
                        "Signed in successfully ✓"
                    );


                    closeAuth();


                    updateAccountButton();

                }


                catch (error) {

                    toast(
                        error.message ||
                        "Sign in failed."
                    );

                }


                finally {

                    if (button) {

                        button.disabled =
                            false;

                        button.textContent =
                            "Sign In";

                    }

                }

            }
        );


    // --------------------------------------------------------
    // REGISTER
    // --------------------------------------------------------

    $("#register-form")
        ?.addEventListener(
            "submit",
            async event => {

                event.preventDefault();


                const password =
                    $("#register-password")
                        .value;


                const confirm =
                    $("#register-confirm")
                        .value;


                if (
                    password !==
                    confirm
                ) {

                    toast(
                        "Passwords do not match."
                    );

                    return;

                }


                const data = {

                    name:
                        $("#register-name")
                            .value
                            .trim(),

                    email:
                        $("#register-email")
                            .value
                            .trim(),

                    password,

                    phone:
                        $("#register-phone")
                            .value
                            .trim(),

                    address:
                        $("#register-address")
                            .value
                            .trim()

                };


                const button =
                    event.currentTarget
                        .querySelector(
                            'button[type="submit"]'
                        );


                if (button) {

                    button.disabled = true;

                    button.textContent =
                        "Creating...";

                }


                try {

                    const result =
                        await register(
                            data
                        );


                    localStorage.setItem(
                        "nc_user",
                        JSON.stringify(
                            result.user ||
                            data
                        )
                    );


                    toast(
                        "Account created successfully ✓"
                    );


                    closeAuth();


                    updateAccountButton();

                }


                catch (error) {

                    toast(
                        error.message ||
                        "Could not create account."
                    );

                }


                finally {

                    if (button) {

                        button.disabled =
                            false;

                        button.textContent =
                            "Create Account";

                    }

                }

            }
        );


    updateAccountButton();

}


// ============================================================
// UPDATE SIGN-IN BUTTON
// ============================================================

export function updateAccountButton() {

    const button =
        $("#signin-btn");


    const user =
        JSON.parse(
            localStorage.getItem(
                "nc_user"
            ) || "null"
        );


    if (!button) return;


    if (user?.name) {

        button.textContent =
            `Hi, ${
                user.name.split(" ")[0]
            }`;

    } else {

        button.textContent =
            "Sign In";

    }

}


// ============================================================
// LOGOUT
// ============================================================

export function logout() {

    localStorage.removeItem(
        "nc_token"
    );


    localStorage.removeItem(
        "nc_user"
    );


    updateAccountButton();


    toast(
        "Signed out."
    );

}