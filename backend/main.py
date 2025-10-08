"""
Main FastAPI application for Grammar Correction Web App
"""

import os
import uuid
import asyncio
import json
from typing import Dict, Any, Set
from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

from services.document_parser import DocumentParser
from services.grammar_checker import GrammarChecker
from services.report_generator import ReportGenerator
from services.progress_tracker import ProgressTracker
from models.schemas import (
    UploadResponse,
    ProcessingStatus,
    ProcessingResult,
    ErrorResponse
)

# Initialize FastAPI app
app = FastAPI(
    title="Grammar Correction API",
    description="API for grammar checking and document analysis",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
document_parser = DocumentParser()
grammar_checker = GrammarChecker()
report_generator = ReportGenerator()
progress_tracker = ProgressTracker()

# In-memory storage for processing tasks (in production, use Redis or database)
processing_tasks: Dict[str, Dict[str, Any]] = {}

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, task_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[task_id] = websocket
        print(f"[WebSocket] Client connected for task {task_id}")
    
    def disconnect(self, task_id: str):
        if task_id in self.active_connections:
            del self.active_connections[task_id]
            print(f"[WebSocket] Client disconnected for task {task_id}")
    
    async def send_progress(self, task_id: str, data: dict):
        if task_id in self.active_connections:
            try:
                await self.active_connections[task_id].send_json(data)
            except Exception as e:
                print(f"[WebSocket] Error sending to {task_id}: {e}")
                self.disconnect(task_id)

manager = ConnectionManager()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "grammar-correction-api"}

@app.post("/upload", response_model=UploadResponse)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    output_filename: str = None,
    output_format: str = "docx"
):
    """
    Upload a document for grammar checking
    """
    # Validate file type
    if not file.filename.lower().endswith(('.doc', '.docx')):
        raise HTTPException(
            status_code=400,
            detail="Only .doc and .docx files are supported"
        )
    
    # Validate file size (10MB limit)
    max_size = int(os.getenv("MAX_FILE_SIZE", 10485760))
    content = await file.read()
    if len(content) > max_size:
        raise HTTPException(
            status_code=400,
            detail=f"File size exceeds {max_size // 1024 // 1024}MB limit"
        )
    
    # Generate task ID
    task_id = str(uuid.uuid4())
    
    # Set default output filename
    if not output_filename:
        base_name = os.path.splitext(file.filename)[0]
        output_filename = f"{base_name}_corrected"
    
    # Store task information
    processing_tasks[task_id] = {
        "status": "uploaded",
        "filename": file.filename,
        "output_filename": output_filename,
        "output_format": output_format,
        "progress": 0,
        "result": None,
        "error": None
    }
    
    print(f"[{task_id}] Document uploaded: {file.filename} ({len(content)} bytes)")
    
    # Start background processing with a small delay to ensure WebSocket connects first
    background_tasks.add_task(
        process_document_with_delay,
        task_id,
        content,
        file.filename,
        output_filename,
        output_format
    )
    
    print(f"[{task_id}] Background task added")
    
    return UploadResponse(
        task_id=task_id,
        message="Document uploaded successfully. Processing started."
    )

@app.get("/status/{task_id}", response_model=ProcessingStatus)
async def get_processing_status(task_id: str):
    """
    Get the processing status of a task
    """
    if task_id not in processing_tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = processing_tasks[task_id]
    print(f"[{task_id}] Status check: {task['status']} ({task['progress']}%)")
    
    return ProcessingStatus(
        task_id=task_id,
        status=task["status"],
        progress=task["progress"],
        message=progress_tracker.get_status_message(task["status"]),
        error=task.get("error")
    )

@app.get("/results/{task_id}")
async def get_processing_results(task_id: str):
    """
    Get the processing results (issues and summary) for a completed task
    """
    if task_id not in processing_tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = processing_tasks[task_id]
    
    if task["status"] != "completed":
        raise HTTPException(status_code=400, detail="Task not completed yet")
    
    if not task.get("result"):
        raise HTTPException(status_code=404, detail="No results found")
    
    return task["result"]

@app.get("/download/{task_id}")
async def download_report(task_id: str):
    """
    Download the generated report
    """
    if task_id not in processing_tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = processing_tasks[task_id]
    
    if task["status"] != "completed":
        raise HTTPException(
            status_code=400,
            detail="Report not ready yet"
        )
    
    result = task["result"]
    if not result or not result.get("report_path"):
        raise HTTPException(
            status_code=500,
            detail="Report file not found"
        )
    
    return FileResponse(
        path=result["report_path"],
        filename=result["filename"],
        media_type="application/octet-stream"
    )

@app.websocket("/ws/{task_id}")
async def websocket_endpoint(websocket: WebSocket, task_id: str):
    """
    WebSocket endpoint for real-time progress updates
    """
    await manager.connect(task_id, websocket)
    try:
        # Keep connection alive and send initial status if available
        if task_id in processing_tasks:
            await manager.send_progress(task_id, {
                "type": "status",
                "status": processing_tasks[task_id]["status"],
                "progress": processing_tasks[task_id]["progress"]
            })
        
        # Keep connection open until client disconnects
        while True:
            try:
                # Wait for any message from client (ping/pong)
                await asyncio.wait_for(websocket.receive_text(), timeout=1.0)
            except asyncio.TimeoutError:
                # No message received, continue waiting
                continue
            except WebSocketDisconnect:
                break
    except Exception as e:
        print(f"[WebSocket] Error: {e}")
    finally:
        manager.disconnect(task_id)

async def process_document_with_delay(
    task_id: str,
    file_content: bytes,
    original_filename: str,
    output_filename: str,
    output_format: str
):
    """
    Process document with a small delay to ensure WebSocket connects first
    """
    # Wait 1 second to allow WebSocket connection to establish
    await asyncio.sleep(1)
    await process_document(task_id, file_content, original_filename, output_filename, output_format)

async def process_document(
    task_id: str,
    file_content: bytes,
    original_filename: str,
    output_filename: str,
    output_format: str
):
    """
    Background task to process the uploaded document with real-time WebSocket updates
    """
    try:
        print(f"[{task_id}] Starting document processing...")
        
        # Send WebSocket update: Starting
        await manager.send_progress(task_id, {
            "type": "starting",
            "message": "Starting analysis..."
        })
        
        # Update status
        processing_tasks[task_id]["status"] = "parsing"
        processing_tasks[task_id]["progress"] = 10
        print(f"[{task_id}] Status: parsing")
        
        # Send WebSocket update: Parsing
        await manager.send_progress(task_id, {
            "type": "status",
            "status": "parsing",
            "progress": 10,
            "message": "Parsing document..."
        })
        
        # Parse document
        document_data = await document_parser.parse_document(
            file_content, original_filename
        )
        
        if not document_data:
            raise Exception("Failed to parse document")
        
        print(f"[{task_id}] Parsed: {document_data.total_lines} lines")
        
        # Send WebSocket update: Document parsed
        await manager.send_progress(task_id, {
            "type": "parsed",
            "total_lines": document_data.total_lines,
            "total_sentences": document_data.total_sentences,
            "message": f"Document parsed: {document_data.total_lines} lines to analyze"
        })
        
        # Update status
        processing_tasks[task_id]["status"] = "checking"
        processing_tasks[task_id]["progress"] = 30
        processing_tasks[task_id]["total_lines"] = document_data.total_lines
        processing_tasks[task_id]["lines_analyzed"] = 0
        processing_tasks[task_id]["issues_found"] = 0
        print(f"[{task_id}] Status: checking grammar")
        
        # Send WebSocket update: Starting grammar check
        await manager.send_progress(task_id, {
            "type": "status",
            "status": "checking",
            "progress": 30,
            "total_lines": document_data.total_lines,
            "lines_analyzed": 0,
            "issues_found": 0,
            "message": "Analyzing grammar and style..."
        })
        
        # Grammar checking with real-time progress
        issues = []
        async def progress_callback(line_num: int, total_lines: int, current_issues: int):
            """Send real-time updates during grammar checking"""
            progress = 30 + int((line_num / total_lines) * 50)
            processing_tasks[task_id]["progress"] = progress
            processing_tasks[task_id]["lines_analyzed"] = line_num
            processing_tasks[task_id]["issues_found"] = current_issues
            
            # Send WebSocket update
            await manager.send_progress(task_id, {
                "type": "progress",
                "status": "checking",
                "progress": progress,
                "total_lines": total_lines,
                "lines_analyzed": line_num,
                "issues_found": current_issues,
                "message": f"Analyzing line {line_num}/{total_lines}..."
            })
        
        issues = await grammar_checker.check_document(
            document_data,
            progress_callback=progress_callback
        )
        
        print(f"[{task_id}] Found {len(issues)} issues")
        
        # Send WebSocket update: Analysis complete
        await manager.send_progress(task_id, {
            "type": "analysis_complete",
            "issues_found": len(issues),
            "message": f"Analysis complete: {len(issues)} issues found"
        })
        
        # Update status
        processing_tasks[task_id]["status"] = "generating"
        processing_tasks[task_id]["progress"] = 80
        print(f"[{task_id}] Status: generating report")
        
        # Send WebSocket update: Generating report
        await manager.send_progress(task_id, {
            "type": "status",
            "status": "generating",
            "progress": 80,
            "message": "Generating correction report..."
        })
        
        # Generate report
        report_path = await report_generator.generate_report(
            issues,
            document_data,
            output_filename,
            output_format
        )
        
        print(f"[{task_id}] Report generated: {report_path}")
        
        # Update status
        processing_tasks[task_id]["status"] = "completed"
        processing_tasks[task_id]["progress"] = 100
        processing_tasks[task_id]["result"] = {
            "report_path": report_path,
            "filename": f"{output_filename}.{output_format}",
            "issues_count": len(issues),
            "issues": [issue.dict() for issue in issues],  # Convert Pydantic models to dict
            "summary": grammar_checker.get_issues_summary(issues)
        }
        
        # Send WebSocket update: Completed
        await manager.send_progress(task_id, {
            "type": "completed",
            "status": "completed",
            "progress": 100,
            "issues_count": len(issues),
            "message": "Processing completed successfully!"
        })
        
        print(f"[{task_id}] Processing completed successfully")
        
    except Exception as e:
        print(f"[{task_id}] Error: {e}")
        import traceback
        traceback.print_exc()
        
        processing_tasks[task_id]["status"] = "error"
        processing_tasks[task_id]["error"] = str(e)
        processing_tasks[task_id]["progress"] = 0
        
        # Send WebSocket update: Error
        await manager.send_progress(task_id, {
            "type": "error",
            "status": "error",
            "error": str(e),
            "message": f"Error: {str(e)}"
        })

def update_progress(task_id: str, progress: int):
    """Update task progress"""
    if task_id in processing_tasks:
        processing_tasks[task_id]["progress"] = progress

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
