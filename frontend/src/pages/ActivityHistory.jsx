import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { History, Filter, Download, Calendar } from 'lucide-react';
import { interactionsAPI } from '../api/client';
import { useUser } from '../context/UserContext';

const ActivityHistory = () => {
  const { userId, setUserId } = useUser();
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [currentPage, setCurrentPage] = useState(1);
  const [filterType, setFilterType] = useState('all');
  const itemsPerPage = 20;

  useEffect(() => {
    loadHistory();
  }, [userId]);

  const loadHistory = async () => {
    try {
      setLoading(true);
      const historyRes = await interactionsAPI.getUserHistory(userId, 500);
      setHistory(historyRes.data.interactions);
    } catch (error) {
      console.error('Error loading history:', error);
    } finally {
      setLoading(false);
    }
  };

  // Filter by interaction type
  const filteredHistory = filterType === 'all'
    ? history
    : history.filter(h => h.interaction_type === filterType);

  // Pagination
  const totalPages = Math.ceil(filteredHistory.length / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  const currentItems = filteredHistory.slice(startIndex, endIndex);

  // Reset to page 1 when filter changes
  useEffect(() => {
    setCurrentPage(1);
  }, [filterType]);

  const getPageNumbers = () => {
    const pages = [];
    const maxVisible = 7;

    if (totalPages <= maxVisible) {
      for (let i = 1; i <= totalPages; i++) {
        pages.push(i);
      }
    } else {
      if (currentPage <= 3) {
        for (let i = 1; i <= 5; i++) pages.push(i);
        pages.push('...');
        pages.push(totalPages);
      } else if (currentPage >= totalPages - 2) {
        pages.push(1);
        pages.push('...');
        for (let i = totalPages - 4; i <= totalPages; i++) pages.push(i);
      } else {
        pages.push(1);
        pages.push('...');
        for (let i = currentPage - 1; i <= currentPage + 1; i++) pages.push(i);
        pages.push('...');
        pages.push(totalPages);
      }
    }

    return pages;
  };

  // Statistics
  const stats = {
    total: history.length,
    views: history.filter(h => h.interaction_type === 'view').length,
    purchases: history.filter(h => h.interaction_type === 'purchase').length,
    ratings: history.filter(h => h.interaction_type === 'rating').length,
    totalSpent: history
      .filter(h => h.interaction_type === 'purchase')
      .reduce((sum, h) => sum + h.product_price, 0),
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
          className="w-16 h-16 border-4 border-orange-500 border-t-transparent rounded-full"
        />
      </div>
    );
  }

  return (
    <div className="min-h-screen py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-gradient-to-r from-orange-500 to-orange-600 rounded-lg flex items-center justify-center">
                <History className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-3xl font-bold text-gray-900">Activity History</h1>
                <p className="text-gray-600">Complete history of all your interactions</p>
              </div>
            </div>

            {/* User Switcher */}
            <div className="flex items-center gap-2">
              <span className="text-sm text-gray-600">User:</span>
              <select
                value={userId}
                onChange={(e) => setUserId(parseInt(e.target.value))}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
              >
                {[1, 2, 3, 4, 5, 10, 25, 50].map(id => (
                  <option key={id} value={id}>User {id}</option>
                ))}
              </select>
            </div>
          </div>

          {/* Stats Cards */}
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
            <motion.div
              whileHover={{ scale: 1.02 }}
              className="glass rounded-lg p-4"
            >
              <p className="text-sm text-gray-600">Total Activities</p>
              <p className="text-2xl font-bold text-gray-900">{stats.total}</p>
            </motion.div>

            <motion.div
              whileHover={{ scale: 1.02 }}
              className="glass rounded-lg p-4"
            >
              <p className="text-sm text-gray-600">Views</p>
              <p className="text-2xl font-bold text-slate-600">{stats.views}</p>
            </motion.div>

            <motion.div
              whileHover={{ scale: 1.02 }}
              className="glass rounded-lg p-4"
            >
              <p className="text-sm text-gray-600">Purchases</p>
              <p className="text-2xl font-bold text-green-600">{stats.purchases}</p>
            </motion.div>

            <motion.div
              whileHover={{ scale: 1.02 }}
              className="glass rounded-lg p-4"
            >
              <p className="text-sm text-gray-600">Ratings</p>
              <p className="text-2xl font-bold text-yellow-600">{stats.ratings}</p>
            </motion.div>

            <motion.div
              whileHover={{ scale: 1.02 }}
              className="glass rounded-lg p-4"
            >
              <p className="text-sm text-gray-600">Total Spent</p>
              <p className="text-2xl font-bold text-orange-600">${stats.totalSpent.toFixed(2)}</p>
            </motion.div>
          </div>
        </motion.div>

        {/* Filters */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-2">
            <Filter className="w-5 h-5 text-gray-600" />
            <span className="text-sm font-medium text-gray-700">Filter:</span>
            {['all', 'view', 'purchase', 'rating', 'wishlist'].map((type) => (
              <motion.button
                key={type}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => setFilterType(type)}
                className={`px-4 py-2 rounded-lg font-medium capitalize transition-all ${filterType === type
                  ? 'bg-gradient-to-r from-slate-700 to-slate-900 text-white shadow-lg'
                  : 'bg-white text-gray-700 hover:bg-gray-50 border border-gray-300'
                  }`}
              >
                {type}
              </motion.button>
            ))}
          </div>

          <span className="text-sm text-gray-600">
            Showing {startIndex + 1}-{Math.min(endIndex, filteredHistory.length)} of {filteredHistory.length}
          </span>
        </div>

        {/* Activity Table */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="glass rounded-xl overflow-hidden"
        >
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 border-b border-gray-200">
                <tr>
                  <th className="px-6 py-4 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Product
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Category
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Action
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Price
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Date
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {currentItems.map((item) => (
                  <motion.tr
                    key={item.id}
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="hover:bg-gray-50 transition-colors"
                  >
                    <td className="px-6 py-4">
                      <div className="font-medium text-gray-900">{item.product_title}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="px-2 py-1 text-xs font-medium bg-slate-100 text-slate-700 rounded-full">
                        {item.product_category}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${item.interaction_type === 'purchase'
                        ? 'bg-green-100 text-green-700'
                        : item.interaction_type === 'rating'
                          ? 'bg-yellow-100 text-yellow-700'
                          : item.interaction_type === 'wishlist'
                            ? 'bg-pink-100 text-pink-700'
                            : 'bg-gray-100 text-gray-700'
                        }`}>
                        {item.interaction_type}
                        {item.rating && ` (${item.rating}⭐)`}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-gray-900 font-medium">
                      ${item.product_price.toFixed(2)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {new Date(item.timestamp).toLocaleDateString('en-US', {
                        year: 'numeric',
                        month: 'short',
                        day: 'numeric'
                      })}
                    </td>
                  </motion.tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-between px-6 py-4 border-t border-gray-200 bg-gray-50">
              <div className="flex items-center gap-2">
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                  disabled={currentPage === 1}
                  className={`px-4 py-2 rounded-lg font-medium transition-all ${currentPage === 1
                    ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                    : 'bg-white text-gray-700 hover:bg-gray-50 border border-gray-300'
                    }`}
                >
                  Previous
                </motion.button>

                <div className="flex items-center gap-2">
                  {getPageNumbers().map((page, idx) => (
                    page === '...' ? (
                      <span key={`ellipsis-${idx}`} className="px-2 text-gray-500">...</span>
                    ) : (
                      <motion.button
                        key={page}
                        whileHover={{ scale: 1.1 }}
                        whileTap={{ scale: 0.95 }}
                        onClick={() => setCurrentPage(page)}
                        className={`w-10 h-10 rounded-lg font-medium transition-all ${currentPage === page
                          ? 'bg-gradient-to-r from-slate-700 to-slate-900 text-white shadow-lg'
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
                  onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                  disabled={currentPage === totalPages}
                  className={`px-4 py-2 rounded-lg font-medium transition-all ${currentPage === totalPages
                    ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                    : 'bg-white text-gray-700 hover:bg-gray-50 border border-gray-300'
                    }`}
                >
                  Next
                </motion.button>
              </div>
            </div>
          )}
        </motion.div>
      </div>
    </div>
  );
};

export default ActivityHistory;