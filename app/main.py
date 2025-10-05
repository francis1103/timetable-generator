"""
FastAPI Application Entry Point

This is the main application file that initializes FastAPI,
configures middleware, and includes all routes.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import router


# Create FastAPI application instance
app = FastAPI(
    title="FastAPI ML Backend",
    description="A FastAPI backend for machine learning model predictions",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)


# Configure CORS middleware
# This allows your frontend (running on a different port) to make requests to this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React default port
        "http://localhost:5173",  # Vite default port
        "http://localhost:8080",  # Vue default port
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8080",
        # Add your frontend URL here
    ],
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allows all headers
)


# Include routers
app.include_router(router, tags=["API Endpoints"])


# Optional: Add startup event
@app.on_event("startup")
async def startup_event():
    """
    Execute code when the application starts.
    Use this to load ML models, initialize database connections, etc.
    """
    print("🚀 FastAPI application is starting up...")
    print("📊 Loading ML model (if applicable)...")
    # Add model loading logic here when ready
    # Example: global model
    # model = load_model('path/to/model.h5')
    print("✅ Application startup complete!")


# Optional: Add shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """
    Execute code when the application shuts down.
    Use this to clean up resources, close connections, etc.
    """
    print("🛑 FastAPI application is shutting down...")
    print("✅ Cleanup complete!")


# For direct execution (not recommended for production)
if __name__ == "__main__":
    import uvicorn
    
    # Run the application
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True  # Enable auto-reload during development
    )
