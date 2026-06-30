document.addEventListener("DOMContentLoaded", () => {

    // --- ANIMATION DES COMPTEURS DE STATISTIQUES ---
    let countersAnimated = false;

    const animateCounters = () => {
        if (countersAnimated) return; // Empêche de relancer l'animation

        const counters = document.querySelectorAll(".stats .num");
        if (counters.length === 0) return;

        countersAnimated = true;

        counters.forEach(counter => {
            const target = parseInt(counter.getAttribute("data-target"));
            if (isNaN(target)) return;

            let count = 0;
            const duration = 2000; // Durée de l'animation en ms
            const stepTime = Math.abs(Math.floor(duration / target));

            const updateCount = () => {
                const increment = Math.ceil(target / (duration / 15));
                
                if (count < target) {
                    count += increment;
                    if (count > target) count = target; // Assure de ne pas dépasser la cible
                    counter.innerText = count.toLocaleString('fr-FR');
                    setTimeout(updateCount, 15);
                } else {
                    counter.innerText = target.toLocaleString('fr-FR');
                    // Ajoute le "+" ou "ans" si nécessaire après l'animation
                    if (target === 1200) counter.innerText += "+";
                }
            };
            updateCount();
        });
    };

    // --- DÉCLENCHEMENT AU SCROLL ---
    // On utilise IntersectionObserver pour de meilleures performances
    const statsSection = document.querySelector('.stats');

    if (statsSection) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                // Si la section est visible à l'écran
                if (entry.isIntersecting) {
                    animateCounters();
                    observer.unobserve(entry.target); // On arrête d'observer une fois l'animation lancée
                }
            });
        }, { threshold: 0.5 }); // Déclenche quand 50% de la section est visible

        observer.observe(statsSection);
    }
});