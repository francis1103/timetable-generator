"""FastAPI-based REST API for timetable scheduling system."""

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import json
import asyncio
import os
import pandas as pd

from src.optimization.scheduler import TimetableScheduler
from src.models.schedule import Timetable

app = FastAPI(
    title="AI Timetable Scheduler API",
    description="REST API for intelligent timetable generation and optimization",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global scheduler instance
scheduler = TimetableScheduler()

# Active WebSocket connections
active_connections: List[WebSocket] = []


# Pydantic models for API
class ScheduleRequest(BaseModel):
    """Request model for schedule generation."""
    method: str = 'nsga2'  # nsga2, csp, ilp, hybrid
    population_size: Optional[int] = 100
    num_generations: Optional[int] = 50
    verbose: bool = True


class NaturalLanguageRule(BaseModel):
    """Model for natural language scheduling rule."""
    rule: str
    priority: str = 'medium'


class ConflictResolutionRequest(BaseModel):
    """Request model for conflict resolution."""
    use_ilp: bool = True


# WebSocket manager
class ConnectionManager:
    """Manages WebSocket connections for real-time updates."""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass


manager = ConnectionManager()


# API Endpoints

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "AI Timetable Scheduler API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "load_data": "POST /api/load-data",
            "generate": "POST /api/generate",
            "conflicts": "GET /api/conflicts",
            "resolve": "POST /api/resolve-conflicts",
            "export": "POST /api/export",
            "recommendations": "GET /api/recommendations"
        }
    }


@app.post("/api/load-data")
async def load_data(
    data_source: str = Query(..., description="Path to data file or directory"),
    format: str = Query("csv", description="Format: csv, excel, json (auto-detected from file extension)")
):
    """
    Load scheduling data from file or directory.
    
    Examples:
    - Directory: ?data_source=data&format=csv
    - Single file: ?data_source=C:/path/to/file.csv&format=csv
    - Excel: ?data_source=C:/path/to/file.xlsx&format=excel
    """
    try:
        # Remove surrounding quotes if present (from Swagger UI)
        data_source = data_source.strip('"').strip("'")
        
        # Auto-detect format from file extension if single file
        if os.path.isfile(data_source):
            ext = os.path.splitext(data_source)[1].lower()
            if ext in ['.xlsx', '.xls']:
                format = 'excel'
            elif ext == '.json':
                format = 'json'
            elif ext == '.csv':
                format = 'csv'
        
        scheduler.load_data(data_source, format)
        
        return {
            "status": "success",
            "message": f"Data loaded successfully from {data_source}",
            "data": {
                "courses": len(scheduler.courses),
                "faculty": len(scheduler.faculty),
                "rooms": len(scheduler.rooms),
                "students": len(scheduler.students),
                "time_slots": len(scheduler.time_slots)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/preview-data")
async def preview_data(
    file_path: str = Query(..., description="Path to CSV/Excel file to preview"),
    rows: int = Query(5, description="Number of rows to display", ge=1, le=100)
):
    """
    Preview top N rows of a CSV or Excel file before loading.
    
    Example: ?file_path=C:/Users/mrunk/Downloads/FINAL_INFOSYS.csv&rows=5
    """
    try:
        # Remove surrounding quotes if present (from Swagger UI)
        file_path = file_path.strip('"').strip("'")
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail=f"File not found: {file_path}")
        
        # Detect format
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext == '.csv':
            df = pd.read_csv(file_path, nrows=rows)
        elif ext in ['.xlsx', '.xls']:
            df = pd.read_excel(file_path, nrows=rows)
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported file format: {ext}")
        
        # Replace NaN values with None for JSON serialization
        df = df.fillna('')  # Replace NaN with empty string
        
        # Convert to JSON-friendly format
        preview_data = {
            "file_path": file_path,
            "total_columns": len(df.columns),
            "columns": df.columns.tolist(),
            "rows_shown": len(df),
            "data": df.to_dict(orient='records')
        }
        
        return {
            "status": "success",
            "preview": preview_data
        }
    except HTTPException:
        raise  # Re-raise HTTPException as-is
    except Exception as e:
        import traceback
        error_detail = f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()}"
        raise HTTPException(status_code=500, detail=error_detail)


@app.post("/api/add-rule")
async def add_natural_language_rule(rule: NaturalLanguageRule):
    """
    Add a scheduling rule in natural language.
    
    Example: "No classes for Computer Science students after 3 PM on Fridays"
    """
    try:
        scheduler.add_natural_language_rule(rule.rule)
        
        await manager.broadcast({
            "event": "rule_added",
            "rule": rule.rule,
            "priority": rule.priority
        })
        
        return {
            "status": "success",
            "message": "Rule added successfully",
            "rule": rule.rule
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/generate")
async def generate_schedule(request: ScheduleRequest):
    """
    Generate optimal timetable.
    
    Args:
        request: Schedule generation parameters
    """
    try:
        # Update configuration if provided
        if request.population_size:
            scheduler.optimization_config.population_size = request.population_size
        if request.num_generations:
            scheduler.optimization_config.num_generations = request.num_generations
        
        # Generate schedule
        timetable = scheduler.generate_optimal_schedule(
            method=request.method,
            verbose=request.verbose
        )
        
        # Broadcast update
        await manager.broadcast({
            "event": "schedule_generated",
            "method": request.method,
            "total_slots": timetable.get_total_slots(),
            "is_valid": timetable.is_valid()
        })
        
        return {
            "status": "success",
            "message": "Schedule generated successfully",
            "timetable": {
                "total_slots": timetable.get_total_slots(),
                "is_valid": timetable.is_valid(),
                "conflicts": len(timetable.conflicts),
                "fitness_scores": timetable.fitness_scores,
                "statistics": timetable.get_utilization_stats()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/timetable")
async def get_current_timetable():
    """Get the current timetable."""
    if not scheduler.schedule.current_timetable:
        raise HTTPException(status_code=404, detail="No timetable generated yet")
    
    return scheduler.schedule.export_current('json')


@app.get("/api/conflicts")
async def get_conflicts():
    """Get conflict report for current timetable."""
    if not scheduler.schedule.current_timetable:
        raise HTTPException(status_code=404, detail="No timetable generated yet")
    
    report = scheduler.get_conflict_report()
    return report


@app.post("/api/resolve-conflicts")
async def resolve_conflicts(request: ConflictResolutionRequest):
    """Resolve conflicts in the current timetable."""
    if not scheduler.schedule.current_timetable:
        raise HTTPException(status_code=404, detail="No timetable to resolve")
    
    try:
        resolved_timetable = scheduler.resolve_conflicts()
        
        await manager.broadcast({
            "event": "conflicts_resolved",
            "remaining_conflicts": len(resolved_timetable.conflicts)
        })
        
        return {
            "status": "success",
            "message": "Conflicts resolved",
            "timetable": {
                "total_slots": resolved_timetable.get_total_slots(),
                "is_valid": resolved_timetable.is_valid(),
                "conflicts": len(resolved_timetable.conflicts)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/recommendations")
async def get_recommendations():
    """Get AI-powered scheduling recommendations."""
    recommendations = scheduler.get_recommendations()
    
    return {
        "status": "success",
        "recommendations": recommendations,
        "count": len(recommendations)
    }


@app.post("/api/export")
async def export_timetable(
    output_path: str = Query(..., description="Output file path or directory"),
    format: str = Query('pdf', description="Export format: pdf, excel, json, ical, html")
):
    """
    Export timetable to file.
    
    Args:
        output_path: Output file path or directory
        format: Export format (pdf, excel, json, ical, html)
    """
    if not scheduler.schedule.current_timetable:
        raise HTTPException(status_code=404, detail="No timetable to export")
    
    try:
        # Remove surrounding quotes if present
        output_path = output_path.strip('"').strip("'")
        
        scheduler.export(output_path, format)
        
        return {
            "status": "success",
            "message": f"Timetable exported to {output_path}",
            "format": format,
            "output_path": output_path
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/statistics")
async def get_statistics():
    """Get detailed statistics about the current timetable."""
    if not scheduler.schedule.current_timetable:
        raise HTTPException(status_code=404, detail="No timetable generated yet")
    
    timetable = scheduler.schedule.current_timetable
    
    return {
        "status": "success",
        "statistics": {
            "total_slots": timetable.get_total_slots(),
            "is_valid": timetable.is_valid(),
            "conflicts": len(timetable.conflicts),
            "utilization": timetable.get_utilization_stats(),
            "fitness_scores": timetable.fitness_scores
        }
    }


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates."""
    await manager.connect(websocket)
    
    try:
        while True:
            # Receive messages from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Echo back
            await websocket.send_json({
                "event": "message_received",
                "data": message
            })
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
