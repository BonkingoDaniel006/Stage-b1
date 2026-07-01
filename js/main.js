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

            const duration = 1500; // Durée de l'animation en ms
            let startTimestamp = null;

            const step = (timestamp) => {
                if (!startTimestamp) startTimestamp = timestamp;
                const progress = Math.min((timestamp - startTimestamp) / duration, 1);
                const currentValue = Math.floor(progress * target);
                counter.innerText = currentValue.toLocaleString('fr-FR');

                if (progress < 1) {
                    window.requestAnimationFrame(step);
                } else {
                    counter.innerText = target.toLocaleString('fr-FR');
                }
            };

            window.requestAnimationFrame(step);
        });
    };

    // --- ANIMATION D'APPARITION AU SCROLL (FADE UP) ---
    const sectionsToAnimate = document.querySelectorAll('section[id]');

    const revealObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                // Ajoute la classe 'is-visible' pour déclencher l'animation CSS
                entry.target.classList.add('is-visible');

                // Déclenche l'animation des compteurs si la section stats est visible
                const statsSection = document.querySelector('.stats');
                if (statsSection && statsSection.contains(entry.target) || entry.target.classList.contains('stats')) {
                    // Un peu complexe car .stats n'est pas une <section>
                    // On vérifie si l'élément observé est dans .stats
                    // ou si c'est le conteneur .stats lui-même (au cas où on l'observerait)
                    const statsWrap = document.querySelector('.stats .wrap');
                    if(statsWrap.getBoundingClientRect().top < window.innerHeight) {
                       animateCounters();
                    }
                }
            }
        });
    }, {
        threshold: 0.1 // Déclenche l'animation quand 10% de la section est visible
    });

    // Observe chaque section
    sectionsToAnimate.forEach(section => {
        revealObserver.observe(section);
    });
    // Observe aussi la section des stats qui n'est pas une <section>
    const statsSection = document.querySelector('.stats');
    if (statsSection) revealObserver.observe(statsSection);
});