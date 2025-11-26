// newsfeed/static/js/script.js

document.addEventListener('DOMContentLoaded', function() {
    console.log("News Feed Website base script loaded.");

    // Functionality for Header/Navigation (Optional, already handled mostly by CSS)
    const navLinks = document.querySelectorAll('.main-nav ul li a');
    navLinks.forEach(link => {
        link.addEventListener('click', function() {
            // Optional logging or active state logic
            console.log('Navigated to:', this.textContent);
        });
    });

    // Add any global JavaScript functionality here, if needed.
    // Jaise: Sticky header, general search functionality, etc.
});