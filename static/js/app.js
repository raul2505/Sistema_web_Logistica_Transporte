const toggle = document.querySelector(".toggle");
const menuDashboard = document.querySelector(".menu-dashboard");
const iconoMenu = toggle.querySelector("i");
const enlacesMenu = document.querySelectorAll(".enlace");

// Alternar el estado del menú
toggle.addEventListener("click", () => {
    menuDashboard.classList.toggle("open");

    // Cambiar el ícono del menú
    if (iconoMenu.classList.contains("bx-menu")) {
        iconoMenu.classList.replace("bx-menu", "bx-x");
    } else {
        iconoMenu.classList.replace("bx-x", "bx-menu");
    }
});

// Redirección al hacer clic en un enlace del menú
function navigateTo(url) {
    window.location.href = url;
}
