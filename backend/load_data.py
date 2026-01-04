import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os
import sys

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

if not DATABASE_URL:
    print("❌ ERROR: DATABASE_URL not found in .env file")
    print("Please add your NeonDB connection string to backend/.env")
    sys.exit(1)

# Handle postgres:// vs postgresql:// for SQLAlchemy 2.0+
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

def create_tables(engine):
    """Create database tables with proper schema"""
    print("\n🏗️  Creating database tables...")
    
    with engine.connect() as conn:
        # Drop existing tables (careful - this deletes all data!)
        print("   Dropping existing tables...")
        conn.execute(text("""
            DROP TABLE IF EXISTS cached_recommendations CASCADE;
            DROP TABLE IF EXISTS interactions CASCADE;
            DROP TABLE IF EXISTS products CASCADE;
            DROP TABLE IF EXISTS users CASCADE;
        """))
        conn.commit()
        
        # Create products table
        print("   Creating products table...")
        conn.execute(text("""
            CREATE TABLE products (
                id SERIAL PRIMARY KEY,
                title VARCHAR(500) NOT NULL,
                category VARCHAR(100) NOT NULL,
                price DECIMAL(10,2) NOT NULL,
                description TEXT,
                image_url VARCHAR(500),
                rating DECIMAL(3,2),
                review_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT NOW()
            );
        """))
        
        # Create users table
        print("   Creating users table...")
        conn.execute(text("""
            CREATE TABLE users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(100) UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT NOW()
            );
        """))
        
        # Create interactions table
        print("   Creating interactions table...")
        conn.execute(text("""
            CREATE TABLE interactions (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                product_id INTEGER REFERENCES products(id) ON DELETE CASCADE,
                interaction_type VARCHAR(20) NOT NULL,
                rating INTEGER CHECK (rating >= 1 AND rating <= 5),
                timestamp TIMESTAMP DEFAULT NOW()
            );
        """))
        
        # Create cached recommendations table (for performance)
        print("   Creating cached_recommendations table...")
        conn.execute(text("""
            CREATE TABLE cached_recommendations (
                id SERIAL PRIMARY KEY,
                user_id INTEGER,
                product_id INTEGER REFERENCES products(id) ON DELETE CASCADE,
                algorithm VARCHAR(50) NOT NULL,
                score DECIMAL(5,4),
                computed_at TIMESTAMP DEFAULT NOW()
            );
        """))
        
        # Create indexes for better query performance
        print("   Creating indexes...")
        conn.execute(text("""
            CREATE INDEX idx_interactions_user ON interactions(user_id);
            CREATE INDEX idx_interactions_product ON interactions(product_id);
            CREATE INDEX idx_interactions_type ON interactions(interaction_type);
            CREATE INDEX idx_products_category ON products(category);
            CREATE INDEX idx_products_rating ON products(rating);
            CREATE INDEX idx_cached_recs_user_algo ON cached_recommendations(user_id, algorithm);
        """))
        
        conn.commit()
    
    print("   ✅ Tables created successfully!")

def load_csv_data(engine):
    """Load CSV data into database tables"""
    print("\n📥 Loading data from CSV files...")
    
    # Determine the correct path to CSV files
    data_path = os.path.join(os.path.dirname(__file__), '..', 'data')
    
    # Fallback paths
    if not os.path.exists(os.path.join(data_path, 'users.csv')):
        data_path = '../data'
    if not os.path.exists(os.path.join(data_path, 'users.csv')):
        data_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data')
    
    try:
        # Load users
        print("   Loading users...")
        users_df = pd.read_csv(os.path.join(data_path, 'users.csv'))
        users_df[['id', 'username']].to_sql('users', engine, if_exists='append', index=False)
        print(f"      ✅ Loaded {len(users_df)} users")
        
        # Load products
        print("   Loading products...")
        products_df = pd.read_csv(os.path.join(data_path, 'products.csv'))
        products_df.to_sql('products', engine, if_exists='append', index=False)
        print(f"      ✅ Loaded {len(products_df)} products")
        
        # Load interactions
        print("   Loading interactions...")
        interactions_df = pd.read_csv(os.path.join(data_path, 'interactions.csv'))
        interactions_df.to_sql('interactions', engine, if_exists='append', index=False)
        print(f"      ✅ Loaded {len(interactions_df)} interactions")
        
        print("\n   ✅ All data loaded successfully!")
        
    except FileNotFoundError as e:
        print(f"\n   ❌ Error: CSV file not found: {e}")
        print(f"   Make sure CSV files are in: {os.path.abspath(data_path)}")
        print(f"   Run 'python data/generate_data.py' first to create them.")
        sys.exit(1)
    except Exception as e:
        print(f"\n   ❌ Error loading data: {e}")
        raise

def verify_data(engine):
    """Verify data was loaded correctly and show statistics"""
    print("\n🔍 Verifying data...")
    
    with engine.connect() as conn:
        # Count records
        users_count = conn.execute(text("SELECT COUNT(*) FROM users")).scalar()
        products_count = conn.execute(text("SELECT COUNT(*) FROM products")).scalar()
        interactions_count = conn.execute(text("SELECT COUNT(*) FROM interactions")).scalar()
        
        print("\n" + "="*60)
        print("📊 DATABASE STATISTICS")
        print("="*60)
        print(f"Users:        {users_count:,}")
        print(f"Products:     {products_count:,}")
        print(f"Interactions: {interactions_count:,}")
        
        # Category distribution
        print("\n" + "="*60)
        print("📦 PRODUCTS BY CATEGORY")
        print("="*60)
        category_stats = conn.execute(text("""
            SELECT category, COUNT(*) as count, 
                   ROUND(AVG(price)::numeric, 2) as avg_price, 
                   ROUND(AVG(rating)::numeric, 1) as avg_rating
            FROM products
            GROUP BY category
            ORDER BY count DESC
        """)).fetchall()
        
        for stat in category_stats:
            print(f"{stat[0]:25s} | Count: {stat[1]:4d} | Avg Price: ${stat[2]:6.2f} | Avg Rating: {stat[3]:.1f}⭐")
        
        # Sample products
        print("\n" + "="*60)
        print("🎯 TOP RATED PRODUCTS")
        print("="*60)
        sample_products = conn.execute(text("""
            SELECT title, category, price, rating 
            FROM products 
            ORDER BY rating DESC
            LIMIT 5
        """)).fetchall()
        
        for i, p in enumerate(sample_products, 1):
            print(f"{i}. {p[0][:40]:40s} | {p[1]:15s} | ${p[2]:6.2f} | {p[3]:.1f}⭐")
        
        # Interaction statistics
        print("\n" + "="*60)
        print("🔄 INTERACTION DISTRIBUTION")
        print("="*60)
        interaction_stats = conn.execute(text("""
            SELECT interaction_type, COUNT(*) as count
            FROM interactions
            GROUP BY interaction_type
            ORDER BY count DESC
        """)).fetchall()
        
        for stat in interaction_stats:
            pct = (stat[1] / interactions_count) * 100
            print(f"{stat[0]:10s}: {stat[1]:6,} ({pct:5.1f}%)")
        
        # User activity
        print("\n" + "="*60)
        print("👥 USER ACTIVITY")
        print("="*60)
        user_stats = conn.execute(text("""
            SELECT 
                MIN(interaction_count) as min_interactions,
                ROUND(AVG(interaction_count)::numeric, 1) as avg_interactions,
                MAX(interaction_count) as max_interactions
            FROM (
                SELECT user_id, COUNT(*) as interaction_count
                FROM interactions
                GROUP BY user_id
            ) user_counts
        """)).fetchone()
        
        print(f"Min interactions per user:  {user_stats[0]}")
        print(f"Avg interactions per user:  {user_stats[1]}")
        print(f"Max interactions per user:  {user_stats[2]}")
        
        # Most popular products
        print("\n" + "="*60)
        print("🔥 MOST POPULAR PRODUCTS (by interactions)")
        print("="*60)
        popular = conn.execute(text("""
            SELECT p.title, p.category, COUNT(*) as interaction_count
            FROM interactions i
            JOIN products p ON i.product_id = p.id
            GROUP BY p.id, p.title, p.category
            ORDER BY interaction_count DESC
            LIMIT 5
        """)).fetchall()
        
        for i, p in enumerate(popular, 1):
            print(f"{i}. {p[0][:40]:40s} | {p[1]:15s} | {p[2]:4d} interactions")

def main():
    """Main function to set up database"""
    print("="*60)
    print("🚀 RECOMMENDATION ENGINE - DATABASE SETUP")
    print("="*60)
    print(f"\n📍 Connecting to NeonDB...")
    print(f"   {DATABASE_URL[:50]}...")
    
    # Create engine
    try:
        engine = create_engine(DATABASE_URL)
        
        # Test connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("   ✅ Connected successfully!")
        
    except Exception as e:
        print(f"\n❌ Connection failed: {e}")
        print("\nPlease check your DATABASE_URL in backend/.env")
        sys.exit(1)
    
    try:
        # Step 1: Create tables
        create_tables(engine)
        
        # Step 2: Load data
        load_csv_data(engine)
        
        # Step 3: Verify
        verify_data(engine)
        
        print("\n" + "="*60)
        print("✅ DATABASE SETUP COMPLETE!")
        print("="*60)
        print("\n🎉 Your recommendation engine database is ready!")
        print("📈 Next: Start the API with 'uvicorn app.main:app --reload'")
        
    except Exception as e:
        print(f"\n❌ Error during setup: {e}")
        raise
    
    finally:
        engine.dispose()

if __name__ == "__main__":
    main()
