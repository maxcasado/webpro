// Gestion de l'interface utilisateur
const UI = {
    // Éléments DOM
    elements: {
        content: document.getElementById('content'),
        pageContent: document.getElementById('page-content'),
        loading: document.getElementById('loading'),
        messageContainer: document.getElementById('message-container'),
        message: document.getElementById('message'),
        navLinks: document.querySelectorAll('.nav-link'),
        authRequired: document.querySelectorAll('.auth-required'),
        adminRequired: document.querySelectorAll('.admin-required'),
        logoutLink: document.getElementById('logout-link')
    },

    // Initialisation de l'interface
    init: function() {
        this.updateNavigation();
        this.setupEventListeners();
    },

    // Configuration des écouteurs d'événements
    setupEventListeners: function() {
        // Navigation - Use event delegation to handle dynamically shown elements
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('nav-link')) {
                e.preventDefault();
                const page = e.target.getAttribute('data-page');
                if (page) {
                    App.loadPage(page);
                }
            }
        });

        // Déconnexion
        const logoutLink = document.getElementById('logout-link');
        if (logoutLink) {
            logoutLink.addEventListener('click', (e) => {
                e.preventDefault();
                Auth.logout();
                this.updateNavigation();
                App.loadPage('login');
                this.showMessage('Vous avez été déconnecté avec succès', 'success');
            });
        }
    },

    // Mise à jour de la navigation en fonction de l'état d'authentification
    updateNavigation: function() {
        const isAuthenticated = Auth.isAuthenticated();
        const user = Auth.getUser();
        const isAdmin = user && user.is_admin;

        // Re-query the DOM elements to get fresh references
        const authRequired = document.querySelectorAll('.auth-required');
        const adminRequired = document.querySelectorAll('.admin-required');
        const userOnly = document.querySelectorAll('.user-only');

        authRequired.forEach((item, index) => {
            item.classList.toggle('hidden', !isAuthenticated);
        });

        adminRequired.forEach((item, index) => {
            item.classList.toggle('hidden', !isAdmin);
            // Force display style as backup
            item.style.display = isAdmin ? 'block' : 'none';
        });

        // Hide user-only items for admins (they have their own admin panel)
        userOnly.forEach((item, index) => {
            item.classList.toggle('hidden', !isAuthenticated || isAdmin);
            item.style.display = (isAuthenticated && !isAdmin) ? 'block' : 'none';
        });

        // Afficher/masquer les liens de connexion/inscription
        document.querySelectorAll('[data-page="login"], [data-page="register"]').forEach(link => {
            const listItem = link.parentElement;
            listItem.classList.toggle('hidden', isAuthenticated);
        });
    },

    // Affiche un message à l'utilisateur
    showMessage: function(text, type = 'success') {
        this.elements.message.textContent = text;
        this.elements.message.className = type;
        this.elements.messageContainer.classList.remove('hidden');

        // Masquer le message après 5 secondes
        setTimeout(() => {
            this.hideMessage();
        }, 5000);
    },

    // Masque le message
    hideMessage: function() {
        this.elements.messageContainer.classList.add('hidden');
    },

    // Affiche l'indicateur de chargement
    showLoading: function() {
        this.elements.loading.classList.remove('hidden');
    },

    // Masque l'indicateur de chargement
    hideLoading: function() {
        this.elements.loading.classList.add('hidden');
    },

    // Charge le contenu HTML dans la page
    setContent: function(html) {
        this.elements.pageContent.innerHTML = html;
    }
};