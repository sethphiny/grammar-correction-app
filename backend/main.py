"""
Main FastAPI application for Grammar Correction Web App
"""

import os
import uuid
import asyncio
from typing import Dict, Any
from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

from services.document_parser import DocumentParser
from services.hybrid_grammar_checker import HybridGrammarChecker
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
grammar_checker = HybridGrammarChecker()
report_generator = ReportGenerator()
progress_tracker = ProgressTracker()

# In-memory storage for processing tasks (in production, use Redis or database)
processing_tasks: Dict[str, Dict[str, Any]] = {}

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
    
    # Start background processing
    background_tasks.add_task(
        process_document,
        task_id,
        content,
        file.filename,
        output_filename,
        output_format
    )
    
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
    return ProcessingStatus(
        task_id=task_id,
        status=task["status"],
        progress=task["progress"],
        message=progress_tracker.get_status_message(task["status"]),
        error=task.get("error")
    )

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

async def process_document(
    task_id: str,
    file_content: bytes,
    original_filename: str,
    output_filename: str,
    output_format: str
):
    """
    Background task to process the uploaded document
    """
    try:
        # Update status
        processing_tasks[task_id]["status"] = "parsing"
        processing_tasks[task_id]["progress"] = 10
        
        # Parse document
        document_data = await document_parser.parse_document(
            file_content, original_filename
        )
        
        if not document_data:
            raise Exception("Failed to parse document")
        
        # Update status
        processing_tasks[task_id]["status"] = "checking"
        processing_tasks[task_id]["progress"] = 30
        
        # Grammar checking
        issues = await grammar_checker.check_document(
            document_data,
            progress_callback=lambda p: update_progress(task_id, 30 + int(p * 0.5))
        )
        
        # Update status
        processing_tasks[task_id]["status"] = "generating"
        processing_tasks[task_id]["progress"] = 80
        
        # Generate report
        report_path = await report_generator.generate_report(
            issues,
            document_data,
            output_filename,
            output_format
        )
        
        # Update status
        processing_tasks[task_id]["status"] = "completed"
        processing_tasks[task_id]["progress"] = 100
        processing_tasks[task_id]["result"] = {
            "report_path": report_path,
            "filename": f"{output_filename}.{output_format}",
            "issues_count": len(issues),
            "summary": grammar_checker.get_issues_summary(issues)
        }
        
    except Exception as e:
        processing_tasks[task_id]["status"] = "error"
        processing_tasks[task_id]["error"] = str(e)
        processing_tasks[task_id]["progress"] = 0

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
