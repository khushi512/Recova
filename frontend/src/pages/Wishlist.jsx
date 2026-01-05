import { motion } from 'framer-motion';
import { Heart, Trash2, ArrowLeft, ShoppingCart } from 'lucide-react';
import { Link } from 'react-router-dom';
import { useCart } from '../context/CartContext';

const Wishlist = () => {
    const { wishlistItems, wishlistCount, removeFromWishlist, addToCart, isInCart } = useCart();

    const handleMoveToCart = (item) => {
        addToCart(item);
        removeFromWishlist(item.product_id);
    };

    if (wishlistCount === 0) {
        return (
            <div className="min-h-screen py-16">
                <div className="max-w-4xl mx-auto px-4 text-center">
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                    >
                        <div className="w-24 h-24 bg-pink-100 rounded-full flex items-center justify-center mx-auto mb-6">
                            <Heart className="w-12 h-12 text-pink-400" />
                        </div>
                        <h1 className="text-3xl font-bold text-gray-900 mb-4">Your Wishlist is Empty</h1>
                        <p className="text-gray-600 mb-8">Save items you love by clicking the heart icon on products.</p>
                        <Link to="/">
                            <motion.button
                                whileHover={{ scale: 1.05 }}
                                whileTap={{ scale: 0.95 }}
                                className="btn-primary inline-flex items-center gap-2"
                            >
                                <ArrowLeft className="w-5 h-5" />
                                Start Shopping
                            </motion.button>
                        </Link>
                    </motion.div>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen py-8">
            <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
                {/* Header */}
                <motion.div
                    initial={{ opacity: 0, y: -20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="flex items-center gap-4 mb-8"
                >
                    <div className="w-12 h-12 bg-gradient-to-r from-orange-500 to-orange-600 rounded-lg flex items-center justify-center">
                        <Heart className="w-6 h-6 text-white" />
                    </div>
                    <div>
                        <h1 className="text-3xl font-bold text-gray-900">My Wishlist</h1>
                        <p className="text-gray-600">{wishlistCount} item{wishlistCount !== 1 ? 's' : ''} saved</p>
                    </div>
                </motion.div>

                {/* Wishlist Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {wishlistItems.map((item, index) => (
                        <motion.div
                            key={`${item.product_id}-${index}`}
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: index * 0.05 }}
                            className="glass rounded-xl overflow-hidden group"
                        >
                            {/* Product Image */}
                            <Link to={`/product/${item.product_id}`}>
                                <div className="relative h-48 overflow-hidden">
                                    <img
                                        src={item.image_url || `https://picsum.photos/seed/${item.product_id}/400/300`}
                                        alt={item.title}
                                        className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-300"
                                    />
                                    <div className="absolute top-3 right-3">
                                        <span className="bg-pink-500 text-white text-xs px-2 py-1 rounded-full">
                                            ♥ Saved
                                        </span>
                                    </div>
                                </div>
                            </Link>

                            {/* Product Details */}
                            <div className="p-4">
                                <Link to={`/product/${item.product_id}`}>
                                    <h3 className="font-semibold text-gray-900 hover:text-pink-600 transition-colors line-clamp-2 mb-2">
                                        {item.title}
                                    </h3>
                                </Link>

                                {item.category && (
                                    <p className="text-sm text-gray-500 mb-2">{item.category}</p>
                                )}

                                <p className="text-2xl font-bold text-gray-900 mb-4">
                                    ${item.price?.toFixed(2)}
                                </p>

                                {/* Action Buttons */}
                                <div className="flex gap-2">
                                    {isInCart(item.product_id) ? (
                                        <Link to="/cart" className="flex-1">
                                            <motion.button
                                                whileHover={{ scale: 1.02 }}
                                                whileTap={{ scale: 0.98 }}
                                                className="w-full py-2 bg-green-500 text-white rounded-lg font-medium flex items-center justify-center gap-2"
                                            >
                                                <ShoppingCart className="w-4 h-4" />
                                                View in Cart
                                            </motion.button>
                                        </Link>
                                    ) : (
                                        <motion.button
                                            whileHover={{ scale: 1.02 }}
                                            whileTap={{ scale: 0.98 }}
                                            onClick={() => handleMoveToCart(item)}
                                            className="flex-1 py-2 bg-gradient-to-r from-blue-500 to-indigo-600 text-white rounded-lg font-medium flex items-center justify-center gap-2"
                                        >
                                            <ShoppingCart className="w-4 h-4" />
                                            Move to Cart
                                        </motion.button>
                                    )}

                                    <motion.button
                                        whileHover={{ scale: 1.1 }}
                                        whileTap={{ scale: 0.9 }}
                                        onClick={() => removeFromWishlist(item.product_id)}
                                        className="p-2 text-red-500 hover:bg-red-50 rounded-lg transition-colors"
                                        title="Remove from wishlist"
                                    >
                                        <Trash2 className="w-5 h-5" />
                                    </motion.button>
                                </div>
                            </div>
                        </motion.div>
                    ))}
                </div>

                {/* Continue Shopping */}
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.3 }}
                    className="mt-8 text-center"
                >
                    <Link to="/">
                        <motion.button
                            whileHover={{ scale: 1.02 }}
                            whileTap={{ scale: 0.98 }}
                            className="inline-flex items-center gap-2 px-6 py-3 border-2 border-gray-300 text-gray-700 rounded-lg font-medium hover:border-pink-500 hover:text-pink-600 transition-colors"
                        >
                            <ArrowLeft className="w-5 h-5" />
                            Continue Shopping
                        </motion.button>
                    </Link>
                </motion.div>
            </div>
        </div>
    );
};

export default Wishlist;
