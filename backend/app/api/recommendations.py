"""
Recommendation API endpoints with multiple algorithms
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from app.schemas import RecommendationResponse, ProductRecommendation, MetricsResponse
from app.algorithms.content_based import ContentBasedRecommender
from app.algorithms.collaborative import CollaborativeFilteringRecommender

router = APIRouter()

# Initialize recommenders (singleton pattern)
content_recommender = None
collaborative_recommender = None

def get_content_recommender():
    """Get or create content-based recommender instance"""
    global content_recommender
    if content_recommender is None:
        print("🔨 Initializing Content-Based Recommender...")
        content_recommender = ContentBasedRecommender()
        content_recommender.load_products()
        content_recommender.build_tfidf_matrix()
    return content_recommender

def get_collaborative_recommender():
    """Get or create collaborative filtering recommender instance"""
    global collaborative_recommender
    if collaborative_recommender is None:
        print("🔨 Initializing Collaborative Filtering Recommender...")
        collaborative_recommender = CollaborativeFilteringRecommender()
        collaborative_recommender.build_user_item_matrix()
        collaborative_recommender.calculate_user_similarity()
    return collaborative_recommender

@router.get("/similar/{product_id}", response_model=RecommendationResponse)
async def get_similar_products(
    product_id: int,
    limit: int = Query(default=10, ge=1, le=50, description="Number of recommendations")
):
    """
    Get products similar to the given product
    Uses content-based filtering
    """
    try:
        rec = get_content_recommender()
        similar = rec.get_similar_products(product_id, n=limit)
        
        if not similar:
            raise HTTPException(
                status_code=404,
                detail=f"No similar products found for product_id {product_id}"
            )
        
        return RecommendationResponse(
            product_id=product_id,
            algorithm="content_based",
            recommendations=[ProductRecommendation(**item) for item in similar],
            count=len(similar)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/for-user/{user_id}", response_model=RecommendationResponse)
async def get_user_recommendations(
    user_id: int,
    limit: int = Query(default=10, ge=1, le=50, description="Number of recommendations"),
    algorithm: str = Query(default="hybrid", description="Algorithm: content, collaborative, or hybrid")
):
    """
    Get personalized recommendations for a user
    
    Algorithms:
    - content: Based on user's past interactions (content similarity)
    - collaborative: Based on similar users' preferences
    - hybrid: Combines both (default)
    """
    try:
        if algorithm == "content":
            # Content-based recommendations
            rec = get_content_recommender()
            recommendations = rec.get_recommendations_for_user(user_id, n=limit)
            algo_name = "content_based"
            
        elif algorithm == "collaborative":
            # Collaborative filtering recommendations
            rec = get_collaborative_recommender()
            recommendations = rec.get_recommendations(user_id, n=limit)
            algo_name = "collaborative_filtering"
            
        else:  # hybrid (default)
            # Get recommendations from both algorithms
            content_rec = get_content_recommender()
            collab_rec = get_collaborative_recommender()
            
            content_recs = content_rec.get_recommendations_for_user(user_id, n=limit * 2)
            collab_recs = collab_rec.get_recommendations(user_id, n=limit * 2)
            
            # Combine and deduplicate
            recommendations = _combine_recommendations(content_recs, collab_recs, limit)
            algo_name = "hybrid"
        
        if not recommendations:
            # Fallback to popular products
            rec = get_content_recommender()
            recommendations = rec.get_popular_products(n=limit)
        
        # Format recommendations
        formatted_recs = []
        for item in recommendations:
            formatted_recs.append(ProductRecommendation(
                product_id=item.get('product_id', item.get('id')),
                title=item.get('title'),
                category=item.get('category'),
                price=item.get('price'),
                rating=item.get('rating'),
                similarity_score=item.get('similarity_score') or item.get('recommendation_score'),
                image_url=item.get('image_url', f"https://picsum.photos/seed/{item.get('product_id', 0)}/400/400")
            ))
        
        return RecommendationResponse(
            user_id=user_id,
            algorithm=algo_name,
            recommendations=formatted_recs,
            count=len(formatted_recs)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/popular", response_model=RecommendationResponse)
async def get_popular_products(
    limit: int = Query(default=10, ge=1, le=50, description="Number of products")
):
    """
    Get popular products (most interacted with)
    Good for homepage or cold start
    """
    try:
        rec = get_content_recommender()
        popular = rec.get_popular_products(n=limit)
        
        formatted_recs = []
        for item in popular:
            formatted_recs.append(ProductRecommendation(
                product_id=item.get('product_id', item.get('id')),
                title=item.get('title'),
                category=item.get('category'),
                price=item.get('price'),
                rating=item.get('rating'),
                similarity_score=None,
                image_url=f"https://picsum.photos/seed/{item.get('product_id', 0)}/400/400"
            ))
        
        return RecommendationResponse(
            algorithm="popularity_based",
            recommendations=formatted_recs,
            count=len(formatted_recs)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/metrics", response_model=MetricsResponse)
async def get_recommendation_metrics(
    algorithm: str = Query(default="content", description="Algorithm: content or collaborative")
):
    """
    Get recommendation algorithm performance metrics
    """
    try:
        if algorithm == "collaborative":
            rec = get_collaborative_recommender()
        else:
            rec = get_content_recommender()
        
        metrics = rec.get_metrics()
        
        return MetricsResponse(**metrics)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def _combine_recommendations(content_recs, collab_recs, limit):
    """
    Combine recommendations from both algorithms
    Weight: 60% collaborative, 40% content-based
    """
    # Create dictionaries by product_id
    content_dict = {
        rec.get('product_id', rec.get('id')): rec 
        for rec in content_recs
    }
    collab_dict = {
        rec.get('product_id', rec.get('id')): rec 
        for rec in collab_recs
    }
    
    # Calculate hybrid scores
    hybrid_scores = {}
    
    # Add collaborative recommendations (higher weight)
    for product_id, rec in collab_dict.items():
        score = (rec.get('recommendation_score') or 0) * 0.6
        hybrid_scores[product_id] = {
            'score': score,
            'data': rec
        }
    
    # Add content recommendations (lower weight)
    for product_id, rec in content_dict.items():
        score = (rec.get('similarity_score') or 0) * 0.4
        if product_id in hybrid_scores:
            hybrid_scores[product_id]['score'] += score
        else:
            hybrid_scores[product_id] = {
                'score': score,
                'data': rec
            }
    
    # Sort by hybrid score
    sorted_recs = sorted(
        hybrid_scores.items(),
        key=lambda x: x[1]['score'],
        reverse=True
    )[:limit]
    
    # Return formatted recommendations
    return [item[1]['data'] for item in sorted_recs]
