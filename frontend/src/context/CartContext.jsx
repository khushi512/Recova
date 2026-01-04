import { createContext, useContext, useState, useEffect } from 'react';
import { useUser } from './UserContext';
import { interactionsAPI } from '../api/client';

const CartContext = createContext();

export const useCart = () => {
    const context = useContext(CartContext);
    if (!context) {
        throw new Error('useCart must be used within a CartProvider');
    }
    return context;
};

// Helper to get storage key per user
const getStorageKey = (userId, type) => `shopsmart_${type}_user_${userId}`;

export const CartProvider = ({ children }) => {
    const { userId } = useUser();
    const [cartItems, setCartItems] = useState([]);
    const [wishlistItems, setWishlistItems] = useState([]);
    const [loading, setLoading] = useState(true);

    // Load from localStorage when userId changes
    useEffect(() => {
        loadFromStorage();
    }, [userId]);

    // Save to localStorage whenever cart/wishlist changes
    useEffect(() => {
        if (!loading) {
            localStorage.setItem(getStorageKey(userId, 'cart'), JSON.stringify(cartItems));
        }
    }, [cartItems, userId, loading]);

    useEffect(() => {
        if (!loading) {
            localStorage.setItem(getStorageKey(userId, 'wishlist'), JSON.stringify(wishlistItems));
        }
    }, [wishlistItems, userId, loading]);

    const loadFromStorage = () => {
        setLoading(true);
        try {
            const storedCart = localStorage.getItem(getStorageKey(userId, 'cart'));
            const storedWishlist = localStorage.getItem(getStorageKey(userId, 'wishlist'));

            setCartItems(storedCart ? JSON.parse(storedCart) : []);
            setWishlistItems(storedWishlist ? JSON.parse(storedWishlist) : []);
        } catch (error) {
            console.error('Error loading from storage:', error);
            setCartItems([]);
            setWishlistItems([]);
        }
        setLoading(false);
    };

    // ========== CART FUNCTIONS ==========

    const isInCart = (productId) => {
        return cartItems.some(item => item.product_id === productId);
    };

    const addToCart = async (product) => {
        const productId = product.product_id || product.id;

        // Don't add duplicates
        if (isInCart(productId)) return false;

        try {
            // Track as purchase interaction
            await interactionsAPI.track({
                user_id: userId,
                product_id: productId,
                interaction_type: 'purchase'
            });

            // Add to local cart state
            setCartItems(prev => [...prev, {
                product_id: productId,
                title: product.title,
                price: product.price,
                image_url: product.image_url || `https://picsum.photos/seed/${productId}/400/400`
            }]);

            return true;
        } catch (error) {
            console.error('Error adding to cart:', error);
            return false;
        }
    };

    const removeFromCart = (productId) => {
        setCartItems(prev => prev.filter(item => item.product_id !== productId));
    };

    const toggleCart = async (product) => {
        const productId = product.product_id || product.id;

        if (isInCart(productId)) {
            removeFromCart(productId);
            return false; // removed
        } else {
            await addToCart(product);
            return true; // added
        }
    };

    const cartCount = cartItems.length;
    const cartTotal = cartItems.reduce((sum, item) => sum + (item.price || 0), 0);

    // ========== WISHLIST FUNCTIONS ==========

    const isInWishlist = (productId) => {
        return wishlistItems.some(item => item.product_id === productId);
    };

    const addToWishlist = async (product) => {
        const productId = product.product_id || product.id;

        // Don't add duplicates
        if (isInWishlist(productId)) return false;

        try {
            // Track as wishlist interaction
            await interactionsAPI.track({
                user_id: userId,
                product_id: productId,
                interaction_type: 'wishlist'
            });

            // Add to local wishlist state
            setWishlistItems(prev => [...prev, {
                product_id: productId,
                title: product.title,
                price: product.price,
                image_url: product.image_url || `https://picsum.photos/seed/${productId}/400/400`
            }]);

            return true;
        } catch (error) {
            console.error('Error adding to wishlist:', error);
            return false;
        }
    };

    const removeFromWishlist = (productId) => {
        setWishlistItems(prev => prev.filter(item => item.product_id !== productId));
    };

    const toggleWishlist = async (product) => {
        const productId = product.product_id || product.id;

        if (isInWishlist(productId)) {
            removeFromWishlist(productId);
            return false; // removed
        } else {
            await addToWishlist(product);
            return true; // added
        }
    };

    const wishlistCount = wishlistItems.length;

    // ========== CLEAR ALL ==========

    const clearCart = () => {
        setCartItems([]);
    };

    const clearWishlist = () => {
        setWishlistItems([]);
    };

    return (
        <CartContext.Provider value={{
            // Cart
            cartItems,
            cartCount,
            cartTotal,
            isInCart,
            addToCart,
            removeFromCart,
            toggleCart,
            clearCart,
            // Wishlist
            wishlistItems,
            wishlistCount,
            isInWishlist,
            addToWishlist,
            removeFromWishlist,
            toggleWishlist,
            clearWishlist,
            // State
            loading
        }}>
            {children}
        </CartContext.Provider>
    );
};

export default CartContext;
