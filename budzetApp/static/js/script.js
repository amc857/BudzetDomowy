document.addEventListener('DOMContentLoaded', function() {
    const menuIcon = document.querySelector('.menu-icon');
    const sideMenu = document.getElementById('sideMenu');
    const mainContent = document.querySelector('.main');

    // Funkcja zamykania menu
    function closeMenu() {
        sideMenu.classList.remove('active');
        mainContent.classList.remove('shifted');
    }

    // Otwieranie/zamykanie menu przez kliknięcie ikony
    menuIcon.addEventListener('click', function(event) {
        event.stopPropagation(); // Zatrzymaj propagację eventu
        sideMenu.classList.toggle('active');
        mainContent.classList.toggle('shifted');
    });

    // Zamykanie menu po kliknięciu poza menu
    document.addEventListener('click', function(event) {
        if (!sideMenu.contains(event.target) && 
            !menuIcon.contains(event.target)) {
            closeMenu();
        }
    });

    // Opcjonalnie: zamykanie menu przy przewijaniu
    window.addEventListener('scroll', closeMenu);
});