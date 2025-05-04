// Card entrance animation on scroll
document.addEventListener("DOMContentLoaded", function() {
    const cards = document.querySelectorAll('.movie-card');
    const observer = new IntersectionObserver(entries => {
        entries.forEach(entry => {
            if(entry.isIntersecting) {
                entry.target.classList.add('show');
            }
        });
    }, { threshold: 0.15 });

    cards.forEach(card => {
        observer.observe(card);
    });
});

// Dark/Light mode toggle
document.addEventListener("DOMContentLoaded", function() {
    const toggleBtn = document.getElementById('theme-toggle');
    if (!toggleBtn) return;
    toggleBtn.addEventListener('click', function() {
        document.body.classList.toggle('light-mode');
        if(document.body.classList.contains('light-mode')) {
            toggleBtn.innerHTML = '<i class="fas fa-moon"></i> Dark';
        } else {
            toggleBtn.innerHTML = '<i class="fas fa-sun"></i> Light';
        }
    });
});

// Ripple effect for buttons
document.addEventListener("DOMContentLoaded", function() {
    document.querySelectorAll('button, .genre-filter a, .alphabet-filter a, nav a').forEach(el => {
        el.addEventListener('click', function(e) {
            let ripple = document.createElement('span');
            ripple.className = 'ripple';
            ripple.style.left = (e.offsetX) + 'px';
            ripple.style.top = (e.offsetY) + 'px';
            this.appendChild(ripple);
            setTimeout(() => ripple.remove(), 600);
        });
    });
});