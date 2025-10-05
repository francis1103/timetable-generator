# FastAPI ML Backend

A complete FastAPI backend for machine learning model predictions with a modular structure designed for easy ML model integration.

## 📁 Project Structure

```
backend/
│
├─ app/
│   ├─ __init__.py      # Package initializer
│   ├─ main.py          # FastAPI application entry point
│   ├─ routes.py        # API endpoints
│   ├─ model.py         # ML model integration (currently mock)
│   └─ utils.py         # Helper functions
│
├─ requirements.txt     # Python dependencies
├─ .gitignore          # Git ignore rules
└─ README.md           # This file
```

## ✨ Features

- **FastAPI Framework**: Modern, fast web framework for building APIs
- **CORS Middleware**: Pre-configured for frontend integration
- **Mock ML Model**: Ready-to-replace placeholder for your ML model
- **RESTful API**: Clean `/predict` endpoint for predictions
- **Auto-generated Docs**: Interactive API documentation with Swagger UI
- **Modular Design**: Easy to extend and maintain
- **Type Safety**: Pydantic models for request/response validation

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. **Navigate to the backend directory**:
   ```powershell
   cd c:\Users\franc\Downloads\backend
   ```

2. **Create a virtual environment** (recommended):
   ```powershell
   python -m venv venv
   ```

3. **Activate the virtual environment**:
   ```powershell
   # On Windows PowerShell
   .\venv\Scripts\Activate.ps1
   
   # If you get an execution policy error, run:
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

4. **Install dependencies**:
   ```powershell
   pip install -r requirements.txt
   ```

### Running the Server

**Start the development server**:
```powershell
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The server will start at `http://127.0.0.1:8000`

**Alternative method** (using Python directly):
```powershell
python -m uvicorn app.main:app --reload
```

You should see output like:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
🚀 FastAPI application is starting up...
📊 Loading ML model (if applicable)...
✅ Application startup complete!
INFO:     Application startup complete.
```

## 📚 API Documentation

Once the server is running, you can access:

- **Swagger UI (Interactive Docs)**: http://127.0.0.1:8000/docs
- **ReDoc (Alternative Docs)**: http://127.0.0.1:8000/redoc
- **OpenAPI Schema**: http://127.0.0.1:8000/openapi.json

## 🔌 API Endpoints

### 1. Root Endpoint
**GET** `/`

Returns API status and welcome message.

**Response**:
```json
{
  "message": "FastAPI ML Backend",
  "status": "running",
  "docs": "/docs",
  "redoc": "/redoc"
}
```

### 2. Predict Endpoint
**POST** `/predict`

Make predictions using the ML model.

**Request Body**:
```json
{
  "text": "Your input text here"
}
```

**Response**:
```json
{
  "prediction": "Mock prediction for input: 'Your input text here'"
}
```

### 3. Health Check
**GET** `/health`

Check if the API is healthy and running.

**Response**:
```json
{
  "status": "healthy",
  "service": "FastAPI ML Backend"
}
```

## 🧪 Testing the API

### Using Swagger UI (Recommended for Beginners)

1. Open your browser and go to: http://127.0.0.1:8000/docs
2. Find the **POST /predict** endpoint
3. Click "Try it out"
4. Enter your test data in the request body:
   ```json
   {
     "text": "This is a test input"
   }
   ```
5. Click "Execute"
6. View the response below

### Using PowerShell (curl)

```powershell
$body = @{
    text = "This is a test input"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://127.0.0.1:8000/predict" -Method Post -Body $body -ContentType "application/json"
```

### Using Python

```python
import requests

url = "http://127.0.0.1:8000/predict"
data = {"text": "This is a test input"}

response = requests.post(url, json=data)
print(response.json())
```

## 🤖 Integrating Your ML Model

The backend is designed to make ML model integration simple. Follow these steps:

### Step 1: Prepare Your Model

Train and save your ML model (e.g., `.pkl`, `.h5`, `.pt` file).

### Step 2: Update `app/model.py`

Replace the mock `predict()` function with your actual model logic:

```python
import pickle  # or tensorflow, torch, etc.

# Load your model (do this once, preferably at startup)
MODEL_PATH = "path/to/your/model.pkl"
model = None

def load_model(model_path: str):
    """Load the trained ML model."""
    global model
    with open(model_path, 'rb') as f:
        model = pickle.load(f)
    return model

def predict(input_data: str) -> str:
    """Make prediction using the loaded model."""
    global model
    
    # Preprocess input
    processed_input = preprocess(input_data)
    
    # Make prediction
    prediction = model.predict(processed_input)
    
    # Postprocess and return
    result = postprocess(prediction)
    return result
```

### Step 3: Load Model at Startup

Update `app/main.py` startup event:

```python
@app.on_event("startup")
async def startup_event():
    from app.model import load_model
    load_model("path/to/your/model.pkl")
    print("✅ Model loaded successfully!")
```

### Step 4: Test Your Integration

Restart the server and test with real data through the `/predict` endpoint.

## 🔧 Configuration

### Modify CORS Settings

Edit `app/main.py` to add/modify allowed origins:

```python
allow_origins=[
    "http://localhost:3000",
    "https://your-frontend-domain.com",
    # Add more origins as needed
]
```

### Change Server Port

Modify the uvicorn command:
```powershell
uvicorn app.main:app --reload --port 8080
```

## 📦 Dependencies

Main dependencies (see `requirements.txt` for full list):

- **fastapi**: Web framework
- **uvicorn**: ASGI server
- **pydantic**: Data validation
- **numpy**: Numerical computing
- **pandas**: Data manipulation
- **scikit-learn**: ML utilities
- **tensorflow**: Deep learning (optional)
- **torch**: PyTorch (optional)

## 🛠️ Development Tips

1. **Auto-reload**: The `--reload` flag automatically restarts the server when you make code changes.

2. **Logging**: Check console output for request logs and errors.

3. **Type Hints**: Use Python type hints for better code completion and error detection.

4. **Validation**: Pydantic models automatically validate request data.

## 🐛 Troubleshooting

### Port Already in Use
```powershell
# Use a different port
uvicorn app.main:app --reload --port 8001
```

### Import Errors
```powershell
# Make sure you're in the backend directory and venv is activated
cd c:\Users\franc\Downloads\backend
.\venv\Scripts\Activate.ps1
```

### CORS Issues
- Check that your frontend URL is in the `allow_origins` list in `app/main.py`
- Verify the frontend is making requests to the correct URL

## 📝 Next Steps

1. ✅ Install dependencies and run the server
2. ✅ Test the `/predict` endpoint in Swagger UI
3. 🔄 Train your ML model
4. 🔄 Replace the mock `predict()` function with your model
5. 🔄 Deploy to production (consider using Docker, AWS, GCP, or Azure)

## 📄 License

This project is open source and available for your use.

## 🤝 Contributing

Feel free to extend and modify this backend for your specific needs!

---

**Happy Coding! 🚀**
