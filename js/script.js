document.addEventListener("DOMContentLoaded", () => {
    
    // --- 1. EFFET D'APPARITION AU SCROLL (REVEAL ANIMATION) ---
    const reveals = document.querySelectorAll(".reveal");

    const revealOnScroll = () => {
        const windowHeight = window.innerHeight;
        
        reveals.forEach(reveal => {
            const elementTop = reveal.getBoundingClientRect().top;
            const elementVisible = 100; // Marge de déclenchement en pixels
            
            if (elementTop < windowHeight - elementVisible) {
                reveal.classList.add("active");
                
                // Si l'élément contient des compteurs, on lance l'animation de compte
                if(reveal.classList.contains('stats-section')) {
                    animateCounters();
                }
            }
        });
    };

    window.addEventListener("scroll", revealOnScroll);
    // Lancement initial au cas où des éléments sont déjà visibles
    revealOnScroll();


    // --- 2. COMPTEURS ANIMÉS DYNAMIQUES ---
    let countersStarted = false;

    const animateCounters = () => {
        if (countersStarted) return; // Évite de relancer l'animation plusieurs fois
        countersStarted = true;

        const counters = document.querySelectorAll(".stat-number");
        
        counters.forEach(counter => {
            const target = parseInt(counter.getAttribute("data-target"));
            const speed = 200; // Plus le chiffre est grand, plus c'est rapide
            const increment = target / speed;

            const updateCount = () => {
                const count = parseInt(counter.innerText);
                if (count < target) {
                    counter.innerText = Math.ceil(count + increment);
                    setTimeout(updateCount, 15);
                } else {
                    counter.innerText = target + "+"; // Ajoute un "+" à la fin
                }
            };
            updateCount();
        });
    };


    // --- 3. EFFET DE NAVBAR SUR ÉVÉNEMENT HOVER INTERACTIF ---
    const navLinks = document.querySelectorAll(".nav-links a");
    navLinks.forEach(link => {
        link.addEventListener("click", function() {
            navLinks.forEach(lnk => lnk.classList.remove("active"));
            this.classList.add("active");
        });
    });

    // --- 4. MENU HAMBURGER POUR MOBILE ---
    const hamburger = document.querySelector(".hamburger");
    const navMenu = document.querySelector(".nav-links");

    if(hamburger && navMenu) {
        hamburger.addEventListener("click", () => {
            navMenu.classList.toggle("active");
        });
    }
});