# Start the API server
Write-Host "Starting AI Timetable Scheduler API..." -ForegroundColor Green
Write-Host "Server will be available at: http://127.0.0.1:8000" -ForegroundColor Cyan
Write-Host "API Documentation: http://127.0.0.1:8000/docs" -ForegroundColor Cyan
Write-Host ""

# Activate virtual environment and start server
& .\venv\Scripts\Activate.ps1
uvicorn src.api.main:app --reload --host 127.0.0.1 --port 8000
