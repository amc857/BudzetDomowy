/* SideBar menu animation */

document.addEventListener('DOMContentLoaded', function() {
    const menuIcon = document.querySelector('.menu-icon');
    const sideMenu = document.getElementById('sideMenu');
    const mainContent = document.querySelector('.main');

    function closeMenu() {
        sideMenu.classList.remove('active');
        mainContent.classList.remove('shifted');
    }

    menuIcon.addEventListener('click', function(event) {
        event.stopPropagation(); 
        sideMenu.classList.toggle('active');
        mainContent.classList.toggle('shifted');
    });

    document.addEventListener('click', function(event) {
        if (!sideMenu.contains(event.target) && 
            !menuIcon.contains(event.target)) {
            closeMenu();
        }
    });

    window.addEventListener('scroll', closeMenu);
});