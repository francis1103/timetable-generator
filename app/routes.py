"""
API Routes Module

This module defines all API endpoints for the FastAPI application.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from app.model import predict


# Create router
router = APIRouter()


# Request model
class PredictionRequest(BaseModel):
    """
    Request model for prediction endpoint.
    
    Attributes:
        text (str): The input text for prediction
    """
    text: str = Field(..., description="Input text for prediction", min_length=1)
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "This is a sample input text for prediction"
            }
        }


# Response model
class PredictionResponse(BaseModel):
    """
    Response model for prediction endpoint.
    
    Attributes:
        prediction (str): The prediction result
    """
    prediction: str = Field(..., description="The prediction result")
    
    class Config:
        json_schema_extra = {
            "example": {
                "prediction": "Mock prediction for input: 'This is a sample input text for prediction'"
            }
        }


@router.get("/")
async def root():
    """
    Root endpoint - health check.
    
    Returns:
        dict: Welcome message and API status
    """
    return {
        "message": "FastAPI ML Backend",
        "status": "running",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@router.post("/predict", response_model=PredictionResponse)
async def predict_endpoint(request: PredictionRequest):
    """
    Prediction endpoint.
    
    Accepts POST requests with JSON body containing text input,
    processes it through the ML model, and returns the prediction.
    
    Args:
        request (PredictionRequest): The request body containing input text
        
    Returns:
        PredictionResponse: The prediction result
        
    Raises:
        HTTPException: If prediction fails
    """
    try:
        # Get input text from request
        input_text = request.text
        
        # Call the prediction function from model.py
        prediction_result = predict(input_text)
        
        # Return the prediction response
        return PredictionResponse(prediction=prediction_result)
        
    except Exception as e:
        # Handle any errors during prediction
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        dict: Health status of the API
    """
    return {
        "status": "healthy",
        "service": "FastAPI ML Backend"
    }
