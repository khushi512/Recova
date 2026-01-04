import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const apiClient = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Recommendations API
export const recommendationsAPI = {
    getSimilar: (productId, limit = 10) =>
        apiClient.get(`/api/recommendations/similar/${productId}`, { params: { limit } }),

    getForUser: (userId, limit = 10) =>
        apiClient.get(`/api/recommendations/for-user/${userId}`, { params: { limit } }),

    getPopular: (limit = 10) =>
        apiClient.get('/api/recommendations/popular', { params: { limit } }),

    getMetrics: () =>
        apiClient.get('/api/recommendations/metrics'),
};

// Products API
export const productsAPI = {
    getAll: (params = {}) =>
        apiClient.get('/api/products', { params }),

    getById: (productId) =>
        apiClient.get(`/api/products/${productId}`),

    getCategories: () =>
        apiClient.get('/api/products/categories/list'),
};

// Interactions API
export const interactionsAPI = {
    track: (interaction) =>
        apiClient.post('/api/interactions', interaction),

    getUserHistory: (userId, limit = 50) =>
        apiClient.get(`/api/interactions/user/${userId}`, { params: { limit } }),
};

export default apiClient;
