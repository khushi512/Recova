import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os

# Configuration
NUM_PRODUCTS = 1000
NUM_USERS = 500
NUM_INTERACTIONS = 10000
OUTPUT_DIR = "."

# Product categories (Amazon-like)
CATEGORIES = [
    'Electronics', 'Books', 'Clothing', 'Home & Kitchen', 
    'Sports & Outdoors', 'Toys & Games', 'Beauty & Personal Care',
    'Health & Household', 'Automotive', 'Tools & Home Improvement'
]

# Sample product titles by category
PRODUCT_TEMPLATES = {
    'Electronics': [
        '{Brand} Wireless Headphones',
        '{Brand} Smart Watch Series {Num}',
        '{Brand} Bluetooth Speaker Pro',
        '{Brand} USB-C Fast Charger',
        '{Brand} Phone Case Premium',
        '{Brand} Laptop Stand Adjustable',
        '{Brand} Wireless Mouse',
        '{Brand} Mechanical Keyboard RGB'
    ],
    'Books': [
        'The {Adjective} {Noun}',
        '{Adjective} Guide to {Topic}',
        'Learning {Topic}: Complete Guide',
        '{Topic} for Beginners',
        'Mastering {Topic} in 30 Days'
    ],
    'Clothing': [
        '{Brand} {Type} T-Shirt',
        '{Brand} {Type} Jeans Slim Fit',
        '{Brand} {Type} Jacket Winter',
        '{Brand} Running Shoes Athletic',
        '{Brand} Casual Sneakers'
    ],
    'Home & Kitchen': [
        '{Brand} Coffee Maker Automatic',
        '{Brand} Blender High Speed',
        '{Brand} Non-Stick Pan Set',
        '{Brand} Knife Set Professional',
        '{Brand} Air Fryer Digital'
    ]
}

BRANDS = ['TechPro', 'SmartLife', 'HomeEssentials', 'StyleMax', 'FitGear', 
          'BookWorm', 'EliteChoice', 'PremiumPlus', 'ValueBrand', 'QualityFirst',
          'ProGear', 'SmartHome', 'LifeStyle', 'TechZone', 'MasterChef']

ADJECTIVES = ['Ultimate', 'Essential', 'Complete', 'Advanced', 'Practical', 
              'Modern', 'Classic', 'Professional', 'Premium', 'Expert']
NOUNS = ['Journey', 'Adventure', 'Story', 'Mystery', 'Guide', 'Path', 'Way']
TOPICS = ['Python', 'Cooking', 'Photography', 'Fitness', 'Meditation', 
          'Leadership', 'Design', 'Marketing', 'Finance', 'Health']
TYPES = ['Cotton', 'Premium', 'Classic', 'Vintage', 'Athletic', 'Casual', 'Formal']

def generate_product_title(category):
    """Generate realistic product title based on category"""
    if category in PRODUCT_TEMPLATES:
        template = random.choice(PRODUCT_TEMPLATES[category])
        return template.format(
            Brand=random.choice(BRANDS),
            Adjective=random.choice(ADJECTIVES),
            Noun=random.choice(NOUNS),
            Topic=random.choice(TOPICS),
            Type=random.choice(TYPES),
            Num=random.randint(1, 10)
        )
    else:
        return f"{random.choice(BRANDS)} {category} Product"

def generate_description(title, category):
    """Generate product description"""
    descriptions = [
        f"High-quality {category.lower()} item with premium features. Perfect for everyday use and built to last.",
        f"Premium {title.lower()} featuring advanced technology and excellent durability. Trusted by thousands.",
        f"Best-selling {category.lower()} product with 5-star reviews. Great value for money.",
        f"Professional-grade {title.lower()} designed for home and office use. Easy to use and reliable.",
        f"Top-rated {category.lower()} item with outstanding performance. Highly recommended by customers."
    ]
    return random.choice(descriptions)

def generate_products(n=NUM_PRODUCTS):
    """Generate synthetic product data"""
    products = []
    
    for i in range(n):
        category = random.choice(CATEGORIES)
        title = generate_product_title(category)
        
        product = {
            'id': i + 1,
            'title': title,
            'category': category,
            'price': round(random.uniform(9.99, 499.99), 2),
            'description': generate_description(title, category),
            'image_url': f'https://picsum.photos/seed/{i}/400/400',
            'rating': round(random.uniform(3.5, 5.0), 1),
            'review_count': random.randint(10, 5000),
            'created_at': datetime.now() - timedelta(days=random.randint(0, 365))
        }
        products.append(product)
    
    return pd.DataFrame(products)

def generate_users(n=NUM_USERS):
    """Generate synthetic user data"""
    users = []
    
    for i in range(n):
        user = {
            'id': i + 1,
            'username': f'user_{i+1:04d}',
            'created_at': datetime.now() - timedelta(days=random.randint(0, 730))
        }
        users.append(user)
    
    return pd.DataFrame(users)

def generate_interactions(users_df, products_df, n=NUM_INTERACTIONS):
    """Generate synthetic user-product interactions with realistic patterns"""
    interactions = []
    interaction_types = ['view', 'purchase', 'rating']
    
    # Create power-law distributions (realistic: few users very active, most casual)
    user_activity = np.random.zipf(1.5, len(users_df))
    product_popularity = np.random.zipf(1.5, len(products_df))
    
    # Normalize to probabilities
    user_probs = user_activity / user_activity.sum()
    product_probs = product_popularity / product_popularity.sum()
    
    for i in range(n):
        # Choose user (biased towards active users)
        user_id = np.random.choice(users_df['id'], p=user_probs)
        
        # Choose product (biased towards popular products)
        product_id = np.random.choice(products_df['id'], p=product_probs)
        
        # Choose interaction type (views most common, then purchases, then ratings)
        interaction_type = np.random.choice(
            interaction_types, 
            p=[0.70, 0.20, 0.10]
        )
        
        # Generate rating (if type is rating)
        # Higher-rated products get more positive ratings
        product_avg_rating = products_df[products_df['id'] == product_id]['rating'].values[0]
        if interaction_type == 'rating':
            # Bias towards product's average rating
            rating_choices = [3, 4, 5] if product_avg_rating >= 4.0 else [2, 3, 4, 5]
            rating = random.choice(rating_choices)
        else:
            rating = None
        
        interaction = {
            'id': i + 1,
            'user_id': int(user_id),
            'product_id': int(product_id),
            'interaction_type': interaction_type,
            'rating': rating,
            'timestamp': datetime.now() - timedelta(days=random.randint(0, 90))
        }
        interactions.append(interaction)
    
    return pd.DataFrame(interactions)

def main():
    """Generate all datasets and save to CSV"""
    print("="*60)
    print("🚀 Generating Synthetic Amazon-like Dataset")
    print("="*60)
    
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    # Generate data
    print(f"\n📦 Generating {NUM_PRODUCTS} products...")
    products_df = generate_products(NUM_PRODUCTS)
    
    print(f"👥 Generating {NUM_USERS} users...")
    users_df = generate_users(NUM_USERS)
    
    print(f"🔄 Generating {NUM_INTERACTIONS} interactions...")
    interactions_df = generate_interactions(users_df, products_df, NUM_INTERACTIONS)
    
    # Save to CSV
    print(f"\n💾 Saving to CSV files in {os.path.abspath(OUTPUT_DIR)}...")
    products_df.to_csv(os.path.join(OUTPUT_DIR, 'products.csv'), index=False)
    users_df.to_csv(os.path.join(OUTPUT_DIR, 'users.csv'), index=False)
    interactions_df.to_csv(os.path.join(OUTPUT_DIR, 'interactions.csv'), index=False)
    
    print("\n✅ Data generation complete!")
    print(f"\n📁 Files saved:")
    print(f"   - products.csv ({len(products_df)} rows)")
    print(f"   - users.csv ({len(users_df)} rows)")
    print(f"   - interactions.csv ({len(interactions_df)} rows)")

if __name__ == "__main__":
    main()
