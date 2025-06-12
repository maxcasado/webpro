// Configuration de l'application
const CONFIG = {
    // URL de base de l'API
    API_URL: 'http://localhost:8000/api/v2',

    // Durée de vie du token en millisecondes (8 jours)
    TOKEN_EXPIRY: 8 * 24 * 60 * 60 * 1000,

    // Clés de stockage local
    STORAGE_KEYS: {
        TOKEN: 'auth_token',
        USER: 'user_data',
        TOKEN_EXPIRY: 'token_expiry'
    }
};