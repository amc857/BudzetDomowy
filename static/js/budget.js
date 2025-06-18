document.addEventListener('DOMContentLoaded', function () {
    console.log('🔧 DOM fully loaded');
    
    const cards = document.querySelectorAll('.budget-card');
    console.log(`🟣 Found ${cards.length} cards`);

    cards.forEach(card => {
        card.addEventListener('click', function () {
            const url = this.getAttribute('data-url');
            console.log(`➡️ Redirecting to: ${url}`);
            window.location = url;
        });
    });
});
