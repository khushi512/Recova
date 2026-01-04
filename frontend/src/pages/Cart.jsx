import { motion } from 'framer-motion';
import { ShoppingCart, Trash2, ArrowLeft, CreditCard } from 'lucide-react';
import { Link } from 'react-router-dom';
import { useCart } from '../context/CartContext';

const Cart = () => {
    const { cartItems, cartTotal, removeFromCart, cartCount } = useCart();

    if (cartCount === 0) {
        return (
            <div className="min-h-screen py-16">
                <div className="max-w-4xl mx-auto px-4 text-center">
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                    >
                        <div className="w-24 h-24 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-6">
                            <ShoppingCart className="w-12 h-12 text-gray-400" />
                        </div>
                        <h1 className="text-3xl font-bold text-gray-900 mb-4">Your Cart is Empty</h1>
                        <p className="text-gray-600 mb-8">Looks like you haven't added any items yet.</p>
                        <Link to="/">
                            <motion.button
                                whileHover={{ scale: 1.05 }}
                                whileTap={{ scale: 0.95 }}
                                className="btn-primary inline-flex items-center gap-2"
                            >
                                <ArrowLeft className="w-5 h-5" />
                                Continue Shopping
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
                    <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-lg flex items-center justify-center">
                        <ShoppingCart className="w-6 h-6 text-white" />
                    </div>
                    <div>
                        <h1 className="text-3xl font-bold text-gray-900">Shopping Cart</h1>
                        <p className="text-gray-600">{cartCount} item{cartCount !== 1 ? 's' : ''} in your cart</p>
                    </div>
                </motion.div>

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                    {/* Cart Items */}
                    <div className="lg:col-span-2 space-y-4">
                        {cartItems.map((item, index) => (
                            <motion.div
                                key={`${item.product_id}-${index}`}
                                initial={{ opacity: 0, x: -20 }}
                                animate={{ opacity: 1, x: 0 }}
                                transition={{ delay: index * 0.05 }}
                                className="glass rounded-xl p-4 flex gap-4"
                            >
                                {/* Product Image */}
                                <Link to={`/product/${item.product_id}`}>
                                    <img
                                        src={item.image_url || `https://picsum.photos/seed/${item.product_id}/200/200`}
                                        alt={item.title}
                                        className="w-24 h-24 object-cover rounded-lg"
                                    />
                                </Link>

                                {/* Product Details */}
                                <div className="flex-1">
                                    <Link to={`/product/${item.product_id}`}>
                                        <h3 className="font-semibold text-gray-900 hover:text-blue-600 transition-colors">
                                            {item.title}
                                        </h3>
                                    </Link>
                                    <p className="text-2xl font-bold text-gray-900 mt-2">
                                        ${item.price?.toFixed(2)}
                                    </p>
                                </div>

                                {/* Remove Button */}
                                <motion.button
                                    whileHover={{ scale: 1.1 }}
                                    whileTap={{ scale: 0.9 }}
                                    onClick={() => removeFromCart(item.product_id)}
                                    className="p-2 text-red-500 hover:bg-red-50 rounded-lg transition-colors self-start"
                                >
                                    <Trash2 className="w-5 h-5" />
                                </motion.button>
                            </motion.div>
                        ))}
                    </div>

                    {/* Order Summary */}
                    <div className="lg:col-span-1">
                        <motion.div
                            initial={{ opacity: 0, x: 20 }}
                            animate={{ opacity: 1, x: 0 }}
                            className="glass rounded-xl p-6 sticky top-24"
                        >
                            <h2 className="text-xl font-bold text-gray-900 mb-6">Order Summary</h2>

                            <div className="space-y-3 mb-6">
                                <div className="flex justify-between text-gray-600">
                                    <span>Subtotal ({cartCount} items)</span>
                                    <span>${cartTotal.toFixed(2)}</span>
                                </div>
                                <div className="flex justify-between text-gray-600">
                                    <span>Shipping</span>
                                    <span className="text-green-600">Free</span>
                                </div>
                                <div className="flex justify-between text-gray-600">
                                    <span>Tax</span>
                                    <span>${(cartTotal * 0.08).toFixed(2)}</span>
                                </div>
                                <div className="border-t border-gray-200 pt-3">
                                    <div className="flex justify-between text-xl font-bold text-gray-900">
                                        <span>Total</span>
                                        <span>${(cartTotal * 1.08).toFixed(2)}</span>
                                    </div>
                                </div>
                            </div>

                            <motion.button
                                whileHover={{ scale: 1.02 }}
                                whileTap={{ scale: 0.98 }}
                                className="w-full btn-primary flex items-center justify-center gap-2 py-4"
                            >
                                <CreditCard className="w-5 h-5" />
                                Proceed to Checkout
                            </motion.button>

                            <Link to="/">
                                <motion.button
                                    whileHover={{ scale: 1.02 }}
                                    whileTap={{ scale: 0.98 }}
                                    className="w-full mt-3 py-3 border-2 border-gray-300 text-gray-700 rounded-lg font-medium hover:border-blue-500 transition-colors flex items-center justify-center gap-2"
                                >
                                    <ArrowLeft className="w-5 h-5" />
                                    Continue Shopping
                                </motion.button>
                            </Link>
                        </motion.div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Cart;
