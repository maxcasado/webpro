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
        logoutLink: document.getElementById('logout-link'),
        navMenu: document.getElementById('nav-menu')  // 👈 Assure-toi que ton HTML a cet ID
    },

    // Initialisation de l'interface
    init: function() {
        this.updateNavigation();
        this.setupEventListeners();
    },

    // Configuration des écouteurs d'événements
    setupEventListeners: function() {
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('nav-link')) {
                e.preventDefault();
                const page = e.target.getAttribute('data-page');
                if (page) {
                    App.loadPage(page);
                }
            }
        });

        const logoutLink = this.elements.logoutLink;
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

    // Mise à jour de la navigation
    updateNavigation: function() {
        const isAuthenticated = Auth.isAuthenticated();
        const user = Auth.getUser();
        const isAdmin = user && user.is_admin;

        const authRequired = document.querySelectorAll('.auth-required');
        const adminRequired = document.querySelectorAll('.admin-required');
        const userOnly = document.querySelectorAll('.user-only');

        authRequired.forEach(item => item.classList.toggle('hidden', !isAuthenticated));
        adminRequired.forEach(item => {
            item.classList.toggle('hidden', !isAdmin);
            item.style.display = isAdmin ? 'block' : 'none';
        });
        userOnly.forEach((item, index) => {
            item.classList.toggle('hidden', !isAuthenticated || isAdmin);
            item.style.display = (isAuthenticated && !isAdmin) ? 'block' : 'none';
        });


        document.querySelectorAll('[data-page="login"], [data-page="register"]').forEach(link => {
            const listItem = link.parentElement;
            listItem.classList.toggle('hidden', isAuthenticated);
        });

        // 🆕 Ajout de l'onglet "Mes emprunts" si utilisateur authentifié (non admin)
        const navMenu = this.elements.navMenu;
        if (navMenu && isAuthenticated && !isAdmin) {
            if (!navMenu.querySelector('[data-page="my-loans"]')) {
                const li = document.createElement('li');
                li.innerHTML = `<a href="#" class="nav-link" data-page="my-loans">📚 Mes emprunts</a>`;
                navMenu.appendChild(li);
            }
        }
    },

    // Affiche un message
    showMessage: function(text, type = 'success') {
        this.elements.message.textContent = text;
        this.elements.message.className = type;
        this.elements.messageContainer.classList.remove('hidden');
        setTimeout(() => this.hideMessage(), 5000);
    },

    hideMessage: function() {
        this.elements.messageContainer.classList.add('hidden');
    },

    showLoading: function() {
        this.elements.loading.classList.remove('hidden');
    },

    hideLoading: function() {
        this.elements.loading.classList.add('hidden');
    },

    setContent: function(html) {
        this.elements.pageContent.innerHTML = html;
    }
};
