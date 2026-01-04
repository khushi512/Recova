"""
Products API endpoints
"""

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import create_engine, text
from typing import Optional
import os
from dotenv import load_dotenv
import pandas as pd

from app.schemas import Product, SearchResponse

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')

# Handle postgres:// vs postgresql://
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)

router = APIRouter()

@router.get("/", response_model=SearchResponse)
async def get_products(
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=20, ge=1, le=100, description="Items per page"),
    category: Optional[str] = Query(default=None, description="Filter by category"),
    search: Optional[str] = Query(default=None, description="Search in title"),
    min_price: Optional[float] = Query(default=None, ge=0, description="Minimum price"),
    max_price: Optional[float] = Query(default=None, ge=0, description="Maximum price"),
    min_rating: Optional[float] = Query(default=None, ge=0, le=5, description="Minimum rating")
):
    """
    Get paginated list of products with filters
    """
    try:
        # Build query
        conditions = []
        params = {}
        
        if category:
            conditions.append("category = :category")
            params['category'] = category
        
        if search:
            conditions.append("title ILIKE :search")
            params['search'] = f"%{search}%"
        
        if min_price is not None:
            conditions.append("price >= :min_price")
            params['min_price'] = min_price
        
        if max_price is not None:
            conditions.append("price <= :max_price")
            params['max_price'] = max_price
        
        if min_rating is not None:
            conditions.append("rating >= :min_rating")
            params['min_rating'] = min_rating
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        # Count total
        count_query = f"SELECT COUNT(*) FROM products WHERE {where_clause}"
        
        with engine.connect() as conn:
            total = conn.execute(text(count_query), params).scalar()
        
        # Get paginated results
        offset = (page - 1) * page_size
        params['limit'] = page_size
        params['offset'] = offset
        
        data_query = f"""
            SELECT id, title, category, price, description, image_url, rating, review_count, created_at
            FROM products
            WHERE {where_clause}
            ORDER BY rating DESC, review_count DESC
            LIMIT :limit OFFSET :offset
        """
        
        products_df = pd.read_sql(text(data_query), engine, params=params)
        products = products_df.to_dict('records')
        
        return SearchResponse(
            products=[Product(**p) for p in products],
            total=total,
            page=page,
            page_size=page_size
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/categories/list")
async def get_categories():
    """
    Get list of all product categories
    """
    try:
        query = text("""
            SELECT category, COUNT(*) as count
            FROM products
            GROUP BY category
            ORDER BY count DESC
        """)
        
        with engine.connect() as conn:
            result = conn.execute(query).fetchall()
        
        categories = [
            {"category": row[0], "count": row[1]}
            for row in result
        ]
        
        return {"categories": categories}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{product_id}", response_model=Product)
async def get_product(product_id: int):
    """
    Get a single product by ID
    """
    try:
        query = text("""
            SELECT id, title, category, price, description, image_url, rating, review_count, created_at
            FROM products
            WHERE id = :product_id
        """)
        
        with engine.connect() as conn:
            result = conn.execute(query, {'product_id': product_id}).fetchone()
        
        if not result:
            raise HTTPException(status_code=404, detail=f"Product {product_id} not found")
        
        product_dict = dict(result._mapping)
        
        return Product(**product_dict)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
