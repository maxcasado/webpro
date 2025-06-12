// Gestion des appels API
const Api = {
    // Headers par défaut pour les requêtes
    getHeaders: function() {
        const headers = {
            'Content-Type': 'application/json'
        };

        if (Auth.isAuthenticated()) {
            const token = Auth.getToken();
            console.log('Adding authorization header with token:', token ? 'Token present' : 'No token');
            headers['Authorization'] = `Bearer ${token}`;
        } else {
            console.log('User not authenticated, no authorization header added');
        }

        console.log('Request headers:', headers);
        return headers;
    },

    // Appel API générique
    call: async function(endpoint, method = 'GET', data = null) {
        console.log(`Making ${method} request to ${endpoint}`);
        UI.showLoading();

        const url = `${CONFIG.API_URL}${endpoint}`;
        const options = {
            method: method,
            headers: this.getHeaders()
        };

        if (data && (method === 'POST' || method === 'PUT' || method === 'PATCH')) {
            options.body = JSON.stringify(data);
        }

        console.log('Request URL:', url);
        console.log('Request options:', options);

        try {
            const response = await fetch(url, options);
            console.log('Response status:', response.status, response.statusText);
            
            // Check if response is JSON
            let responseData;
            try {
                responseData = await response.json();
            } catch (jsonError) {
                console.error('Failed to parse JSON response:', jsonError);
                throw new Error(`Erreur de communication avec le serveur (${response.status})`);
            }

            console.log('Response data:', responseData);

            if (!response.ok) {
                // Handle different error types
                if (response.status === 422) {
                    // Validation errors
                    const errorMessage = responseData.detail?.[0]?.msg || responseData.detail || 'Erreur de validation';
                    throw new Error(errorMessage);
                }
                throw new Error(responseData.detail || `Erreur ${response.status}: ${response.statusText}`);
            }

            UI.hideLoading();
            return responseData;
        } catch (error) {
            console.error('API call failed:', error);
            UI.hideLoading();
            UI.showMessage(error.message, 'error');
            throw error;
        }
    },

    // Méthodes spécifiques
    login: async function(email, password) {
        const formData = new URLSearchParams();
        formData.append('username', email);
        formData.append('password', password);

        UI.showLoading();

        try {
            const response = await fetch(`${CONFIG.API_URL}/auth/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                body: formData
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || 'Échec de la connexion');
            }

            // Stocker le token
            Auth.setToken(data.access_token);

            // Récupérer les informations utilisateur
            await this.getCurrentUser();

            UI.hideLoading();
            return data;
        } catch (error) {
            UI.hideLoading();
            UI.showMessage(error.message, 'error');
            throw error;
        }
    },

    register: async function(userData) {
        console.log('Attempting registration with data:', userData);
        try {
            const result = await this.call('/users/', 'POST', userData);
            console.log('Registration successful:', result);
            return result;
        } catch (error) {
            console.error('Registration failed:', error);
            throw error;
        }
    },

    getCurrentUser: async function() {
        try {
            const userData = await this.call('/users/me');
            console.log('User data retrieved:', userData);
            Auth.setUser(userData);
            
            // Update navigation after setting user data
            UI.updateNavigation();
            
            return userData;
        } catch (error) {
            Auth.logout();
            throw error;
        }
    },

    getBooks: async function(skip = 0, limit = 100) {
        console.log('Fetching books with pagination...');
        try {
            const response = await this.call(`/books/?skip=${skip}&limit=${limit}`);
            console.log('Books API response:', response);
            
            // Check if response has the paginated structure
            if (response && response.items) {
                return response.items; // Return just the items array
            }
            
            // If it's already an array, return as is
            if (Array.isArray(response)) {
                return response;
            }
            
            // Fallback to empty array
            return [];
        } catch (error) {
            console.error('Error fetching books:', error);
            throw error;
        }
    },

    getBook: async function(id) {
        return this.call(`/books/${id}`);
    },

    // Create a new book (admin only)
    createBook: async function(bookData) {
        console.log('Creating book with data:', bookData);
        try {
            const result = await this.call('/books/', 'POST', bookData);
            console.log('Book created successfully:', result);
            return result;
        } catch (error) {
            console.error('Book creation failed:', error);
            throw error;
        }
    },

    // Update an existing book (admin only)
    updateBook: async function(id, bookData) {
        console.log(`Updating book ${id} with data:`, bookData);
        try {
            const result = await this.call(`/books/${id}`, 'PUT', bookData);
            console.log('Book updated successfully:', result);
            return result;
        } catch (error) {
            console.error('Book update failed:', error);
            throw error;
        }
    },

    // Delete a book (admin only)
    deleteBook: async function(id) {
        console.log(`Deleting book ${id}`);
        try {
            const result = await this.call(`/books/${id}`, 'DELETE');
            console.log('Book deleted successfully:', result);
            return result;
        } catch (error) {
            console.error('Book deletion failed:', error);
            throw error;
        }
    },

    // Search books by title
    searchBooksByTitle: async function(title) {
        console.log('Searching books by title:', title);
        try {
            const result = await this.call(`/books/search/title/${encodeURIComponent(title)}`);
            console.log('Title search results:', result);
            return result;
        } catch (error) {
            console.error('Title search failed:', error);
            throw error;
        }
    },

    // Search books by author
    searchBooksByAuthor: async function(author) {
        console.log('Searching books by author:', author);
        try {
            const result = await this.call(`/books/search/author/${encodeURIComponent(author)}`);
            console.log('Author search results:', result);
            return result;
        } catch (error) {
            console.error('Author search failed:', error);
            throw error;
        }
    },

    // Search book by ISBN
    searchBookByISBN: async function(isbn) {
        console.log('Searching book by ISBN:', isbn);
        try {
            const result = await this.call(`/books/search/isbn/${encodeURIComponent(isbn)}`);
            console.log('ISBN search result:', result);
            return result;
        } catch (error) {
            console.error('ISBN search failed:', error);
            throw error;
        }
    },

    // Advanced search for books
    searchBooks: async function(searchParams = {}) {
        console.log('Advanced book search with params:', searchParams);
        
        const queryParams = new URLSearchParams();
        
        // Add parameters if they exist
        if (searchParams.query) queryParams.append('query', searchParams.query);
        if (searchParams.category_id) queryParams.append('category_id', searchParams.category_id);
        if (searchParams.author) queryParams.append('author', searchParams.author);
        if (searchParams.publication_year) queryParams.append('publication_year', searchParams.publication_year);
        if (searchParams.skip !== undefined) queryParams.append('skip', searchParams.skip);
        if (searchParams.limit !== undefined) queryParams.append('limit', searchParams.limit);
        if (searchParams.sort_by) queryParams.append('sort_by', searchParams.sort_by);
        if (searchParams.sort_desc !== undefined) queryParams.append('sort_desc', searchParams.sort_desc);

        const queryString = queryParams.toString();
        const endpoint = `/books/search/${queryString ? '?' + queryString : ''}`;
        
        try {
            const response = await this.call(endpoint);
            console.log('Advanced search results:', response);
            
            // Handle paginated response
            if (response && response.items) {
                return response; // Return full pagination object for advanced search
            }
            
            return { items: [], total: 0, page: 1, size: 0, pages: 0 };
        } catch (error) {
            console.error('Advanced search failed:', error);
            throw error;
        }
    },

    // =================== USERS API FUNCTIONS ===================

    // Get all users (admin only)
    getUsers: async function(skip = 0, limit = 100) {
        console.log('Fetching users list...');
        try {
            const result = await this.call(`/users/?skip=${skip}&limit=${limit}`);
            console.log('Users list fetched successfully:', result);
            return result;
        } catch (error) {
            console.error('Error fetching users:', error);
            throw error;
        }
    },

    // Get a specific user by ID (admin only)
    getUser: async function(id) {
        console.log(`Fetching user with ID: ${id}`);
        try {
            const result = await this.call(`/users/${id}`);
            console.log('User fetched successfully:', result);
            return result;
        } catch (error) {
            console.error('Error fetching user:', error);
            throw error;
        }
    },

    // Update current user's profile
    updateCurrentUser: async function(userData) {
        console.log('Updating current user profile with data:', userData);
        try {
            const result = await this.call('/users/me', 'PUT', userData);
            console.log('Profile updated successfully:', result);
            // Update the stored user data
            Auth.setUser(result);
            return result;
        } catch (error) {
            console.error('Profile update failed:', error);
            throw error;
        }
    },

    // Update any user by ID (admin only)
    updateUser: async function(id, userData) {
        console.log(`Updating user ${id} with data:`, userData);
        try {
            const result = await this.call(`/users/${id}`, 'PUT', userData);
            console.log('User updated successfully:', result);
            return result;
        } catch (error) {
            console.error('User update failed:', error);
            throw error;
        }
    },

    // Delete a user (admin only)
    deleteUser: async function(id) {
        console.log(`Deleting user ${id}`);
        try {
            const result = await this.call(`/users/${id}`, 'DELETE');
            console.log('User deleted successfully:', result);
            return result;
        } catch (error) {
            console.error('User deletion failed:', error);
            throw error;
        }
    },

    // Get user by email (admin only)
    getUserByEmail: async function(email) {
        console.log('Fetching user by email:', email);
        try {
            const result = await this.call(`/users/by-email/${encodeURIComponent(email)}`);
            console.log('User fetched by email successfully:', result);
            return result;
        } catch (error) {
            console.error('Error fetching user by email:', error);
            throw error;
        }
    },

    // Create a new user (admin only)
    createUser: async function(userData) {
        console.log('Creating new user with data:', userData);
        try {
            const result = await this.call('/users/', 'POST', userData);
            console.log('User created successfully:', result);
            return result;
        } catch (error) {
            console.error('User creation failed:', error);
            throw error;
        }
    },

    // =================== LOANS API FUNCTIONS ===================

    // Get all loans (admin only)
    getLoans: async function(skip = 0, limit = 100) {
        console.log('Fetching loans list...');
        try {
            const result = await this.call(`/loans/?skip=${skip}&limit=${limit}`);
            console.log('Loans list fetched successfully:', result);
            return result;
        } catch (error) {
            console.error('Error fetching loans:', error);
            throw error;
        }
    },

    // Get current user's own loans
    getMyLoans: async function() {
        console.log('Fetching current user loans...');
        try {
            const user = Auth.getUser();
            if (!user || !user.id) {
                throw new Error('User not authenticated');
            }
            const result = await this.call(`/loans/user/${user.id}`);
            console.log('My loans fetched successfully:', result);
            return result;
        } catch (error) {
            console.error('Error fetching my loans:', error);
            throw error;
        }
    },

    // Get current user's active loans
    getMyActiveLoans: async function() {
        console.log('Fetching current user active loans...');
        try {
            const allLoans = await this.getMyLoans();
            const activeLoans = allLoans.filter(loan => !loan.return_date);
            console.log('My active loans:', activeLoans);
            return activeLoans;
        } catch (error) {
            console.error('Error fetching my active loans:', error);
            throw error;
        }
    },

    // Get current user's overdue loans
    getMyOverdueLoans: async function() {
        console.log('Fetching current user overdue loans...');
        try {
            const allLoans = await this.getMyLoans();
            const now = new Date();
            const overdueLoans = allLoans.filter(loan => 
                !loan.return_date && new Date(loan.due_date) < now
            );
            console.log('My overdue loans:', overdueLoans);
            return overdueLoans;
        } catch (error) {
            console.error('Error fetching my overdue loans:', error);
            throw error;
        }
    },

    // Get a specific loan by ID (admin only)
    getLoan: async function(id) {
        console.log(`Fetching loan with ID: ${id}`);
        try {
            const result = await this.call(`/loans/${id}`);
            console.log('Loan fetched successfully:', result);
            return result;
        } catch (error) {
            console.error('Error fetching loan:', error);
            throw error;
        }
    },

    // Create a new loan (admin only)
    createLoan: async function(userId, bookId, loanPeriodDays = 14) {
        console.log('Creating new loan:', { userId, bookId, loanPeriodDays });
        try {
            const queryParams = new URLSearchParams({
                user_id: userId,
                book_id: bookId,
                loan_period_days: loanPeriodDays
            });
            const result = await this.call(`/loans/?${queryParams.toString()}`, 'POST');
            console.log('Loan created successfully:', result);
            return result;
        } catch (error) {
            console.error('Loan creation failed:', error);
            throw error;
        }
    },

    // Return a loan (admin only)
    returnLoan: async function(id) {
        console.log(`Returning loan ${id}`);
        try {
            const result = await this.call(`/loans/${id}/return`, 'POST');
            console.log('Loan returned successfully:', result);
            return result;
        } catch (error) {
            console.error('Loan return failed:', error);
            throw error;
        }
    },

    // Extend a loan (admin only)
    extendLoan: async function(id, days) {
        console.log(`Extending loan ${id} by ${days} days`);
        try {
            const queryParams = new URLSearchParams({
                extension_days: days
            });
            const result = await this.call(`/loans/${id}/extend?${queryParams.toString()}`, 'POST');
            console.log('Loan extended successfully:', result);
            return result;
        } catch (error) {
            console.error('Loan extension failed:', error);
            throw error;
        }
    },

    // Get loans by user ID (admin only)
    getLoansByUser: async function(userId) {
        console.log(`Fetching loans for user: ${userId}`);
        try {
            const result = await this.call(`/loans/user/${userId}`);
            console.log('User loans fetched successfully:', result);
            return result;
        } catch (error) {
            console.error('Error fetching user loans:', error);
            throw error;
        }
    },

    // Get active loans (admin only)
    getActiveLoans: async function() {
        console.log('Fetching active loans...');
        try {
            const result = await this.call('/loans/active/');
            console.log('Active loans fetched successfully:', result);
            return result;
        } catch (error) {
            console.error('Error fetching active loans:', error);
            throw error;
        }
    },

    // Get loans by book ID (admin only)
    getLoansByBook: async function(bookId) {
        console.log(`Fetching loans for book: ${bookId}`);
        try {
            const result = await this.call(`/loans/book/${bookId}`);
            console.log('Book loans fetched successfully:', result);
            return result;
        } catch (error) {
            console.error('Error fetching book loans:', error);
            throw error;
        }
    },

    // Get overdue loans (admin only)
    getOverdueLoans: async function() {
        console.log('Fetching overdue loans...');
        try {
            const result = await this.call('/loans/overdue/');
            console.log('Overdue loans fetched successfully:', result);
            return result;
        } catch (error) {
            console.error('Error fetching overdue loans:', error);
            throw error;
        }
    },

    // Advanced search for loans (admin only)
    searchLoans: async function(searchParams = {}) {
        console.log('Advanced loan search with params:', searchParams);
        
        const queryParams = new URLSearchParams();
        
        // Add parameters if they exist
        if (searchParams.user_id) queryParams.append('user_id', searchParams.user_id);
        if (searchParams.book_id) queryParams.append('book_id', searchParams.book_id);
        if (searchParams.status) queryParams.append('status', searchParams.status);
        if (searchParams.is_overdue !== undefined) queryParams.append('is_overdue', searchParams.is_overdue);
        if (searchParams.skip !== undefined) queryParams.append('skip', searchParams.skip);
        if (searchParams.limit !== undefined) queryParams.append('limit', searchParams.limit);
        if (searchParams.sort_by) queryParams.append('sort_by', searchParams.sort_by);
        if (searchParams.sort_desc !== undefined) queryParams.append('sort_desc', searchParams.sort_desc);

        const queryString = queryParams.toString();
        const endpoint = `/loans/search${queryString ? '?' + queryString : ''}`;
        
        try {
            const response = await this.call(endpoint);
            console.log('Loan search results:', response);
            
            // Handle paginated response if applicable
            if (response && response.items) {
                return response; // Return full pagination object
            }
            
            return Array.isArray(response) ? response : [];
        } catch (error) {
            console.error('Loan search failed:', error);
            throw error;
        }
    },

    // =================== STATISTICS API FUNCTIONS ===================

    // Get general library statistics (admin only)
    getGeneralStats: async function() {
        console.log('Fetching general statistics...');
        try {
            const result = await this.call('/stats/general');
            console.log('General stats fetched successfully:', result);
            return result;
        } catch (error) {
            console.error('Error fetching general stats:', error);
            throw error;
        }
    },

    // Get most borrowed books (admin only)
    getMostBorrowedBooks: async function(limit = 10) {
        console.log(`Fetching top ${limit} most borrowed books...`);
        try {
            const result = await this.call(`/stats/most-borrowed-books?limit=${limit}`);
            console.log('Most borrowed books fetched successfully:', result);
            return result;
        } catch (error) {
            console.error('Error fetching most borrowed books:', error);
            throw error;
        }
    },

    // Get most active users (admin only)
    getMostActiveUsers: async function(limit = 10) {
        console.log(`Fetching top ${limit} most active users...`);
        try {
            const result = await this.call(`/stats/most-active-users?limit=${limit}`);
            console.log('Most active users fetched successfully:', result);
            return result;
        } catch (error) {
            console.error('Error fetching most active users:', error);
            throw error;
        }
    },

    // Get monthly loan statistics (admin only)
    getMonthlyLoans: async function(months = 12) {
        console.log(`Fetching monthly loans for last ${months} months...`);
        try {
            const result = await this.call(`/stats/monthly-loans?months=${months}`);
            console.log('Monthly loans stats fetched successfully:', result);
            return result;
        } catch (error) {
            console.error('Error fetching monthly loans:', error);
            throw error;
        }
    },

    // =================== CATEGORIES API FUNCTIONS ===================

    // Get all categories
    getCategories: async function(skip = 0, limit = 100) {
        console.log('Fetching categories list...');
        try {
            const result = await this.call(`/categories/?skip=${skip}&limit=${limit}`);
            console.log('Categories list fetched successfully:', result);
            return result;
        } catch (error) {
            console.error('Error fetching categories:', error);
            throw error;
        }
    },

    // Get a specific category by ID
    getCategory: async function(id) {
        console.log(`Fetching category with ID: ${id}`);
        try {
            const result = await this.call(`/categories/${id}`);
            console.log('Category fetched successfully:', result);
            return result;
        } catch (error) {
            console.error('Error fetching category:', error);
            throw error;
        }
    },

    // Create a new category (admin only)
    createCategory: async function(categoryData) {
        console.log('Creating category with data:', categoryData);
        try {
            const result = await this.call('/categories/', 'POST', categoryData);
            console.log('Category created successfully:', result);
            return result;
        } catch (error) {
            console.error('Category creation failed:', error);
            throw error;
        }
    },

    // Update an existing category (admin only)
    updateCategory: async function(id, categoryData) {
        console.log(`Updating category ${id} with data:`, categoryData);
        try {
            const result = await this.call(`/categories/${id}`, 'PUT', categoryData);
            console.log('Category updated successfully:', result);
            return result;
        } catch (error) {
            console.error('Category update failed:', error);
            throw error;
        }
    },

    // Delete a category (admin only)
    deleteCategory: async function(id) {
        console.log(`Deleting category ${id}`);
        try {
            const result = await this.call(`/categories/${id}`, 'DELETE');
            console.log('Category deleted successfully:', result);
            return result;
        } catch (error) {
            console.error('Category deletion failed:', error);
            throw error;
        }
    },

    // Get category by name
    getCategoryByName: async function(name) {
        console.log('Fetching category by name:', name);
        try {
            const result = await this.call(`/categories/name/${encodeURIComponent(name)}`);
            console.log('Category fetched by name successfully:', result);
            return result;
        } catch (error) {
            console.error('Error fetching category by name:', error);
            throw error;
        }
    }
};
