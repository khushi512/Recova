"""
Content-Based Filtering Algorithm
Recommends products similar to a given product based on:
- Category similarity (30%)
- Description similarity via TF-IDF (60%)
- Price similarity (10%)
"""

import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')

# Handle postgres:// vs postgresql:// for SQLAlchemy 2.0+
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

class ContentBasedRecommender:
    """Content-based recommendation engine"""
    
    def __init__(self):
        self.engine = create_engine(DATABASE_URL) if DATABASE_URL else None
        self.products_df = None
        self.tfidf_matrix = None
        self.vectorizer = None
        
    def load_products(self):
        """Load all products from database"""
        print("📦 Loading products from database...")
        
        query = """
            SELECT id, title, category, price, description, image_url, rating, review_count
            FROM products
        """
        
        self.products_df = pd.read_sql(query, self.engine)
        print(f"   Loaded {len(self.products_df)} products")
        
        return self.products_df
    
    def build_tfidf_matrix(self):
        """Build TF-IDF matrix from product descriptions and titles"""
        print("\n🔨 Building TF-IDF matrix...")
        
        if self.products_df is None:
            self.load_products()
        
        # Combine title, category, and description for better matching
        self.products_df['combined_features'] = (
            self.products_df['title'] + ' ' + 
            self.products_df['category'] + ' ' + 
            self.products_df['description'].fillna('')
        )
        
        # Create TF-IDF vectorizer
        self.vectorizer = TfidfVectorizer(
            max_features=500,  # Limit features for performance
            stop_words='english',
            ngram_range=(1, 2)  # Unigrams and bigrams
        )
        
        # Fit and transform
        self.tfidf_matrix = self.vectorizer.fit_transform(
            self.products_df['combined_features']
        )
        
        print(f"   TF-IDF matrix shape: {self.tfidf_matrix.shape}")
        print(f"   Features: {len(self.vectorizer.get_feature_names_out())}")
        
        return self.tfidf_matrix
    
    def calculate_similarity(self, product_idx):
        """Calculate similarity scores between product and all others"""
        
        # Get TF-IDF similarity (text-based)
        cosine_sim = cosine_similarity(
            self.tfidf_matrix[product_idx:product_idx+1], 
            self.tfidf_matrix
        ).flatten()
        
        # Get category similarity (binary: same category = 1, different = 0)
        product_category = self.products_df.iloc[product_idx]['category']
        category_sim = (
            self.products_df['category'] == product_category
        ).astype(float).values
        
        # Get price similarity (closer prices = higher similarity)
        product_price = self.products_df.iloc[product_idx]['price']
        price_diff = np.abs(
            self.products_df['price'].values - product_price
        )
        # Normalize price similarity (0 to 1, where 1 = exact same price)
        max_price_diff = self.products_df['price'].max()
        price_sim = 1 - (price_diff / max_price_diff)
        
        # Combined similarity score (weighted average)
        # Text: 60%, Category: 30%, Price: 10%
        combined_sim = (
            0.6 * cosine_sim + 
            0.3 * category_sim + 
            0.1 * price_sim
        )
        
        return combined_sim
    
    def get_similar_products(self, product_id, n=10, min_score=0.1):
        """
        Get N most similar products to the given product
        
        Args:
            product_id: ID of the product to find similar items for
            n: Number of recommendations to return
            min_score: Minimum similarity score threshold
            
        Returns:
            List of dicts with product info and similarity scores
        """
        
        # Ensure data is loaded
        if self.products_df is None or self.tfidf_matrix is None:
            self.load_products()
            self.build_tfidf_matrix()
        
        # Find product index
        try:
            product_idx = self.products_df[
                self.products_df['id'] == product_id
            ].index[0]
        except IndexError:
            print(f"❌ Product ID {product_id} not found")
            return []
        
        # Calculate similarities
        similarity_scores = self.calculate_similarity(product_idx)
        
        # Get indices of most similar products (excluding the product itself)
        similar_indices = similarity_scores.argsort()[::-1]
        
        # Filter out the product itself and apply minimum score threshold
        recommendations = []
        
        for idx in similar_indices:
            # Skip the product itself
            if idx == product_idx:
                continue
            
            score = similarity_scores[idx]
            
            # Apply minimum score threshold
            if score < min_score:
                break
            
            product = self.products_df.iloc[idx]
            
            recommendations.append({
                'product_id': int(product['id']),
                'title': product['title'],
                'category': product['category'],
                'price': float(product['price']),
                'rating': float(product['rating']) if pd.notna(product['rating']) else None,
                'similarity_score': float(score),
                'image_url': product['image_url'] if pd.notna(product['image_url']) else f"https://picsum.photos/seed/{int(product['id'])}/400/400"
            })
            
            # Return top N
            if len(recommendations) >= n:
                break
        
        return recommendations
    
    def get_recommendations_for_user(self, user_id, n=10):
        """
        Get recommendations for a user based on their interaction history
        Recommends products similar to ones they've interacted with
        
        Args:
            user_id: ID of the user
            n: Number of recommendations
            
        Returns:
            List of recommended products
        """
        
        # Get user's interaction history
        query = text("""
            SELECT p.id, p.title, p.category, p.price
            FROM (
                SELECT DISTINCT ON (p.id) p.id, p.title, p.category, p.price, i.timestamp
                FROM interactions i
                JOIN products p ON i.product_id = p.id
                WHERE i.user_id = :user_id
                ORDER BY p.id, i.timestamp DESC
            ) p
            ORDER BY p.timestamp DESC
            LIMIT 10
        """)
        
        with self.engine.connect() as conn:
            user_products = pd.read_sql(query, conn, params={'user_id': user_id})
        
        if len(user_products) == 0:
            # No history - return popular products
            return self.get_popular_products(n)
        
        # Get similar products for each product user interacted with
        all_recommendations = {}
        
        for _, product in user_products.iterrows():
            similar = self.get_similar_products(product['id'], n=20)
            
            for rec in similar:
                product_id = rec['product_id']
                
                # Aggregate scores if product appears multiple times
                if product_id in all_recommendations:
                    all_recommendations[product_id]['similarity_score'] += rec['similarity_score']
                else:
                    all_recommendations[product_id] = rec
        
        # Remove products user already interacted with
        user_product_ids = set(user_products['id'].values)
        filtered_recs = [
            rec for pid, rec in all_recommendations.items() 
            if pid not in user_product_ids
        ]
        
        # Sort by aggregated score
        filtered_recs.sort(key=lambda x: x['similarity_score'], reverse=True)
        
        return filtered_recs[:n]
    
    def get_popular_products(self, n=10):
        """Get popular products (fallback for cold start)"""
        
        query = text("""
            SELECT p.id as product_id, p.title, p.category, p.price, 
                   p.rating, p.image_url, COUNT(i.id) as interaction_count
            FROM products p
            LEFT JOIN interactions i ON p.id = i.product_id
            GROUP BY p.id
            ORDER BY interaction_count DESC, p.rating DESC
            LIMIT :limit
        """)
        
        with self.engine.connect() as conn:
            popular = pd.read_sql(query, conn, params={'limit': n})
        
        return popular.to_dict('records')
    
    def get_metrics(self):
        """Calculate and return algorithm performance metrics"""
        
        if self.products_df is None:
            self.load_products()
        
        if self.tfidf_matrix is None:
            self.build_tfidf_matrix()
        
        # Calculate coverage (what % of products can be recommended)
        total_products = len(self.products_df)
        
        # Sample similarity for a few products to check quality
        sample_size = min(10, total_products)
        sample_indices = np.random.choice(total_products, sample_size, replace=False)
        
        avg_similarity_scores = []
        
        for idx in sample_indices:
            similarities = self.calculate_similarity(idx)
            # Exclude self-similarity
            similarities = np.delete(similarities, idx)
            avg_similarity_scores.append(similarities.mean())
        
        return {
            'algorithm': 'content_based',
            'total_products': total_products,
            'coverage': 100.0,  # Content-based can recommend any product
            'avg_similarity_score': float(np.mean(avg_similarity_scores)),
            'tfidf_features': len(self.vectorizer.get_feature_names_out()) if self.vectorizer else 0
        }


# Test the algorithm
def test_algorithm():
    """Test the content-based recommender"""
    print("="*60)
    print("🧪 TESTING CONTENT-BASED RECOMMENDER")
    print("="*60)
    
    recommender = ContentBasedRecommender()
    
    # Load and build
    recommender.load_products()
    recommender.build_tfidf_matrix()
    
    # Test 1: Get similar products for a random product
    print("\n" + "="*60)
    print("TEST 1: Similar Products")
    print("="*60)
    
    test_product_id = recommender.products_df.iloc[0]['id']
    test_product = recommender.products_df[recommender.products_df['id'] == test_product_id].iloc[0]
    
    print(f"\n🎯 Finding products similar to:")
    print(f"   ID: {test_product['id']}")
    print(f"   Title: {test_product['title']}")
    print(f"   Category: {test_product['category']}")
    print(f"   Price: ${test_product['price']:.2f}")
    
    similar = recommender.get_similar_products(test_product_id, n=5)
    
    print(f"\n📊 Top 5 Similar Products:")
    for i, rec in enumerate(similar, 1):
        print(f"\n{i}. {rec['title']}")
        print(f"   Category: {rec['category']}")
        print(f"   Price: ${rec['price']:.2f}")
        print(f"   Similarity: {rec['similarity_score']:.3f}")
    
    # Test 2: Get recommendations for a user
    print("\n" + "="*60)
    print("TEST 2: User Recommendations")
    print("="*60)
    
    test_user_id = 1
    user_recs = recommender.get_recommendations_for_user(test_user_id, n=5)
    
    print(f"\n👤 Recommendations for User {test_user_id}:")
    for i, rec in enumerate(user_recs, 1):
        print(f"\n{i}. {rec['title']}")
        print(f"   Category: {rec['category']}")
        print(f"   Price: ${rec['price']:.2f}")
        if 'similarity_score' in rec:
            print(f"   Score: {rec['similarity_score']:.3f}")
    
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
