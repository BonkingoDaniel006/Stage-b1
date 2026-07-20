/**
 * On encapsule toute la logique de l'application dans un objet `App`
 * pour éviter de polluer l'espace de noms global et pour mieux organiser le code.
 */
const App = {
  // --- PROPRIÉTÉS ---
  state: {
    isPunchedIn: false,
    isOnline: true,
  },

  // --- ÉLÉMENTS DU DOM ---
  elements: {
    sidebar: document.getElementById('sidebar'),
    overlay: document.getElementById('overlay'),
    pageTitle: document.getElementById('page-title'),
    navButtons: document.querySelectorAll('.nav-btn'),
    tabPanels: document.querySelectorAll('.tab-panel'),
    liveClock: document.getElementById('live-clock'),
    todayDate: document.getElementById('today-date'),
    punchBtn: document.getElementById('punch-btn'),
    punchIcon: document.getElementById('punch-icon'),
    punchLabel: document.getElementById('punch-label'),
    punchStatus: document.getElementById('punch-status'),
    networkPill: document.getElementById('network-pill'),
    networkDot: document.getElementById('network-dot'),
    networkText: document.getElementById('network-text'),
    networkIcon: document.getElementById('network-icon'),
    ticketForm: document.getElementById('ticket-form'),
    ticketList: document.getElementById('ticket-list'),
    toastContainer: document.getElementById('toast-container'),
  },

  // --- CONSTANTES ---
  config: {
    tabTitles: {
      dashboard: "Tableau de bord",
      presence: "Présence & Planning",
      maintenance: "Gestion de Maintenance & Fret",
      rh: "Communiqués & RH",
      notifications: "Notifications",
      profile: "Mon Profil"
    },
    ticketIcons: {
      "Locomotive": { icon: "fa-train", bg: "bg-red-50", color: "text-red-500" },
      "Wagon de fret": { icon: "fa-box", bg: "bg-sky-50", color: "text-sky-500" },
      "Wagon-citerne": { icon: "fa-gas-pump", bg: "bg-sky-50", color: "text-sky-500" },
      "Infrastructure voie": { icon: "fa-road-barrier", bg: "bg-slate-100", color: "text-slate-400" },
      "Signalisation": { icon: "fa-tower-broadcast", bg: "bg-orange-50", color: "text-orange-500" }
    }
  },

  // --- MÉTHODES ---
  init() {
    console.log("SNCC Connect App Initializing...");
    this.bindEvents();
    this.updateClock();
    setInterval(() => this.updateClock(), 1000);
    this.updateDate();

    // Message de bienvenue
    setTimeout(() => {
      this.showToast('success', 'Bienvenue sur SNCC Connect', 'Prototype de démonstration — Intranet Collaboratif SNCC.');
    }, 800);
  },

  bindEvents() {
    // Navigation
    this.elements.navButtons.forEach(btn => {
      btn.addEventListener('click', () => this.showTab(btn.dataset.tab, btn));
    });

    // Sidebar
    document.querySelectorAll('[data-action="toggle-sidebar"]').forEach(el => {
      el.addEventListener('click', () => this.toggleSidebar());
    });

    // Pointage
    this.elements.punchBtn.addEventListener('click', () => this.togglePunch());
    
    // Simulation réseau
    document.querySelector('[data-action="toggle-network"]').addEventListener('click', () => this.toggleNetwork());
    
    // Formulaires
    this.elements.ticketForm.addEventListener('submit', (e) => this.submitTicket(e));
    document.querySelector('form[data-action="submit-request"]').addEventListener('submit', (e) => this.submitRequest(e));
  },

  showTab(tabName, btn) {
    this.elements.tabPanels.forEach(p => p.classList.remove('active'));
    document.getElementById('tab-' + tabName).classList.add('active');

    this.elements.navButtons.forEach(b => b.classList.remove('active'));
    if (btn) {
        btn.classList.add('active');
        // Gérer le cas où on clique sur un lien qui n'est pas un bouton de nav principal
        const mainBtn = document.querySelector(`.nav-btn[data-tab=${btn.dataset.tab}]`);
        if(mainBtn) mainBtn.classList.add('active');
    }

    this.elements.pageTitle.textContent = this.config.tabTitles[tabName];

    if (window.innerWidth < 1024) this.toggleSidebar(true);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  },

  toggleSidebar(forceClose) {
    const shouldClose = forceClose === true || this.elements.sidebar.classList.contains('open');
    if (shouldClose) {
      this.elements.sidebar.classList.remove('open');
      this.elements.overlay.classList.add('hidden');
    } else {
      this.elements.sidebar.classList.add('open');
      this.elements.overlay.classList.remove('hidden');
    }
  },

  updateClock() {
    this.elements.liveClock.textContent = new Date().toLocaleTimeString('fr-FR');
  },

  updateDate() {
    this.elements.todayDate.textContent = new Date().toLocaleDateString('fr-FR', {
      weekday: 'long', year: 'numeric', month: 'long', day: 'numeric'
    });
  },

  togglePunch() {
    const now = new Date().toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' });
    this.state.isPunchedIn = !this.state.isPunchedIn;

    if (this.state.isPunchedIn) {
      this.elements.punchBtn.classList.remove('bg-sky-600', 'hover:bg-sky-700');
      this.elements.punchBtn.classList.add('bg-orange-500', 'hover:bg-orange-600');
      this.elements.punchIcon.className = 'fa-solid fa-right-from-bracket text-2xl';
      this.elements.punchLabel.textContent = "Pointer le départ";
      this.elements.punchStatus.innerHTML = `<i class="fa-solid fa-circle-check text-emerald-500 mr-1"></i> Arrivée enregistrée à ${now}`;
      this.showToast('success', 'Pointage enregistré', `Arrivée confirmée à ${now}.`);
    } else {
      this.elements.punchBtn.classList.remove('bg-orange-500', 'hover:bg-orange-600');
      this.elements.punchBtn.classList.add('bg-sky-600', 'hover:bg-sky-700');
      this.elements.punchIcon.className = 'fa-solid fa-fingerprint text-2xl';
      this.elements.punchLabel.textContent = "Pointer l'arrivée";
      this.elements.punchStatus.innerHTML = `<i class="fa-solid fa-circle-check text-emerald-500 mr-1"></i> Départ enregistré à ${now}`;
      this.showToast('success', 'Pointage enregistré', `Départ confirmé à ${now}.`);
    }
  },

  toggleNetwork() {
    this.state.isOnline = !this.state.isOnline;

    if (this.state.isOnline) {
      this.elements.networkPill.className = "flex items-center gap-2 bg-emerald-50 text-emerald-700 border border-emerald-200 px-3 py-1.5 rounded-full text-xs font-semibold";
      this.elements.networkDot.className = "w-2 h-2 rounded-full bg-emerald-500 pulse-dot";
      this.elements.networkText.textContent = "Statut Réseau : Connecté (Serveur central)";
      this.elements.networkIcon.className = "fa-solid fa-wifi text-sm";
      this.showToast('success', 'Réseau rétabli', "Toutes les données locales ont été synchronisées avec le serveur central.");
    } else {
      this.elements.networkPill.className = "flex items-center gap-2 bg-orange-50 text-orange-700 border border-orange-200 px-3 py-1.5 rounded-full text-xs font-semibold";
      this.elements.networkDot.className = "w-2 h-2 rounded-full bg-orange-500 pulse-dot offline";
      this.elements.networkText.textContent = "Mode Hors-ligne (Données synchronisées en local)";
      this.elements.networkIcon.className = "fa-solid fa-wifi-slash text-sm";
      this.showToast('warning', 'Connexion perdue', "Basculement en mode hors-ligne. Les données seront synchronisées localement.");
    }
  },

  submitTicket(e) {
    e.preventDefault();

    const type = document.getElementById('ticket-type').value;
    const id = document.getElementById('ticket-id').value.trim();
    const priority = document.getElementById('ticket-priority').value;
    const desc = document.getElementById('ticket-desc').value.trim();

    if (!id || !desc) return;

    const meta = this.config.ticketIcons[type] || this.config.ticketIcons["Locomotive"];
    const priorityText = priority === "Critique — Immobilisation" ? " — priorité critique." : priority === "Élevée" ? " — priorité élevée." : "";

    const newTicket = document.createElement('div');
    newTicket.className = "ticket-item ticket-new flex items-start gap-3 border border-sky-200 rounded-lg p-3 bg-sky-50/40";
    newTicket.innerHTML = `
      <div class="w-10 h-10 rounded-lg ${meta.bg} ${meta.color} flex items-center justify-center shrink-0"><i class="fa-solid ${meta.icon}"></i></div>
      <div class="flex-1 min-w-0">
        <div class="flex items-center justify-between gap-2 flex-wrap">
          <p class="text-sm font-semibold text-slate-700">${type} ${id}</p>
          <span class="bg-slate-100 text-slate-500 text-xs font-semibold px-2 py-0.5 rounded-full whitespace-nowrap">En attente</span>
        </div>
        <p class="text-xs text-slate-500 mt-0.5">${desc}${priorityText}</p>
        <p class="text-[11px] text-slate-400 mt-1">Déclaré par Jonas Kabeya — à l'instant ${!this.state.isOnline ? '<i class="fa-solid fa-cloud-arrow-up text-orange-400 ml-1" title="En attente de synchronisation"></i>' : ''}</p>
      </div>
    `;

    this.elements.ticketList.prepend(newTicket);
    e.target.reset();
    
    if (!this.state.isOnline) {
      this.showToast('warning', 'Alerte — Mode hors-ligne', "Connexion indisponible. Votre rapport est sauvegardé localement et sera transmis dès le retour du réseau.");
    } else {
      this.showToast('success', 'Ticket créé', "Le rapport de panne a été transmis avec succès à l'atelier de maintenance.");
    }
  },

  submitRequest(e) {
    e.preventDefault();
    e.target.reset();
    if (!this.state.isOnline) {
      this.showToast('warning', 'Alerte — Mode hors-ligne', "Votre demande a été enregistrée localement et sera transmise dès le retour du réseau.");
    } else {
      this.showToast('success', 'Demande envoyée', "Votre demande a été transmise au service RH pour traitement.");
    }
  },

  showToast(type, title, message) {
    const colors = {
      success: { bg: "bg-white", border: "border-emerald-200", icon: "fa-circle-check", iconColor: "text-emerald-500" },
      warning: { bg: "bg-white", border: "border-orange-300", icon: "fa-triangle-exclamation", iconColor: "text-orange-500" }
    };
    const c = colors[type] || colors.success;

    const toast = document.createElement('div');
    toast.className = `toast ${c.bg} border ${c.border} shadow-lg rounded-lg p-4 w-72 sm:w-80 flex gap-3 items-start`;
    toast.innerHTML = `
      <i class="fa-solid ${c.icon} ${c.iconColor} mt-0.5"></i>
      <div class="flex-1">
        <p class="text-sm font-semibold text-slate-800">${title}</p>
        <p class="text-xs text-slate-500 mt-0.5">${message}</p>
      </div>
      <button onclick="this.parentElement.remove()" class="text-slate-300 hover:text-slate-500">
        <i class="fa-solid fa-xmark text-xs"></i>
      </button>
    `;
    this.elements.toastContainer.appendChild(toast);

    setTimeout(() => {
      toast.style.transition = "opacity .4s ease";
      toast.style.opacity = "0";
      setTimeout(() => toast.remove(), 400);
    }, 6000);
  }
};

// Démarrage de l'application une fois que le DOM est prêt
document.addEventListener('DOMContentLoaded', () => {
  App.init();
});