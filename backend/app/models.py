from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, Index, Numeric
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False, index=True)
    category = Column(String(100), nullable=False, index=True)
    price = Column(Numeric(10, 2), nullable=False)
    description = Column(Text)
    image_url = Column(String(500))
    rating = Column(Numeric(3, 2))
    review_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    interactions = relationship("Interaction", back_populates="product")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    interactions = relationship("Interaction", back_populates="user")

class Interaction(Base):
    __tablename__ = "interactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"))
    interaction_type = Column(String(20), nullable=False)  # 'view', 'purchase', 'rating'
    rating = Column(Integer, nullable=True)  # 1-5
    timestamp = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="interactions")
    product = relationship("Product", back_populates="interactions")

class CachedRecommendation(Base):
    __tablename__ = "cached_recommendations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"))
    algorithm = Column(String(50), nullable=False)  # 'collaborative', 'content', 'popular'
    score = Column(Numeric(5, 4))
    computed_at = Column(DateTime, default=datetime.utcnow)
