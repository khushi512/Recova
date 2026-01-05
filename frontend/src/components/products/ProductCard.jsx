import { motion } from 'framer-motion';
import { Star, ShoppingCart, Check } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useCart } from '../../context/CartContext';

const ProductCard = ({ product, showScore = false }) => {
    const navigate = useNavigate();
    const { isInCart, toggleCart } = useCart();

    const productId = product.product_id || product.id;
    const inCart = isInCart(productId);

    const handleClick = () => {
        navigate(`/product/${productId}`);
    };

    const handleCartClick = async (e) => {
        e.stopPropagation(); // Prevent card click
        await toggleCart(product);
    };

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
            whileHover={{ y: -8, scale: 1.02 }}
            className="card card-hover cursor-pointer overflow-hidden group"
            onClick={handleClick}
        >
            {/* Image Container */}
            <div className="relative overflow-hidden bg-gradient-to-br from-gray-100 to-gray-200 aspect-square">
                <img
                    src={product.image_url}
                    alt={product.title}
                    className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
                    loading="lazy"
                />

                {/* Similarity Score Badge (if shown) */}
                {showScore && product.similarity_score && (
                    <div className="absolute top-3 right-3 bg-gradient-to-r from-purple-500 to-pink-500 text-white px-3 py-1 rounded-full text-sm font-semibold shadow-lg">
                        {Math.round(product.similarity_score * 100)}% Match
                    </div>
                )}

                {/* Category Badge */}
                <div className="absolute bottom-3 left-3 bg-white/90 backdrop-blur-sm px-3 py-1 rounded-full text-xs font-medium text-gray-700">
                    {product.category}
                </div>

                {/* In Cart Badge */}
                {inCart && (
                    <div className="absolute top-3 left-3 bg-green-500 text-white px-2 py-1 rounded-full text-xs font-medium flex items-center gap-1">
                        <Check className="w-3 h-3" />
                        In Cart
                    </div>
                )}
            </div>

            {/* Content */}
            <div className="p-5">
                {/* Title */}
                <h3 className="font-semibold text-gray-900 mb-2 line-clamp-2 group-hover:text-orange-500 transition-colors">
                    {product.title}
                </h3>

                {/* Rating */}
                {product.rating && (
                    <div className="flex items-center gap-1 mb-3">
                        <Star className="w-4 h-4 fill-yellow-400 text-yellow-400" />
                        <span className="text-sm font-medium text-gray-700">{product.rating.toFixed(1)}</span>
                        <span className="text-xs text-gray-500 ml-1">({product.review_count || 0})</span>
                    </div>
                )}

                {/* Price & Action */}
                <div className="flex items-center justify-between">
                    <div>
                        <span className="text-2xl font-bold text-gray-900">
                            ${product.price?.toFixed(2)}
                        </span>
                    </div>

                    <motion.button
                        whileHover={{ scale: 1.1 }}
                        whileTap={{ scale: 0.95 }}
                        className={`p-3 rounded-full shadow-lg hover:shadow-xl transition-all ${inCart
                            ? 'bg-green-500'
                            : 'bg-gradient-to-r from-orange-500 to-orange-600'
                            }`}
                        onClick={handleCartClick}
                    >
                        {inCart ? (
                            <Check className="w-5 h-5 text-white" />
                        ) : (
                            <ShoppingCart className="w-5 h-5 text-white" />
                        )}
                    </motion.button>
                </div>
            </div>
        </motion.div>
    );
};

export default ProductCard;