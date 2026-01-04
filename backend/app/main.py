"""
Main FastAPI application for Recommendation Engine
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import recommendations, products, interactions

# Create FastAPI app
app = FastAPI(
    title="E-Commerce Recommendation API",
    description="AI-powered product recommendation system",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers with prefix
app.include_router(recommendations.router, prefix="/api/recommendations", tags=["recommendations"])
app.include_router(products.router, prefix="/api/products", tags=["products"])
app.include_router(interactions.router, prefix="/api/interactions", tags=["interactions"])

@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "message": "E-Commerce Recommendation API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "recommendations": {
                "similar_products": "/api/recommendations/similar/{product_id}",
                "user_recommendations": "/api/recommendations/for-user/{user_id}",
                "popular_products": "/api/recommendations/popular",
                "metrics": "/api/recommendations/metrics"
            },
            "products": {
                "list": "/api/products",
                "detail": "/api/products/{product_id}",
                "categories": "/api/products/categories/list"
            },
            "interactions": {
                "track": "/api/interactions",
                "user_history": "/api/interactions/user/{user_id}"
            }
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
