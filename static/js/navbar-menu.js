document.addEventListener("DOMContentLoaded", function () {
    const burgerMenu = document.querySelector(".burger-menu");
    const closeMenu = document.querySelector(".close-menu");
    const mobileMenuOverlay = document.querySelector(".mobile-menu-overlay");
  
    burgerMenu.addEventListener("click", function () {
      mobileMenuOverlay.classList.remove("hidden");
      mobileMenuOverlay.classList.add("visible");
    });
  
    closeMenu.addEventListener("click", function () {
      mobileMenuOverlay.classList.remove("visible");
      mobileMenuOverlay.classList.add("hidden");
    });
  });