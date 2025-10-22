"""
Main FastAPI application for Grammar Correction Web App
"""

import os
import sys
import uuid
import asyncio
import json
from typing import Dict, Any, Set
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
from dotenv import load_dotenv

# Load environment variables - check multiple locations
# For PyInstaller bundled executable
if getattr(sys, 'frozen', False):
    # Running as compiled executable
    app_dir = os.path.dirname(sys.executable)
    # Try next to the executable first
    env_paths = [
        os.path.join(app_dir, '.env'),
        os.path.join(sys._MEIPASS, '.env'),  # Inside the bundle
    ]
else:
    # Running as script
    env_paths = [
        os.path.join(os.path.dirname(__file__), '..', '.env'),
    ]

# Load first available .env file
env_loaded = False
for env_path in env_paths:
    if os.path.exists(env_path):
        load_dotenv(env_path)
        print(f"[Config] Loaded environment from: {env_path}")
        env_loaded = True
        break

if not env_loaded:
    print("[Config] No .env file found - using system environment variables")

from services.document_parser import DocumentParser
from services.grammar_checker import GrammarChecker
from services.report_generator import ReportGenerator
from services.progress_tracker import ProgressTracker
from services.performance_logger import get_performance_logger
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

@app.get("/categories")
async def get_categories():
    """
    Get available grammar checking categories
    """
    return {"categories": grammar_checker.get_available_categories()}

@app.post("/upload", response_model=UploadResponse)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    output_filename: str = Form(None),
    output_format: str = Form("docx"),
    categories: str = Form(None),  # Comma-separated category IDs
    use_llm_enhancement: str = Form("false"),  # AI enhancement flag
    use_llm_detection: str = Form("false")  # AI detection flag (supplementary)
):
    """
    Upload a document for grammar checking
    
    Args:
        file: Document file to analyze
        output_filename: Optional output filename (form field)
        output_format: Output format (docx or pdf) (form field)
        categories: Optional comma-separated list of category IDs to check (e.g., "redundancy,grammar") (form field)
        use_llm_enhancement: Enable AI-powered enhancement of fixes (~$0.01-0.03 per MB) (form field)
        use_llm_detection: Enable AI-powered detection for subtle issues (~$0.05-0.15 per MB) (form field)
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
    
    # Parse categories parameter
    print(f"[{task_id}] Received categories parameter: {repr(categories)}")
    enabled_categories = None
    if categories:
        enabled_categories = [cat.strip() for cat in categories.split(',') if cat.strip()]
        print(f"[{task_id}] Parsed categories: {enabled_categories}")
    else:
        print(f"[{task_id}] No categories specified - will check all categories")
    
    # Parse LLM parameters
    llm_enhancement_enabled = use_llm_enhancement.lower() in ('true', '1', 'yes')
    llm_detection_enabled = use_llm_detection.lower() in ('true', '1', 'yes')
    print(f"[{task_id}] LLM Enhancement: {llm_enhancement_enabled}")
    print(f"[{task_id}] LLM Detection: {llm_detection_enabled}")
    
    # Store task information
    processing_tasks[task_id] = {
        "status": "uploaded",
        "filename": file.filename,
        "output_filename": output_filename,
        "output_format": output_format,
        "categories": enabled_categories,
        "use_llm_enhancement": llm_enhancement_enabled,
        "use_llm_detection": llm_detection_enabled,
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
        output_format,
        enabled_categories,
        llm_enhancement_enabled,
        llm_detection_enabled
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
    output_format: str,
    enabled_categories: list = None,
    use_llm_enhancement: bool = False,
    use_llm_detection: bool = False
):
    """
    Process document with a small delay to ensure WebSocket connects first
    """
    # Wait 1 second to allow WebSocket connection to establish
    await asyncio.sleep(1)
    await process_document(task_id, file_content, original_filename, output_filename, output_format, enabled_categories, use_llm_enhancement, use_llm_detection)

async def process_document(
    task_id: str,
    file_content: bytes,
    original_filename: str,
    output_filename: str,
    output_format: str,
    enabled_categories: list = None,
    use_llm_enhancement: bool = False,
    use_llm_detection: bool = False
):
    """
    Background task to process the uploaded document with real-time WebSocket updates
    
    Args:
        task_id: Unique task identifier
        file_content: Document file content
        original_filename: Original filename
        output_filename: Output filename
        output_format: Output format (docx or pdf)
        enabled_categories: Optional list of category IDs to check
        use_llm_enhancement: Enable AI-powered enhancement
        use_llm_detection: Enable AI-powered detection (supplementary)
    """
    # Initialize performance logger
    perf_logger = get_performance_logger()
    perf_logger.start_task(
        task_id=task_id,
        filename=original_filename,
        file_size=len(file_content),
        categories=enabled_categories or [],
        ai_mode={"enhancement": use_llm_enhancement, "detection": use_llm_detection}
    )
    
    # Determine AI mode for frontend display
    if use_llm_detection and use_llm_enhancement:
        ai_mode_name = "premium"  # Full AI mode
    elif use_llm_enhancement:
        ai_mode_name = "competitive"  # AI Enhancement only
    else:
        ai_mode_name = "free"  # Pattern-only
    
    try:
        print(f"[{task_id}] Starting document processing...")
        print(f"[{task_id}] AI Mode: {ai_mode_name}")
        
        # Send WebSocket update: Starting
        await manager.send_progress(task_id, {
            "type": "starting",
            "message": "Starting analysis...",
            "ai_mode": ai_mode_name,
            "llm_enhancement": use_llm_enhancement,
            "llm_detection": use_llm_detection
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
        perf_logger.start_stage("parsing")
        document_data = await document_parser.parse_document(
            file_content, original_filename
        )
        perf_logger.end_stage("parsing", {
            "total_lines": document_data.total_lines if document_data else 0,
            "total_sentences": document_data.total_sentences if document_data else 0
        })
        
        if not document_data:
            perf_logger.log_error("ParseError", "Failed to parse document", "parsing")
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
        perf_logger.start_stage("checking")
        
        # Track timing for progress updates
        import time
        stage_start_time = time.time()
        
        issues = []
        async def progress_callback(line_num: int, total_lines: int, current_issues: int):
            """Send real-time updates during grammar checking with timing data"""
            progress = 30 + int((line_num / total_lines) * 50)
            processing_tasks[task_id]["progress"] = progress
            processing_tasks[task_id]["lines_analyzed"] = line_num
            processing_tasks[task_id]["issues_found"] = current_issues
            
            # Calculate timing stats
            elapsed_seconds = int(time.time() - stage_start_time)
            processing_speed = line_num / elapsed_seconds if elapsed_seconds > 0 else 0
            
            # Estimate remaining time based on progress
            total_elapsed = int(time.time() - perf_logger.current_task["start_time"]) if perf_logger.current_task else elapsed_seconds
            if progress > 5:  # Only estimate after some progress
                estimated_total = total_elapsed / (progress / 100) if progress > 0 else 0
                estimated_remaining = max(0, int(estimated_total - total_elapsed))
            else:
                estimated_remaining = 0
            
            # Send WebSocket update with timing data
            await manager.send_progress(task_id, {
                "type": "progress",
                "status": "checking",
                "progress": progress,
                "total_lines": total_lines,
                "lines_analyzed": line_num,
                "issues_found": current_issues,
                "message": f"Analyzing line {line_num}/{total_lines}...",
                "timing": {
                    "elapsed_seconds": total_elapsed,
                    "processing_speed": round(processing_speed, 2),
                    "estimated_remaining_seconds": estimated_remaining
                },
                "ai_mode": ai_mode_name
            })
        
        # Enhancement progress callback for WebSocket updates
        async def enhancement_progress_callback(data):
            await manager.send_progress(task_id, data)
        
        issues, enhancement_metadata = await grammar_checker.check_document(
            document_data,
            progress_callback=progress_callback,
            enabled_categories=enabled_categories,
            use_llm_enhancement=use_llm_enhancement,
            use_llm_detection=use_llm_detection,
            enhancement_progress_callback=enhancement_progress_callback
        )
        
        perf_logger.end_stage("checking", {
            "issues_found": len(issues),
            "lines_processed": document_data.total_lines,
            "llm_detection_enabled": enhancement_metadata.get("llm_detection_enabled", False),
            "llm_enhancement_enabled": enhancement_metadata.get("llm_enabled", False),
            "issues_detected_by_llm": enhancement_metadata.get("issues_detected_by_llm", 0),
            "issues_enhanced": enhancement_metadata.get("issues_enhanced", 0)
        })
        
        # Log API usage if LLM was used
        if enhancement_metadata.get("cost", 0) > 0:
            perf_logger.log_api_call(
                api_type="llm_full" if enhancement_metadata.get("llm_detection_enabled") else "llm_enhancement",
                model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                cost=enhancement_metadata.get("cost", 0),
                success=enhancement_metadata.get("warning") is None
            )
        
        print(f"[{task_id}] Found {len(issues)} issues")
        
        if enhancement_metadata.get("llm_detection_enabled"):
            print(f"[{task_id}] 🔍 LLM detected {enhancement_metadata.get('issues_detected_by_llm', 0)} additional issues")
        
        if enhancement_metadata.get("llm_enabled"):
            print(f"[{task_id}] ✨ LLM enhanced {enhancement_metadata.get('issues_enhanced', 0)} issues")
            print(f"[{task_id}] 💰 LLM cost: ${enhancement_metadata.get('cost', 0):.4f}")
        
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
        perf_logger.start_stage("generating")
        report_path = await report_generator.generate_report(
            issues,
            document_data,
            output_filename,
            output_format
        )
        perf_logger.end_stage("generating", {
            "output_format": output_format,
            "report_size": os.path.getsize(report_path) if os.path.exists(report_path) else 0
        })
        
        print(f"[{task_id}] Report generated: {report_path}")
        
        # Update status
        processing_tasks[task_id]["status"] = "completed"
        processing_tasks[task_id]["progress"] = 100
        processing_tasks[task_id]["result"] = {
            "report_path": report_path,
            "filename": f"{output_filename}.{output_format}",
            "issues_count": len(issues),
            "issues": [issue.dict() for issue in issues],  # Convert Pydantic models to dict
            "summary": grammar_checker.get_issues_summary(issues),
            "enhancement": enhancement_metadata  # Include LLM cost and stats
        }
        
        # Send WebSocket update: Completed
        await manager.send_progress(task_id, {
            "type": "completed",
            "status": "completed",
            "progress": 100,
            "issues_count": len(issues),
            "message": "Processing completed successfully!"
        })
        
        # Complete performance logging
        summary = grammar_checker.get_issues_summary(issues)
        perf_data = perf_logger.end_task({
            "total_issues": len(issues),
            "lines_with_issues": summary.get("lines_with_issues", 0),
            "sentences_with_issues": summary.get("sentences_with_issues", 0),
            "categories": summary.get("categories", {}),
            "llm_cost": enhancement_metadata.get("cost", 0)
        })
        
        # Check for bottlenecks and log recommendations
        bottlenecks = perf_logger.get_bottlenecks(threshold_percentage=25.0)
        if bottlenecks:
            print(f"[{task_id}] ⚠️  Performance bottlenecks detected:")
            for bn in bottlenecks:
                print(f"         {bn['stage']}: {bn['duration_seconds']:.2f}s ({bn['percentage']:.1f}%)")
                print(f"         → {bn['recommendation']}")
        
        print(f"[{task_id}] Processing completed successfully")
        print(f"[PerfLog] Performance data saved to logs/performance/")
        
    except Exception as e:
        print(f"[{task_id}] Error: {e}")
        import traceback
        traceback.print_exc()
        
        # Log error
        perf_logger.log_error("ProcessingError", str(e))
        perf_logger.end_task()
        
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
