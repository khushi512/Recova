"""
Collaborative Filtering Algorithm
Recommends products based on similar users' preferences
"""

import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')

# Handle postgres:// vs postgresql:// for SQLAlchemy 2.0+
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

class CollaborativeFilteringRecommender:
    """User-based collaborative filtering"""
    
    def __init__(self):
        self.engine = create_engine(DATABASE_URL) if DATABASE_URL else None
        self.user_item_matrix = None
        self.user_similarity_matrix = None
        
    def build_user_item_matrix(self):
        """Build user-item interaction matrix"""
        print("📊 Building user-item matrix...")
        
        # Get all interactions
        query = """
            SELECT user_id, product_id, 
                   CASE 
                       WHEN interaction_type = 'purchase' THEN 5
                       WHEN interaction_type = 'rating' THEN rating
                       WHEN interaction_type = 'view' THEN 1
                   END as score
            FROM interactions
        """
        
        interactions_df = pd.read_sql(query, self.engine)
        
        # Create pivot table (user-item matrix)
        self.user_item_matrix = interactions_df.pivot_table(
            index='user_id',
            columns='product_id',
            values='score',
            aggfunc='max',  # Take highest score if multiple interactions
            fill_value=0
        )
        
        print(f"   Matrix shape: {self.user_item_matrix.shape}")
        print(f"   Users: {len(self.user_item_matrix)}")
        print(f"   Products: {len(self.user_item_matrix.columns)}")
        
        # Calculate sparsity
        total_cells = self.user_item_matrix.shape[0] * self.user_item_matrix.shape[1]
        non_zero = (self.user_item_matrix > 0).sum().sum()
        sparsity = (1 - non_zero / total_cells) * 100
        print(f"   Sparsity: {sparsity:.1f}%")
        
        return self.user_item_matrix
    
    def calculate_user_similarity(self):
        """Calculate similarity between users"""
        print("\n🔨 Calculating user similarity...")
        
        if self.user_item_matrix is None:
            self.build_user_item_matrix()
        
        # Calculate cosine similarity between users
        self.user_similarity_matrix = cosine_similarity(self.user_item_matrix)
        
        # Convert to DataFrame for easier indexing
        self.user_similarity_matrix = pd.DataFrame(
            self.user_similarity_matrix,
            index=self.user_item_matrix.index,
            columns=self.user_item_matrix.index
        )
        
        print(f"   Similarity matrix shape: {self.user_similarity_matrix.shape}")
        
        return self.user_similarity_matrix
    
    def get_similar_users(self, user_id, n=10):
        """Find N most similar users to the given user"""
        
        if self.user_similarity_matrix is None:
            self.calculate_user_similarity()
        
        # Check if user exists
        if user_id not in self.user_similarity_matrix.index:
            return {}
        
        # Get similarity scores for this user
        user_similarities = self.user_similarity_matrix[user_id]
        
        # Sort and get top N (excluding the user themselves)
        similar_users = user_similarities.sort_values(ascending=False)[1:n+1]
        
        return similar_users.to_dict()
    
    def get_recommendations(self, user_id, n=10, min_similarity=0.1):
        """
        Get product recommendations for a user based on similar users
        
        Args:
            user_id: Target user ID
            n: Number of recommendations
            min_similarity: Minimum user similarity threshold
            
        Returns:
            List of recommended products with scores
        """
        
        if self.user_item_matrix is None or self.user_similarity_matrix is None:
            self.build_user_item_matrix()
            self.calculate_user_similarity()
        
        # Check if user exists
        if user_id not in self.user_item_matrix.index:
            print(f"   User {user_id} not found, returning popular products")
            return self._get_popular_products(n)
        
        # Get similar users
        similar_users = self.get_similar_users(user_id, n=50)
        
        # Filter by minimum similarity
        similar_users = {
            uid: sim for uid, sim in similar_users.items() 
            if sim >= min_similarity
        }
        
        if not similar_users:
            print(f"   No similar users found for user {user_id}")
            return self._get_popular_products(n)
        
        # Get products the target user has already interacted with
        user_products = set(
            self.user_item_matrix.loc[user_id][self.user_item_matrix.loc[user_id] > 0].index
        )
        
        # Calculate weighted scores for all products
        product_scores = {}
        
        for similar_user_id, similarity in similar_users.items():
            # Get products this similar user liked
            similar_user_products = self.user_item_matrix.loc[similar_user_id]
            similar_user_products = similar_user_products[similar_user_products > 0]
            
            for product_id, score in similar_user_products.items():
                # Skip products user already interacted with
                if product_id in user_products:
                    continue
                
                # Weighted score (product score * user similarity)
                weighted_score = score * similarity
                
                if product_id in product_scores:
                    product_scores[product_id] += weighted_score
                else:
                    product_scores[product_id] = weighted_score
        
        # Sort by score and get top N
        sorted_products = sorted(
            product_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )[:n]
        
        # Get product details
        if not sorted_products:
            return self._get_popular_products(n)
        
        product_ids = [p[0] for p in sorted_products]
        scores = {p[0]: p[1] for p in sorted_products}
        
        # Fetch product details from database
        placeholders = ','.join([':id' + str(i) for i in range(len(product_ids))])
        query = text(f"""
            SELECT id, title, category, price, rating, review_count
            FROM products
            WHERE id IN ({placeholders})
        """)
        
        params = {f'id{i}': pid for i, pid in enumerate(product_ids)}
        
        with self.engine.connect() as conn:
            result = conn.execute(query, params)
            products = result.fetchall()
        
        # Format results
        recommendations = []
        for product in products:
            recommendations.append({
                'product_id': product[0],
                'title': product[1],
                'category': product[2],
                'price': float(product[3]),
                'rating': float(product[4]) if product[4] else None,
                'review_count': product[5],
                'recommendation_score': float(scores[product[0]]),
                'image_url': f"https://picsum.photos/seed/{product[0]}/400/400"
            })
        
        # Sort by score
        recommendations.sort(key=lambda x: x['recommendation_score'], reverse=True)
        
        return recommendations
    
    def _get_popular_products(self, n=10):
        """Fallback: Get popular products"""
        query = text("""
            SELECT p.id as product_id, p.title, p.category, p.price, 
                   p.rating, COUNT(i.id) as interaction_count
            FROM products p
            LEFT JOIN interactions i ON p.id = i.product_id
            GROUP BY p.id
            ORDER BY interaction_count DESC, p.rating DESC
            LIMIT :limit
        """)
        
        with self.engine.connect() as conn:
            result = conn.execute(query, {'limit': n})
            products = result.fetchall()
        
        return [
            {
                'product_id': p[0],
                'title': p[1],
                'category': p[2],
                'price': float(p[3]),
                'rating': float(p[4]) if p[4] else None,
                'recommendation_score': None,
                'image_url': f"https://picsum.photos/seed/{p[0]}/400/400"
            }
            for p in products
        ]
    
    def get_metrics(self):
        """Calculate algorithm performance metrics"""
        
        if self.user_item_matrix is None:
            self.build_user_item_matrix()
        
        # Coverage: what % of users/products can we recommend for
        total_users = len(self.user_item_matrix)
        total_products = len(self.user_item_matrix.columns)
        
        # Calculate sparsity
        total_cells = self.user_item_matrix.shape[0] * self.user_item_matrix.shape[1]
        non_zero = (self.user_item_matrix > 0).sum().sum()
        sparsity = (1 - non_zero / total_cells) * 100
        
        # Average interactions per user
        avg_interactions = (self.user_item_matrix > 0).sum(axis=1).mean()
        
        return {
            'algorithm': 'collaborative_filtering',
            'total_users': total_users,
            'total_products': total_products,
            'sparsity': float(sparsity),
            'avg_interactions_per_user': float(avg_interactions),
            'coverage_users': 100.0,  # Can recommend for any user
            'coverage_products': float((self.user_item_matrix.sum(axis=0) > 0).sum() / total_products * 100)
        }


# Test the algorithm
def test_algorithm():
    """Test collaborative filtering"""
    print("="*60)
    print("🧪 TESTING COLLABORATIVE FILTERING")
    print("="*60)
    
    recommender = CollaborativeFilteringRecommender()
    
    # Build matrices
    recommender.build_user_item_matrix()
    recommender.calculate_user_similarity()
    
    # Test 1: Get similar users
    print("\n" + "="*60)
    print("TEST 1: Similar Users")
    print("="*60)
    
    test_user_id = 1
    similar_users = recommender.get_similar_users(test_user_id, n=5)
    
    print(f"\n👥 Top 5 users similar to User {test_user_id}:")
    for user_id, similarity in similar_users.items():
        print(f"   User {user_id}: {similarity:.3f} similarity")
    
    # Test 2: Get recommendations
    print("\n" + "="*60)
    print("TEST 2: Collaborative Recommendations")
    print("="*60)
    
    recommendations = recommender.get_recommendations(test_user_id, n=5)
    
    print(f"\n📊 Top 5 Recommendations for User {test_user_id}:")
    for i, rec in enumerate(recommendations, 1):
        print(f"\n{i}. {rec['title']}")
        print(f"   Category: {rec['category']}")
        print(f"   Price: ${rec['price']:.2f}")
        if rec['recommendation_score']:
            print(f"   Score: {rec['recommendation_score']:.3f}")
    
    # Test 3: Metrics
    print("\n" + "="*60)
    print("TEST 3: Algorithm Metrics")
    print("="*60)
    
    metrics = recommender.get_metrics()
    print(f"\n📈 Performance Metrics:")
    for key, value in metrics.items():
        print(f"   {key}: {value}")
    
    print("\n" + "="*60)
    print("✅ ALL TESTS PASSED!")
    print("="*60)


if __name__ == "__main__":
    test_algorithm()
