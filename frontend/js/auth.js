// Gestion de l'authentification
const Auth = {
    // Stocke le token JWT et les informations utilisateur
    setToken: function(token, expiresIn = CONFIG.TOKEN_EXPIRY) {
        const now = new Date();
        const expiryTime = now.getTime() + expiresIn;

        localStorage.setItem(CONFIG.STORAGE_KEYS.TOKEN, token);
        localStorage.setItem(CONFIG.STORAGE_KEYS.TOKEN_EXPIRY, expiryTime);
    },

    // Récupère le token JWT
    getToken: function() {
        return localStorage.getItem(CONFIG.STORAGE_KEYS.TOKEN);
    },

    // Vérifie si le token est valide et non expiré
    isAuthenticated: function() {
        const token = this.getToken();
        console.log('Checking authentication - token exists:', !!token);
        
        if (!token) return false;

        const expiryTime = localStorage.getItem(CONFIG.STORAGE_KEYS.TOKEN_EXPIRY);
        console.log('Token expiry time:', expiryTime);
        
        if (!expiryTime) return false;

        const now = new Date();
        const isValid = now.getTime() < parseInt(expiryTime);
        console.log('Token is valid:', isValid, 'Current time:', now.getTime(), 'Expiry:', parseInt(expiryTime));
        
        return isValid;
    },

    // Stocke les informations utilisateur
    setUser: function(userData) {
        console.log('Setting user data:', userData);
        console.log('User is admin:', userData && userData.is_admin);
        localStorage.setItem(CONFIG.STORAGE_KEYS.USER, JSON.stringify(userData));
    },

    // Récupère les informations utilisateur
    getUser: function() {
        const userData = localStorage.getItem(CONFIG.STORAGE_KEYS.USER);
        const user = userData ? JSON.parse(userData) : null;
        console.log('Getting user data:', user);
        console.log('User is admin:', user && user.is_admin);
        return user;
    },

    // Déconnecte l'utilisateur
    logout: function() {
        localStorage.removeItem(CONFIG.STORAGE_KEYS.TOKEN);
        localStorage.removeItem(CONFIG.STORAGE_KEYS.TOKEN_EXPIRY);
        localStorage.removeItem(CONFIG.STORAGE_KEYS.USER);
    }
};