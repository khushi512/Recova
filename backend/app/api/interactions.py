"""
User interaction tracking API endpoints
"""

from fastapi import APIRouter, HTTPException
from sqlalchemy import create_engine, text
from datetime import datetime
import os
from dotenv import load_dotenv

from app.schemas import InteractionCreate, Interaction

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')

# Handle postgres:// vs postgresql://
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)

router = APIRouter()

@router.post("/", response_model=Interaction, status_code=201)
async def track_interaction(interaction: InteractionCreate):
    """
    Track a user interaction (view, purchase, rating)
    This helps improve recommendations over time
    """
    try:
        # Validate interaction type
        valid_types = ['view', 'purchase', 'rating', 'wishlist']
        if interaction.interaction_type not in valid_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid interaction_type. Must be one of: {valid_types}"
            )
        
        # Validate rating if type is 'rating'
        if interaction.interaction_type == 'rating':
            if interaction.rating is None:
                raise HTTPException(
                    status_code=400,
                    detail="Rating is required when interaction_type is 'rating'"
                )
            if not (1 <= interaction.rating <= 5):
                raise HTTPException(
                    status_code=400,
                    detail="Rating must be between 1 and 5"
                )
        
        # Insert interaction
        query = text("""
            INSERT INTO interactions (user_id, product_id, interaction_type, rating, timestamp)
            VALUES (:user_id, :product_id, :interaction_type, :rating, :timestamp)
            RETURNING id, user_id, product_id, interaction_type, rating, timestamp
        """)
        
        params = {
            'user_id': interaction.user_id,
            'product_id': interaction.product_id,
            'interaction_type': interaction.interaction_type,
            'rating': interaction.rating,
            'timestamp': datetime.now()
        }
        
        with engine.connect() as conn:
            result = conn.execute(query, params)
            conn.commit()
            row = result.fetchone()
        
        if not row:
            raise HTTPException(status_code=500, detail="Failed to create interaction")
        
        return Interaction(
            id=row[0],
            user_id=row[1],
            product_id=row[2],
            interaction_type=row[3],
            rating=row[4],
            timestamp=row[5]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/user/{user_id}")
async def get_user_interactions(
    user_id: int,
    limit: int = 50
):
    """
    Get recent interactions for a user
    """
    try:
        query = text("""
            SELECT i.id, i.user_id, i.product_id, i.interaction_type, i.rating, i.timestamp,
                   p.title, p.category, p.price
            FROM interactions i
            JOIN products p ON i.product_id = p.id
            WHERE i.user_id = :user_id
            ORDER BY i.timestamp DESC
            LIMIT :limit
        """)
        
        with engine.connect() as conn:
            result = conn.execute(query, {'user_id': user_id, 'limit': limit}).fetchall()
        
        interactions = [
            {
                'id': row[0],
                'user_id': row[1],
                'product_id': row[2],
                'interaction_type': row[3],
                'rating': row[4],
                'timestamp': row[5],
                'product_title': row[6],
                'product_category': row[7],
                'product_price': float(row[8])
            }
            for row in result
        ]
        
        return {
            'user_id': user_id,
            'interactions': interactions,
            'count': len(interactions)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
