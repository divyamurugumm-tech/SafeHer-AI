// ===============================
// SAFEHER AI - BASE JAVASCRIPT
// ===============================

document.addEventListener("DOMContentLoaded", function () {

    // Mobile menu
    const menuButton = document.getElementById("menuButton");
    const mobileMenu = document.getElementById("mobileMenu");

    if (menuButton && mobileMenu) {
        menuButton.addEventListener("click", function () {
            mobileMenu.classList.toggle("show");
        });
    }

    // Automatically hide flash messages
    const flashMessages =
        document.querySelectorAll(".flash-message");

    flashMessages.forEach(function (message) {

        setTimeout(function () {
            message.style.opacity = "0";

            setTimeout(function () {
                message.remove();
            }, 400);

        }, 4000);

    });

});
