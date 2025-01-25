document.addEventListener("DOMContentLoaded", function () {
    const dropdownToggles = document.querySelectorAll(".dropdown-toggle");

    dropdownToggles.forEach((toggle) => {
        toggle.addEventListener("click", function (event) {
            event.preventDefault();
            const menu = this.nextElementSibling;
            document.querySelectorAll(".dropdown-menu").forEach((dropdown) => {
                if (dropdown !== menu) {
                    dropdown.style.display = "none";
                }
            });
            menu.style.display = menu.style.display === "block" ? "none" : "block";
        });
    });

    document.addEventListener("click", function (event) {
        if (!event.target.closest(".dropdown")) {
            document.querySelectorAll(".dropdown-menu").forEach((dropdown) => {
                dropdown.style.display = "none";
            });
        }
    });
});
