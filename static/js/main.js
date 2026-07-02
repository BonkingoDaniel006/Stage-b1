document.addEventListener("DOMContentLoaded", () => {

    /**
     * Fonction pour animer les compteurs de statistiques.
     */
    const animateCounters = () => {
        const counters = document.querySelectorAll(".stats .num[data-target]");
        if (counters.length === 0) return;

        counters.forEach(counter => {
            // Empêche de relancer l'animation si elle a déjà eu lieu
            if (counter.dataset.animated) return;
            counter.dataset.animated = "true";

            const target = parseInt(counter.getAttribute("data-target"));
            if (isNaN(target)) return;

            const duration = 2000; // Durée de l'animation en millisecondes
            let startTimestamp = null;

            const animationStep = (timestamp) => {
                if (!startTimestamp) startTimestamp = timestamp;
                const progress = Math.min((timestamp - startTimestamp) / duration, 1);
                const currentValue = Math.floor(progress * target);
                counter.innerText = currentValue.toLocaleString('fr-FR');

                if (progress < 1) {
                    window.requestAnimationFrame(animationStep);
                } else {
                    counter.innerText = target.toLocaleString('fr-FR');
                }
            };

            window.requestAnimationFrame(animationStep);
        });
    };

    /**
     * Utilise IntersectionObserver pour déclencher les animations au défilement.
     * Cible uniquement la section des statistiques.
     */
    const statsSection = document.querySelector('.stats');
    if (statsSection) {
        const observer = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    animateCounters();
                    observer.unobserve(entry.target); // On arrête d'observer une fois l'animation lancée
                }
            });
        }, { threshold: 0.5 }); // Déclenche quand 50% de la section est visible
        observer.observe(statsSection);
    }
});