// ============================================================
// NAIJACART - UI
// js/ui.js
// ============================================================


export const $ = (
    selector,
    root = document
) => {

    return root.querySelector(selector);

};


export const $$ = (
    selector,
    root = document
) => {

    return [
        ...root.querySelectorAll(selector)
    ];

};


// ============================================================
// OPEN
// ============================================================

export function openElement(element) {

    if (!element) return;


    element.hidden = false;


    element.setAttribute(
        "aria-hidden",
        "false"
    );


    document.body.classList.add(
        "modal-open"
    );

}


// ============================================================
// CLOSE
// ============================================================

export function closeElement(element) {

    if (!element) return;


    element.hidden = true;


    element.setAttribute(
        "aria-hidden",
        "true"
    );


    const openModal =
        document.querySelector(
            ".modal:not([hidden])"
        );


    if (!openModal) {

        document.body.classList.remove(
            "modal-open"
        );

    }

}


// ============================================================
// TOAST
// ============================================================

export function toast(message) {

    const box = $("#toast");


    if (!box) {

        alert(message);

        return;

    }


    box.textContent = message;

    box.hidden = false;


    clearTimeout(
        window.__naijaToast
    );


    window.__naijaToast =
        setTimeout(
            () => {

                box.hidden = true;

            },
            2500
        );

}


// ============================================================
// MONEY
// ============================================================

export function money(value) {

    return `₦${Number(
        value || 0
    ).toLocaleString("en-NG")}`;

}


// ============================================================
// SCROLL
// ============================================================

export function scrollToId(id) {

    const element =
        document.getElementById(id);


    if (!element) return;


    element.scrollIntoView({

        behavior: "smooth",

        block: "start"

    });

}