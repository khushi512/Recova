import { motion } from 'framer-motion';
import { ShoppingBag, Search, User, Menu, ShoppingCart, Heart } from 'lucide-react';
import { Link } from 'react-router-dom';
import { useState } from 'react';
import { useUser } from '../../context/UserContext';
import { useCart } from '../../context/CartContext';

const Navbar = () => {
    const [searchQuery, setSearchQuery] = useState('');
    const { userId } = useUser();
    const { cartCount, wishlistCount } = useCart();

    return (
        <motion.nav
            initial={{ y: -100 }}
            animate={{ y: 0 }}
            className="glass sticky top-0 z-50 border-b border-white/20"
        >
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex items-center justify-between h-16">
                    {/* Logo */}
                    <Link to="/" className="flex items-center space-x-2">
                        <motion.div
                            whileHover={{ rotate: 360 }}
                            transition={{ duration: 0.5 }}
                            className="bg-gradient-to-r from-blue-500 to-indigo-600 p-2 rounded-lg"
                        >
                            <ShoppingBag className="w-6 h-6 text-white" />
                        </motion.div>
                        <span className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
                            Recova
                        </span>
                    </Link>

                    {/* Search Bar */}
                    <div className="hidden md:flex flex-1 max-w-md mx-8">
                        <div className="relative w-full">
                            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                            <input
                                type="text"
                                placeholder="Search products..."
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                                className="w-full pl-10 pr-4 py-2 bg-white border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                            />
                        </div>
                    </div>

                    {/* Right Menu */}
                    <div className="flex items-center space-x-4">
                        {/* Current User Badge */}
                        <div className="hidden md:flex items-center gap-2 px-3 py-1 bg-blue-50 rounded-full">
                            <User className="w-4 h-4 text-blue-600" />
                            <span className="text-sm font-medium text-blue-600">User {userId}</span>
                        </div>

                        {/* Wishlist Button with Count */}
                        <Link to="/wishlist">
                            <motion.div
                                whileHover={{ scale: 1.1 }}
                                whileTap={{ scale: 0.95 }}
                                className="relative p-2 rounded-lg hover:bg-white/50 transition-colors cursor-pointer"
                            >
                                <Heart className="w-6 h-6 text-gray-700" />
                                {wishlistCount > 0 && (
                                    <motion.span
                                        initial={{ scale: 0 }}
                                        animate={{ scale: 1 }}
                                        className="absolute -top-1 -right-1 bg-gradient-to-r from-pink-500 to-rose-500 text-white text-xs font-bold w-5 h-5 rounded-full flex items-center justify-center"
                                    >
                                        {wishlistCount > 9 ? '9+' : wishlistCount}
                                    </motion.span>
                                )}
                            </motion.div>
                        </Link>

                        {/* Cart Button with Count */}
                        <Link to="/cart">
                            <motion.div
                                whileHover={{ scale: 1.1 }}
                                whileTap={{ scale: 0.95 }}
                                className="relative p-2 rounded-lg hover:bg-white/50 transition-colors cursor-pointer"
                            >
                                <ShoppingCart className="w-6 h-6 text-gray-700" />
                                {cartCount > 0 && (
                                    <motion.span
                                        initial={{ scale: 0 }}
                                        animate={{ scale: 1 }}
                                        className="absolute -top-1 -right-1 bg-gradient-to-r from-red-500 to-pink-500 text-white text-xs font-bold w-5 h-5 rounded-full flex items-center justify-center"
                                    >
                                        {cartCount > 9 ? '9+' : cartCount}
                                    </motion.span>
                                )}
                            </motion.div>
                        </Link>

                        {/* User Account */}
                        <Link to="/profile">
                            <motion.button
                                whileHover={{ scale: 1.1 }}
                                whileTap={{ scale: 0.95 }}
                                className="p-2 rounded-lg hover:bg-white/50 transition-colors"
                            >
                                <User className="w-6 h-6 text-gray-700" />
                            </motion.button>
                        </Link>

                        {/* Mobile Menu */}
                        <motion.button
                            whileHover={{ scale: 1.1 }}
                            whileTap={{ scale: 0.95 }}
                            className="md:hidden p-2 rounded-lg hover:bg-white/50 transition-colors"
                        >
                            <Menu className="w-6 h-6 text-gray-700" />
                        </motion.button>
                    </div>
                </div>
            </div>
        </motion.nav>
    );
};

export default Navbar;