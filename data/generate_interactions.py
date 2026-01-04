"""
Generate diverse, realistic user interactions
This creates distinct user profiles with different preferences
"""

import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv
import random
from datetime import datetime, timedelta

# Load .env from backend folder
env_path = os.path.join(os.path.dirname(__file__), '..', 'backend', '.env')
load_dotenv(env_path)
DATABASE_URL = os.getenv('DATABASE_URL')

if not DATABASE_URL:
    raise ValueError("DATABASE_URL not found. Check backend/.env file.")

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)

print("="*60)
print("🎯 GENERATING DIVERSE USER INTERACTIONS")
print("="*60)

# Load existing data
print("\n📊 Loading existing data...")
products_df = pd.read_sql("SELECT id, category, price FROM products", engine)
users_df = pd.read_sql("SELECT id FROM users", engine)

print(f"   Products: {len(products_df)}")
print(f"   Users: {len(users_df)}")

# Define user personas (different shopping behaviors)
PERSONAS = {
    'tech_enthusiast': {
        'categories': ['Electronics'],
        'price_range': (50, 500),
        'interaction_count': (20, 40)
    },
    'bookworm': {
        'categories': ['Books'],
        'price_range': (10, 50),
        'interaction_count': (15, 35)
    },
    'fashion_lover': {
        'categories': ['Clothing'],
        'price_range': (20, 200),
        'interaction_count': (25, 50)
    },
    'home_decorator': {
        'categories': ['Home & Kitchen'],
        'price_range': (15, 300),
        'interaction_count': (15, 30)
    },
    'fitness_fan': {
        'categories': ['Sports & Outdoors'],
        'price_range': (20, 150),
        'interaction_count': (10, 25)
    },
    'variety_shopper': {
        'categories': ['Electronics', 'Books', 'Clothing', 'Home & Kitchen'],
        'price_range': (10, 300),
        'interaction_count': (30, 60)
    },
    'casual_browser': {
        'categories': ['Electronics', 'Books', 'Clothing'],
        'price_range': (10, 100),
        'interaction_count': (5, 15)
    }
}

# Assign persona to each user
def assign_personas(users):
    """Assign a shopping persona to each user"""
    persona_names = list(PERSONAS.keys())
    user_personas = {}
    
    for user_id in users['id'].values:
        # Distribute personas somewhat evenly
        persona = random.choice(persona_names)
        user_personas[user_id] = persona
    
    return user_personas

print("\n👥 Assigning user personas...")
user_personas = assign_personas(users_df)

# Count persona distribution
persona_counts = {}
for persona in user_personas.values():
    persona_counts[persona] = persona_counts.get(persona, 0) + 1

print("\n📊 Persona Distribution:")
for persona, count in sorted(persona_counts.items(), key=lambda x: x[1], reverse=True):
    print(f"   {persona}: {count} users")

# Generate interactions based on personas
def generate_interactions_for_user(user_id, persona_name, products_df):
    """Generate realistic interactions for a user based on their persona"""
    persona = PERSONAS[persona_name]
    interactions = []
    
    # Filter products by user's preferred categories
    preferred_products = products_df[
        (products_df['category'].isin(persona['categories'])) &
        (products_df['price'] >= persona['price_range'][0]) &
        (products_df['price'] <= persona['price_range'][1])
    ]
    
    if len(preferred_products) == 0:
        # Fallback to any products in preferred categories
        preferred_products = products_df[products_df['category'].isin(persona['categories'])]
    
    if len(preferred_products) == 0:
        # Ultimate fallback
        preferred_products = products_df
    
    # Number of interactions for this user
    num_interactions = random.randint(*persona['interaction_count'])
    
    # Select products (with some repetition for realistic behavior)
    num_unique_products = min(len(preferred_products), max(5, num_interactions // 3))
    favorite_products = preferred_products.sample(n=num_unique_products)
    
    for _ in range(num_interactions):
        # 70% chance to interact with favorite products, 30% explore others
        if random.random() < 0.7 and len(favorite_products) > 0:
            product = favorite_products.sample(n=1).iloc[0]
        else:
            product = preferred_products.sample(n=1).iloc[0]
        
        # Determine interaction type
        # Most are views, some purchases, fewer ratings
        rand = random.random()
        if rand < 0.65:
            interaction_type = 'view'
            rating = None
        elif rand < 0.85:
            interaction_type = 'purchase'
            rating = None
        else:
            interaction_type = 'rating'
            # Users with specific personas give different ratings
            if persona_name in ['tech_enthusiast', 'bookworm']:
                rating = random.choice([4, 5, 5])  # More critical
            else:
                rating = random.choice([3, 4, 4, 5])  # More generous
        
        # Random timestamp in last 90 days
        timestamp = datetime.now() - timedelta(days=random.randint(0, 90))
        
        interactions.append({
            'user_id': int(user_id),
            'product_id': int(product['id']),
            'interaction_type': interaction_type,
            'rating': rating,
            'timestamp': timestamp
        })
    
    return interactions

print("\n🔨 Generating interactions...")

# Clear existing interactions (optional - comment out if you want to keep them)
print("   Clearing old interactions...")
with engine.connect() as conn:
    conn.execute(text("DELETE FROM interactions"))
    conn.commit()

all_interactions = []

for i, (user_id, persona) in enumerate(user_personas.items(), 1):
    if i % 50 == 0:
        print(f"   Processing user {i}/{len(user_personas)}...")
    
    user_interactions = generate_interactions_for_user(user_id, persona, products_df)
    all_interactions.extend(user_interactions)

print(f"\n✅ Generated {len(all_interactions)} interactions")

# Save to database
print("\n💾 Saving to database...")
interactions_df = pd.DataFrame(all_interactions)
interactions_df.to_sql('interactions', engine, if_exists='append', index=False)

print("\n✅ DONE!")

# Verify the results
print("\n" + "="*60)
print("📊 VERIFICATION")
print("="*60)

with engine.connect() as conn:
    # Total interactions
    total = conn.execute(text("SELECT COUNT(*) FROM interactions")).scalar()
    print(f"\nTotal interactions: {total}")
    
    # Interactions by type
    print("\nInteractions by type:")
    result = conn.execute(text("""
        SELECT interaction_type, COUNT(*) as count
        FROM interactions
        GROUP BY interaction_type
        ORDER BY count DESC
    """))
    for row in result:
        pct = (row[1] / total) * 100
        print(f"   {row[0]}: {row[1]} ({pct:.1f}%)")
    
    # Sample user stats
    print("\nSample user statistics:")
    result = conn.execute(text("""
        SELECT user_id, COUNT(*) as interactions, COUNT(DISTINCT product_id) as unique_products
        FROM interactions
        GROUP BY user_id
        ORDER BY RANDOM()
        LIMIT 10
    """))
    for row in result:
        print(f"   User {row[0]}: {row[1]} interactions, {row[2]} unique products")
    
    # Average stats
    result = conn.execute(text("""
        SELECT 
            AVG(interaction_count) as avg_interactions,
            AVG(unique_products) as avg_unique_products
        FROM (
            SELECT user_id, 
                   COUNT(*) as interaction_count,
                   COUNT(DISTINCT product_id) as unique_products
            FROM interactions
            GROUP BY user_id
        ) stats
    """))
    row = result.fetchone()
    print(f"\nAverage per user:")
    print(f"   Interactions: {row[0]:.1f}")
    print(f"   Unique products: {row[1]:.1f}")

print("\n" + "="*60)
print("✅ Data generation complete!")
print("="*60)
print("\n🎯 Next steps:")
print("   1. Restart your backend server")
print("   2. Test different users in the dashboard")
print("   3. Recommendations should now be diverse!")
