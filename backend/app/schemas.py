"""
Pydantic schemas for API request/response validation
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime

# Product schemas
class ProductBase(BaseModel):
    title: str
    category: str
    price: float
    description: Optional[str] = None
    image_url: Optional[str] = None
    rating: Optional[float] = None
    review_count: Optional[int] = 0

class Product(ProductBase):
    id: int
    created_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)

class ProductRecommendation(BaseModel):
    """Product with recommendation score"""
    product_id: int
    title: str
    category: str
    price: float
    rating: Optional[float] = None
    similarity_score: Optional[float] = None
    image_url: Optional[str] = None

# User schemas
class UserBase(BaseModel):
    username: str

class User(UserBase):
    id: int
    created_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)

# Interaction schemas
class InteractionCreate(BaseModel):
    user_id: int
    product_id: int
    interaction_type: str = Field(..., pattern="^(view|purchase|rating|wishlist)$")
    rating: Optional[int] = Field(None, ge=1, le=5)

class Interaction(InteractionCreate):
    id: int
    timestamp: datetime
    
    model_config = ConfigDict(from_attributes=True)

# Recommendation response schemas
class RecommendationResponse(BaseModel):
    user_id: Optional[int] = None
    product_id: Optional[int] = None
    algorithm: str
    recommendations: List[ProductRecommendation]
    count: int

class SearchResponse(BaseModel):
    products: List[Product]
    total: int
    page: int
    page_size: int

# Metrics schema
class MetricsResponse(BaseModel):
    algorithm: str
    total_products: int
    coverage: float
    avg_similarity_score: Optional[float] = None
    tfidf_features: Optional[int] = None
