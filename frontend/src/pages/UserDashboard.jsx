import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { User, Heart, ShoppingBag, TrendingUp, Sparkles, ArrowRight, ShoppingCart, Star } from 'lucide-react';
import { Link } from 'react-router-dom';
import { useUser } from '../context/UserContext';
import { useCart } from '../context/CartContext';
import ProductCard from '../components/products/ProductCard';
import { SkeletonCard, SkeletonStat } from '../components/common/SkeletonCard';
import { recommendationsAPI, interactionsAPI } from '../api/client';

const UserDashboard = () => {
  const { userId, setUserId } = useUser();
  const { cartCount, wishlistCount } = useCart();
  const [recommendations, setRecommendations] = useState([]);
  const [history, setHistory] = useState([]);
  const [algorithm, setAlgorithm] = useState('hybrid');
  const [statsLoading, setStatsLoading] = useState(true);
  const [recsLoading, setRecsLoading] = useState(true);
  const [recsPage, setRecsPage] = useState(1);
  const recsPerPage = 20;

  // Calculate stats from history
  const totalSpent = history
    .filter(h => h.interaction_type === 'purchase')
    .reduce((sum, h) => sum + h.product_price, 0);

  const viewsCount = history.filter(h => h.interaction_type === 'view').length;
  const purchasesCount = history.filter(h => h.interaction_type === 'purchase').length;
  const ratingsCount = history.filter(h => h.interaction_type === 'rating').length;

  useEffect(() => {
    loadInitialData();
  }, [userId]);

  useEffect(() => {
    loadRecommendations();
    setRecsPage(1);
  }, [algorithm]);

  const loadInitialData = async () => {
    try {
      setStatsLoading(true);
      const historyRes = await interactionsAPI.getUserHistory(userId, 200);
      setHistory(historyRes.data.interactions);
    } catch (error) {
      console.error('Error loading dashboard:', error);
    } finally {
      setStatsLoading(false);
    }

    // Load recommendations separately (non-blocking)
    loadRecommendations();
  };

  const loadRecommendations = async () => {
    try {
      setRecsLoading(true);
      let recsRes;
      if (algorithm === 'popular') {
        recsRes = await recommendationsAPI.getPopular(50);
      } else {
        recsRes = await recommendationsAPI.getForUser(userId, 50, algorithm);
      }
      setRecommendations(recsRes.data.recommendations);
    } catch (error) {
      console.error('Error loading recommendations:', error);
    } finally {
      setRecsLoading(false);
    }
  };

  // Pagination
  const totalRecsPages = Math.ceil(recommendations.length / recsPerPage);
  const recsStartIndex = (recsPage - 1) * recsPerPage;
  const currentRecs = recommendations.slice(recsStartIndex, recsStartIndex + recsPerPage);

  const getRecsPageNumbers = () => {
    const pages = [];
    const maxVisible = 5;
    if (totalRecsPages <= maxVisible) {
      for (let i = 1; i <= totalRecsPages; i++) pages.push(i);
    } else if (recsPage <= 2) {
      for (let i = 1; i <= 3; i++) pages.push(i);
      pages.push('...', totalRecsPages);
    } else if (recsPage >= totalRecsPages - 1) {
      pages.push(1, '...');
      for (let i = totalRecsPages - 2; i <= totalRecsPages; i++) pages.push(i);
    } else {
      pages.push(1, '...', recsPage, '...', totalRecsPages);
    }
    return pages;
  };

  // Stats card component for reuse
  const StatCard = ({ icon: Icon, label, value, color, loading }) => (
    <motion.div whileHover={{ scale: 1.02 }} className="glass rounded-xl p-4">
      <div className="flex items-center gap-3">
        <div className={`w-10 h-10 ${color} rounded-lg flex items-center justify-center`}>
          <Icon className="w-5 h-5" />
        </div>
        <div>
          <p className="text-gray-600 text-xs">{label}</p>
          {loading ? (
            <div className="h-6 w-8 bg-gray-200 rounded animate-pulse mt-1"></div>
          ) : (
            <motion.p
              initial={{ opacity: 0, scale: 0.5 }}
              animate={{ opacity: 1, scale: 1 }}
              className="text-xl font-bold text-gray-900"
            >
              {value}
            </motion.p>
          )}
        </div>
      </div>
    </motion.div>
  );

  return (
    <div className="min-h-screen py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header - Always visible immediately */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-12"
        >
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-4">
              <div className="w-16 h-16 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-full flex items-center justify-center">
                <User className="w-8 h-8 text-white" />
              </div>
              <div>
                <h1 className="text-3xl font-bold text-gray-900">My Dashboard</h1>
                <p className="text-gray-600">Personalized recommendations just for you</p>
              </div>
            </div>

            <div className="flex items-center gap-4">
              <Link to="/activity">
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="px-6 py-3 bg-gradient-to-r from-purple-500 to-pink-600 text-white rounded-lg font-semibold shadow-lg hover:shadow-xl transition-all flex items-center gap-2"
                >
                  <ArrowRight className="w-5 h-5" />
                  View History
                </motion.button>
              </Link>

              <div className="flex items-center gap-2">
                <span className="text-sm text-gray-600">Demo User:</span>
                <select
                  value={userId}
                  onChange={(e) => setUserId(parseInt(e.target.value))}
                  className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  {[1, 2, 3, 4, 5, 10, 25, 50].map(id => (
                    <option key={id} value={id}>User {id}</option>
                  ))}
                </select>
              </div>
            </div>
          </div>

          {/* Stats Cards - Show immediately with loading states */}
          <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-4">
            <StatCard icon={ShoppingBag} label="Views" value={viewsCount} color="bg-blue-100 text-blue-600" loading={statsLoading} />
            <StatCard icon={ShoppingCart} label="Purchases" value={purchasesCount} color="bg-green-100 text-green-600" loading={statsLoading} />
            <StatCard icon={Star} label="Ratings" value={ratingsCount} color="bg-yellow-100 text-yellow-600" loading={statsLoading} />
            <StatCard icon={Heart} label="Wishlist" value={wishlistCount} color="bg-pink-100 text-pink-600" loading={false} />
            <StatCard icon={ShoppingCart} label="In Cart" value={cartCount} color="bg-indigo-100 text-indigo-600" loading={false} />
            <StatCard icon={TrendingUp} label="Total Spent" value={`$${totalSpent.toFixed(0)}`} color="bg-purple-100 text-purple-600" loading={statsLoading} />
          </div>
        </motion.div>

        {/* Algorithm Selector - Always visible */}
        <div className="mb-8">
          <p className="text-sm font-medium text-gray-700 mb-3">Recommendation Algorithm:</p>
          <div className="flex flex-wrap gap-3">
            {['hybrid', 'collaborative', 'content', 'popular'].map((algo) => (
              <motion.button
                key={algo}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => setAlgorithm(algo)}
                className={`px-4 py-2 rounded-lg font-medium capitalize transition-all ${algorithm === algo
                  ? 'bg-gradient-to-r from-blue-500 to-indigo-600 text-white shadow-lg'
                  : 'bg-white text-gray-700 hover:bg-gray-50'
                  }`}
              >
                {algo === 'popular' ? '🔥 Popular' : algo}
              </motion.button>
            ))}
          </div>
          <p className="text-xs text-gray-500 mt-2">
            {algorithm === 'hybrid' && '✨ Combines collaborative filtering and content-based recommendations'}
            {algorithm === 'collaborative' && '👥 Based on users with similar preferences'}
            {algorithm === 'content' && '🎯 Based on products similar to your interests'}
            {algorithm === 'popular' && '🔥 Most viewed and purchased products by all users'}
          </p>
        </div>

        {/* Recommendations Section */}
        <section className="mb-16">
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            className="flex items-center gap-3 mb-8"
          >
            <Sparkles className="w-8 h-8 text-blue-600" />
            <h2 className="text-3xl font-bold text-gray-900">Recommended For You</h2>
          </motion.div>

          {recsLoading ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 xl:grid-cols-5 gap-6">
              {[...Array(10)].map((_, i) => (
                <SkeletonCard key={i} />
              ))}
            </div>
          ) : (
            <>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 xl:grid-cols-5 gap-6">
                {currentRecs.map((product, index) => (
                  <motion.div
                    key={product.product_id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.03 }}
                  >
                    <ProductCard product={product} showScore={true} />
                  </motion.div>
                ))}
              </div>

              {/* Pagination */}
              {totalRecsPages > 1 && (
                <div className="flex items-center justify-center gap-2 mt-12">
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={() => setRecsPage(p => Math.max(1, p - 1))}
                    disabled={recsPage === 1}
                    className={`px-4 py-2 rounded-lg font-medium transition-all ${recsPage === 1
                      ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                      : 'bg-white text-gray-700 hover:bg-gray-50 border border-gray-300 shadow-sm'
                      }`}
                  >
                    Previous
                  </motion.button>

                  <div className="flex items-center gap-2">
                    {getRecsPageNumbers().map((page, idx) => (
                      page === '...' ? (
                        <span key={`ellipsis-${idx}`} className="px-2 text-gray-500">...</span>
                      ) : (
                        <motion.button
                          key={page}
                          whileHover={{ scale: 1.1 }}
                          whileTap={{ scale: 0.95 }}
                          onClick={() => setRecsPage(page)}
                          className={`w-10 h-10 rounded-lg font-medium transition-all ${recsPage === page
                            ? 'bg-gradient-to-r from-blue-500 to-indigo-600 text-white shadow-lg'
                            : 'bg-white text-gray-700 hover:bg-gray-50 border border-gray-300'
                            }`}
                        >
                          {page}
                        </motion.button>
                      )
                    ))}
                  </div>

                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={() => setRecsPage(p => Math.min(totalRecsPages, p + 1))}
                    disabled={recsPage === totalRecsPages}
                    className={`px-4 py-2 rounded-lg font-medium transition-all ${recsPage === totalRecsPages
                      ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                      : 'bg-white text-gray-700 hover:bg-gray-50 border border-gray-300 shadow-sm'
                      }`}
                  >
                    Next
                  </motion.button>
                </div>
              )}
            </>
          )}
        </section>
      </div>
    </div>
  );
};

export default UserDashboard;