import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Star, ShoppingCart, Heart, Share2, TrendingUp, Check, ArrowLeft } from 'lucide-react';
import { useUser } from '../context/UserContext';
import { useCart } from '../context/CartContext';
import ProductCard from '../components/products/ProductCard';
import { SkeletonCard, SkeletonProductImage, SkeletonProductInfo } from '../components/common/SkeletonCard';
import { productsAPI, recommendationsAPI, interactionsAPI } from '../api/client';

const ProductDetail = () => {
    const { productId } = useParams();
    const { userId } = useUser();
    const { isInCart, toggleCart, isInWishlist, toggleWishlist } = useCart();
    const [product, setProduct] = useState(null);
    const [similarProducts, setSimilarProducts] = useState([]);
    const [productLoading, setProductLoading] = useState(true);
    const [similarLoading, setSimilarLoading] = useState(true);
    const [userRating, setUserRating] = useState(0);
    const [hoverRating, setHoverRating] = useState(0);
    const [ratingSubmitted, setRatingSubmitted] = useState(false);

    const inCart = product ? isInCart(product.id) : false;
    const inWishlist = product ? isInWishlist(product.id) : false;

    useEffect(() => {
        loadProductData();
        trackView();
    }, [productId]);

    const loadProductData = async () => {
        setProductLoading(true);
        setSimilarLoading(true);

        // Load product
        productsAPI.getById(productId)
            .then(res => setProduct(res.data))
            .catch(err => console.error('Error loading product:', err))
            .finally(() => setProductLoading(false));

        // Load similar products (non-blocking)
        recommendationsAPI.getSimilar(productId, 8)
            .then(res => setSimilarProducts(res.data.recommendations))
            .catch(err => console.error('Error loading similar:', err))
            .finally(() => setSimilarLoading(false));
    };

    const trackView = async () => {
        try {
            await interactionsAPI.track({
                user_id: userId,
                product_id: parseInt(productId),
                interaction_type: 'view'
            });
        } catch (error) {
            console.error('Error tracking view:', error);
        }
    };

    const handleAddToCart = async () => {
        if (product) {
            await toggleCart({ ...product, product_id: product.id });
        }
    };

    const handleToggleLike = async () => {
        if (product) {
            await toggleWishlist({ ...product, product_id: product.id });
        }
    };

    const handleRating = async (rating) => {
        setUserRating(rating);
        try {
            await interactionsAPI.track({
                user_id: userId,
                product_id: parseInt(productId),
                interaction_type: 'rating',
                rating: rating
            });
            setRatingSubmitted(true);
            setTimeout(() => setRatingSubmitted(false), 3000);
        } catch (error) {
            console.error('Error submitting rating:', error);
        }
    };

    // Show skeleton layout while loading - page structure is immediately visible
    return (
        <div className="min-h-screen py-8">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                {/* Back Button - Always visible */}
                <Link to="/">
                    <motion.button
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        whileHover={{ scale: 1.05 }}
                        className="flex items-center gap-2 text-gray-600 hover:text-blue-600 mb-6 transition-colors"
                    >
                        <ArrowLeft className="w-5 h-5" />
                        Back to Products
                    </motion.button>
                </Link>

                {/* Product Details */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 mb-16">
                    {/* Image */}
                    {productLoading ? (
                        <SkeletonProductImage />
                    ) : product ? (
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            className="relative"
                        >
                            <div className="card overflow-hidden aspect-square bg-gradient-to-br from-gray-100 to-gray-200">
                                <img
                                    src={`https://picsum.photos/seed/${product.id}/800/800`}
                                    alt={product.title}
                                    className="w-full h-full object-cover"
                                />
                                {inCart && (
                                    <div className="absolute top-4 left-4 bg-green-500 text-white px-3 py-1 rounded-full text-sm font-medium flex items-center gap-1">
                                        <Check className="w-4 h-4" />
                                        In Cart
                                    </div>
                                )}
                            </div>
                        </motion.div>
                    ) : (
                        <div className="card overflow-hidden aspect-square bg-gray-100 flex items-center justify-center">
                            <p className="text-gray-500">Product not found</p>
                        </div>
                    )}

                    {/* Details */}
                    {productLoading ? (
                        <SkeletonProductInfo />
                    ) : product ? (
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            className="flex flex-col"
                        >
                            <span className="inline-block w-fit bg-blue-100 text-blue-700 px-4 py-1 rounded-full text-sm font-medium mb-4">
                                {product.category}
                            </span>

                            <h1 className="text-4xl font-bold text-gray-900 mb-4">
                                {product.title}
                            </h1>

                            {/* Product Rating */}
                            <div className="flex items-center gap-4 mb-6">
                                <div className="flex items-center gap-1">
                                    {[...Array(5)].map((_, i) => (
                                        <Star
                                            key={i}
                                            className={`w-5 h-5 ${i < Math.floor(product.rating)
                                                ? 'fill-yellow-400 text-yellow-400'
                                                : 'text-gray-300'
                                                }`}
                                        />
                                    ))}
                                </div>
                                <span className="text-lg font-semibold text-gray-700">
                                    {product.rating?.toFixed(1)}
                                </span>
                                <span className="text-gray-500">
                                    ({product.review_count || 0} reviews)
                                </span>
                            </div>

                            {/* Price */}
                            <div className="mb-6">
                                <span className="text-5xl font-bold bg-gradient-to-r from-slate-700 to-slate-900 bg-clip-text text-transparent">
                                    ${product.price.toFixed(2)}
                                </span>
                            </div>

                            {/* User Rating Section */}
                            <div className="mb-8 p-4 bg-gradient-to-r from-yellow-50 to-orange-50 rounded-xl border border-yellow-200">
                                <h3 className="text-lg font-semibold text-gray-900 mb-3">
                                    Rate this Product
                                </h3>
                                <div className="flex items-center gap-4">
                                    <div className="flex items-center gap-1">
                                        {[1, 2, 3, 4, 5].map((star) => (
                                            <motion.button
                                                key={star}
                                                whileHover={{ scale: 1.2 }}
                                                whileTap={{ scale: 0.9 }}
                                                onMouseEnter={() => setHoverRating(star)}
                                                onMouseLeave={() => setHoverRating(0)}
                                                onClick={() => handleRating(star)}
                                                className="focus:outline-none"
                                            >
                                                <Star
                                                    className={`w-8 h-8 transition-colors ${star <= (hoverRating || userRating)
                                                        ? 'fill-yellow-400 text-yellow-400'
                                                        : 'text-gray-300 hover:text-yellow-300'
                                                        }`}
                                                />
                                            </motion.button>
                                        ))}
                                    </div>
                                    {userRating > 0 && (
                                        <span className="text-sm font-medium text-yellow-700">
                                            You rated: {userRating} star{userRating > 1 ? 's' : ''}
                                        </span>
                                    )}
                                    {ratingSubmitted && (
                                        <motion.span
                                            initial={{ opacity: 0, x: -10 }}
                                            animate={{ opacity: 1, x: 0 }}
                                            className="text-sm font-medium text-green-600"
                                        >
                                            ✓ Rating saved!
                                        </motion.span>
                                    )}
                                </div>
                            </div>

                            {/* Description */}
                            <div className="mb-8">
                                <h3 className="text-lg font-semibold text-gray-900 mb-2">Description</h3>
                                <p className="text-gray-600 leading-relaxed">{product.description}</p>
                            </div>

                            {/* Actions */}
                            <div className="flex flex-wrap gap-4 mt-auto">
                                <motion.button
                                    whileHover={{ scale: 1.05 }}
                                    whileTap={{ scale: 0.95 }}
                                    onClick={handleAddToCart}
                                    className={`flex-1 flex items-center justify-center gap-2 text-lg py-4 rounded-lg font-semibold transition-all ${inCart
                                        ? 'bg-green-500 text-white'
                                        : 'btn-primary'
                                        }`}
                                >
                                    {inCart ? (
                                        <>
                                            <Check className="w-5 h-5" />
                                            In Cart (Click to Remove)
                                        </>
                                    ) : (
                                        <>
                                            <ShoppingCart className="w-5 h-5" />
                                            Add to Cart
                                        </>
                                    )}
                                </motion.button>

                                <motion.button
                                    whileHover={{ scale: 1.05 }}
                                    whileTap={{ scale: 0.95 }}
                                    onClick={handleToggleLike}
                                    className={`p-4 rounded-lg border-2 transition-all ${inWishlist
                                        ? 'bg-red-50 border-red-500 text-red-500'
                                        : 'border-gray-300 text-gray-600 hover:border-red-500'
                                        }`}
                                >
                                    <Heart className={`w-6 h-6 ${inWishlist ? 'fill-red-500' : ''}`} />
                                </motion.button>

                                <motion.button
                                    whileHover={{ scale: 1.05 }}
                                    whileTap={{ scale: 0.95 }}
                                    className="p-4 rounded-lg border-2 border-gray-300 text-gray-600 hover:border-blue-500 transition-all"
                                >
                                    <Share2 className="w-6 h-6" />
                                </motion.button>
                            </div>
                        </motion.div>
                    ) : (
                        <div className="flex items-center justify-center">
                            <div className="text-center">
                                <h2 className="text-2xl font-bold text-gray-900 mb-2">Product Not Found</h2>
                                <p className="text-gray-600">The product you're looking for doesn't exist.</p>
                            </div>
                        </div>
                    )}
                </div>

                {/* Similar Products */}
                <section className="mt-16">
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        className="flex items-center gap-3 mb-8"
                    >
                        <TrendingUp className="w-8 h-8 text-orange-500" />
                        <h2 className="text-3xl font-bold text-gray-900">You Might Also Like</h2>
                    </motion.div>

                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
                        {similarLoading ? (
                            [...Array(4)].map((_, i) => <SkeletonCard key={i} />)
                        ) : similarProducts.length > 0 ? (
                            similarProducts.map((prod, index) => (
                                <motion.div
                                    key={prod.product_id}
                                    initial={{ opacity: 0, y: 20 }}
                                    whileInView={{ opacity: 1, y: 0 }}
                                    viewport={{ once: true }}
                                    transition={{ delay: index * 0.05 }}
                                >
                                    <ProductCard product={prod} showScore={true} />
                                </motion.div>
                            ))
                        ) : (
                            <p className="text-gray-500 col-span-4">No similar products found.</p>
                        )}
                    </div>
                </section>
            </div>
        </div>
    );
};

export default ProductDetail;