from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import os
import tempfile
import uuid
import time
from typing import Dict, List, Optional
import asyncio
from datetime import datetime

from services.document_parser import DocumentParser
from services.streaming_grammar_checker import StreamingGrammarChecker
from services.report_generator import ReportGenerator
from services.progress_tracker import ProgressTracker
from services.websocket_manager import websocket_manager
from models.schemas import ProcessingStatus, GrammarIssue, CorrectionReport, ProcessingStatusEnum

app = FastAPI(
    title="Grammar Correction API", 
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add middleware to handle large request bodies
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    # Add headers for large file uploads
    response = await call_next(request)
    if request.url.path == "/upload":
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
    return response

# Global storage for processing status and progress trackers
processing_status: Dict[str, ProcessingStatus] = {}
progress_trackers: Dict[str, ProgressTracker] = {}

# Initialize services with optimized settings
document_parser = DocumentParser()
# Try to use LanguageTool server mode for better performance, fallback to local mode
try:
    streaming_grammar_checker = StreamingGrammarChecker(use_server_mode=True, server_url="https://api.languagetool.org")
    print("✅ Using LanguageTool server mode for optimal performance")
except Exception as e:
    print(f"⚠️ Server mode unavailable, using local mode: {e}")
    streaming_grammar_checker = StreamingGrammarChecker(use_server_mode=False)
report_generator = ReportGenerator()

@app.get("/")
async def root():
    return {"message": "Grammar Correction API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.websocket("/ws/{processing_id}")
async def websocket_endpoint(websocket: WebSocket, processing_id: str):
    """WebSocket endpoint for real-time streaming updates"""
    await websocket_manager.connect(websocket, processing_id)
    try:
        while True:
            # Keep the connection alive and handle any incoming messages
            data = await websocket.receive_text()
            # Echo back any messages (for testing)
            await websocket.send_text(f"Echo: {data}")
    except WebSocketDisconnect:
        websocket_manager.disconnect(processing_id)

@app.post("/upload")
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    output_format: str = "docx",
    custom_filename: Optional[str] = None
):
    """Upload and process a document for grammar checking"""
    
    # Validate file type
    if not file.filename.lower().endswith(('.doc', '.docx')):
        raise HTTPException(status_code=400, detail="Only .doc and .docx files are allowed")
    
    # Validate file size (50MB limit for large files)
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB in bytes
    if file.size and file.size > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File size exceeds 50MB limit")
    
    # Warn about large files that might take longer to process
    LARGE_FILE_THRESHOLD = 5 * 1024 * 1024  # 5MB
    if file.size and file.size > LARGE_FILE_THRESHOLD:
        print(f"Warning: Large file detected ({file.size // 1024 // 1024}MB) - processing may take longer")
    
    # Generate unique processing ID
    processing_id = str(uuid.uuid4())
    
    # Initialize progress tracker
    progress_tracker = ProgressTracker()
    progress_tracker.start_processing()
    progress_trackers[processing_id] = progress_tracker
    
    # Initialize processing status
    processing_status[processing_id] = ProcessingStatus(
        id=processing_id,
        status=ProcessingStatusEnum.UPLOADING,
        progress=0,
        message="Starting file upload...",
        filename=file.filename,
        output_format=output_format,
        custom_filename=custom_filename,
        issues=[],
        summary={},
        estimated_time_remaining=None,
        current_stage_progress=0,
        total_stages=progress_tracker.total_stages,
        current_stage=1,
        stage_name=progress_tracker.stage_names[ProcessingStatusEnum.UPLOADING]
    )
    
    try:
        # Update status to show upload in progress
        processing_status[processing_id].progress = 5
        processing_status[processing_id].message = "Reading file content..."
        
        # Read file content in chunks to handle large files efficiently
        file_content = b""
        file_filename = file.filename
        
        # Read file in chunks to avoid memory issues with large files
        while chunk := await file.read(8192):  # 8KB chunks
            file_content += chunk
        
        # Update status to show upload completed
        processing_status[processing_id].progress = 10
        processing_status[processing_id].message = f"File uploaded successfully ({len(file_content) // 1024}KB)"
        
        # Set file size for ETA calculations
        progress_tracker.set_file_size(len(file_content))
        
        # Update progress tracking for upload completion
        progress_tracker.update_stage_progress(ProcessingStatusEnum.UPLOADING, 100)
        stage_info = progress_tracker.get_stage_info(ProcessingStatusEnum.UPLOADING, 100)
        processing_status[processing_id].current_stage_progress = stage_info['current_stage_progress']
        processing_status[processing_id].estimated_time_remaining = progress_tracker.get_eta(ProcessingStatusEnum.UPLOADING, 100)
        
        # Start background processing
        background_tasks.add_task(
            process_document,
            processing_id,
            file_content,
            file_filename,
            output_format,
            custom_filename
        )
        
        return {"processing_id": processing_id, "message": "File uploaded and processing started"}
        
    except Exception as e:
        # Handle upload errors
        processing_status[processing_id].status = ProcessingStatusEnum.ERROR
        processing_status[processing_id].message = f"Upload failed: {str(e)}"
        print(f"Upload error for {processing_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.get("/status/{processing_id}")
async def get_processing_status(processing_id: str):
    """Get the current processing status"""
    if processing_id not in processing_status:
        raise HTTPException(status_code=404, detail="Processing ID not found")
    
    return processing_status[processing_id]

@app.get("/download/{processing_id}")
async def download_report(processing_id: str):
    """Download the generated report"""
    if processing_id not in processing_status:
        raise HTTPException(status_code=404, detail="Processing ID not found")
    
    status = processing_status[processing_id]
    if status.status != ProcessingStatusEnum.COMPLETED:
        raise HTTPException(status_code=400, detail="Processing not completed yet")
    
    if not status.download_path:
        raise HTTPException(status_code=500, detail="Download path not available")
    
    return FileResponse(
        path=status.download_path,
        filename=status.output_filename,
        media_type='application/octet-stream'
    )

@app.delete("/cleanup/{processing_id}")
async def cleanup_processing(processing_id: str):
    """Clean up temporary files and processing data"""
    if processing_id in processing_status:
        status = processing_status[processing_id]
        if status.download_path and os.path.exists(status.download_path):
            os.remove(status.download_path)
        del processing_status[processing_id]
    
    # Clean up progress tracker
    if processing_id in progress_trackers:
        del progress_trackers[processing_id]
    
    return {"message": "Cleanup completed"}

async def progress_callback(progress: int, processed_lines: int, total_lines: int, total_issues: int):
    """Callback function for progress updates during streaming processing"""
    # This can be used to update status if needed
    pass

async def process_document(processing_id: str, file_content: bytes, file_filename: str, output_format: str, custom_filename: Optional[str]):
    """Background task to process the document with optimizations for large files"""
    try:
        status = processing_status[processing_id]
        progress_tracker = progress_trackers[processing_id]
        
        # Add timeout for large file processing (30 minutes max)
        import signal
        import asyncio
        
        async def timeout_handler():
            await asyncio.sleep(1800)  # 30 minutes
            if processing_id in processing_status:
                processing_status[processing_id].status = ProcessingStatusEnum.ERROR
                processing_status[processing_id].message = "Processing timeout - file too large or complex"
        
        # Start timeout task
        timeout_task = asyncio.create_task(timeout_handler())
        
        # Update status to parsing stage
        status.status = ProcessingStatusEnum.PARSING
        status.progress = 10
        status.message = "Parsing document structure..."
        progress_tracker.start_stage(ProcessingStatusEnum.PARSING)
        
        # Update progress tracking info
        stage_info = progress_tracker.get_stage_info(ProcessingStatusEnum.PARSING, 10)
        status.current_stage = stage_info['current_stage']
        status.stage_name = stage_info['stage_name']
        status.current_stage_progress = stage_info['current_stage_progress']
        status.estimated_time_remaining = progress_tracker.get_eta(ProcessingStatusEnum.PARSING, 10)
        
        # Force status update to global dictionary
        processing_status[processing_id] = status
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file_filename)[1]) as tmp_file:
            tmp_file.write(file_content)
            tmp_file_path = tmp_file.name
        
        try:
            # Parse document
            lines = await document_parser.parse_document(tmp_file_path)
            status.progress = 30
            status.message = f"Document parsed successfully: {len(lines)} lines found"
            
            # Set total lines for ETA calculations
            progress_tracker.set_total_lines(len(lines))
            
            # Update progress tracking for parsing completion
            progress_tracker.update_stage_progress(ProcessingStatusEnum.PARSING, 100)
            stage_info = progress_tracker.get_stage_info(ProcessingStatusEnum.PARSING, 100)
            status.current_stage_progress = stage_info['current_stage_progress']
            status.estimated_time_remaining = progress_tracker.get_eta(ProcessingStatusEnum.PARSING, 100)
            
            # Force status update to global dictionary
            processing_status[processing_id] = status
            
            # Update status to grammar checking stage
            status.status = ProcessingStatusEnum.CHECKING_GRAMMAR
            status.progress = 40
            status.message = "Checking grammar and style..."
            progress_tracker.start_stage(ProcessingStatusEnum.CHECKING_GRAMMAR)
            
            # Update progress tracking info for grammar checking
            stage_info = progress_tracker.get_stage_info(ProcessingStatusEnum.CHECKING_GRAMMAR, 0)
            status.current_stage = stage_info['current_stage']
            status.stage_name = stage_info['stage_name']
            status.current_stage_progress = stage_info['current_stage_progress']
            status.estimated_time_remaining = progress_tracker.get_eta(ProcessingStatusEnum.CHECKING_GRAMMAR, 0)
            
            # Force status update to global dictionary
            processing_status[processing_id] = status
            
            # Check grammar with streaming processing (no chunks, no retries)
            issues = []
            total_lines = len(lines)
            lines_to_process = lines  # Process all lines
            
            # Log document size for monitoring
            if total_lines > 1000:
                status.message = f"Large document detected ({total_lines} lines). Processing with streaming approach for optimal performance..."
                processing_status[processing_id] = status
            
            status.message = f"Processing {len(lines_to_process)} lines with streaming approach (no chunks, no retries)..."
            processing_status[processing_id] = status
            
            # Send initial status via WebSocket if connected
            if websocket_manager.has_connection(processing_id):
                print(f"WebSocket connection found for {processing_id}, sending initial status")
                await websocket_manager.send_status_update(processing_id, "CHECKING_GRAMMAR", "Starting streaming grammar check...", 40)
            else:
                print(f"No WebSocket connection found for {processing_id}")
            
            # Process document with streaming approach
            print(f"Starting streaming processing for {len(lines_to_process)} lines")
            async for result in streaming_grammar_checker.process_document_streaming(
                lines_to_process, 
                progress_callback
            ):
                print(f"Streaming result: {result['type']}")
                if result['type'] == 'line_completed':
                    # Add issues from this line
                    issues.extend(result['issues'])
                    
                    # Update progress
                    progress = 40 + int(result['progress'] * 0.4)  # 40-80% range
                    status.progress = progress
                    status.message = f"Processed {result['processed_lines']}/{result['total_lines']} lines ({progress}% complete)"
                    
                    # Update progress tracking
                    progress_tracker.update_stage_progress(ProcessingStatusEnum.CHECKING_GRAMMAR, progress)
                    stage_info = progress_tracker.get_stage_info(ProcessingStatusEnum.CHECKING_GRAMMAR, progress)
                    status.current_stage_progress = stage_info['current_stage_progress']
                    status.estimated_time_remaining = progress_tracker.get_eta(ProcessingStatusEnum.CHECKING_GRAMMAR, progress)
                    
                    # Update status
                    processing_status[processing_id] = status
                    
                    # Send real-time update via WebSocket if connected
                    if websocket_manager.has_connection(processing_id):
                        print(f"Sending WebSocket update for line {result['line_number']}")
                        await websocket_manager.send_line_completed(
                            processing_id,
                            result['line_number'],
                            result['issues'],
                            progress,
                            result['processed_lines'],
                            result['total_lines'],
                            result['total_issues'],
                            result['skipped_sentences']
                        )
                    else:
                        print(f"No WebSocket connection for line {result['line_number']} update")
                    
                    # Yield control to allow other tasks
                    await asyncio.sleep(0.01)
                    
                elif result['type'] == 'processing_complete':
                    # Processing completed
                    status.progress = 80
                    status.message = f"Grammar checking completed: {result['total_issues']} issues found, {result['skipped_sentences']} sentences skipped"
                    
                    # Update status with issues found so far
                    status.issues = issues
                    processing_status[processing_id] = status
                    
                    # Send completion update via WebSocket if connected
                    if websocket_manager.has_connection(processing_id):
                        await websocket_manager.send_processing_complete(
                            processing_id,
                            result['total_issues'],
                            result['processed_lines'],
                            result['skipped_sentences']
                        )
                    
                    break
            
            status.progress = 80
            status.message = "Grammar checking completed"
            
            # Update progress tracking for grammar checking completion
            progress_tracker.update_stage_progress(ProcessingStatusEnum.CHECKING_GRAMMAR, 100)
            
            # Force status update to global dictionary
            processing_status[processing_id] = status
            
            # Generate summary
            summary = streaming_grammar_checker.generate_summary(issues)
            
            # Update status to report generation stage
            status.status = ProcessingStatusEnum.GENERATING_REPORT
            status.progress = 90
            status.message = "Generating report..."
            progress_tracker.start_stage(ProcessingStatusEnum.GENERATING_REPORT)
            
            # Update progress tracking info for report generation
            stage_info = progress_tracker.get_stage_info(ProcessingStatusEnum.GENERATING_REPORT, 0)
            status.current_stage = stage_info['current_stage']
            status.stage_name = stage_info['stage_name']
            status.current_stage_progress = stage_info['current_stage_progress']
            status.estimated_time_remaining = progress_tracker.get_eta(ProcessingStatusEnum.GENERATING_REPORT, 0)
            
            # Force status update to global dictionary
            processing_status[processing_id] = status
            
            # Generate report
            output_filename = custom_filename or f"grammar_report_{processing_id}"
            download_path = await report_generator.generate_report(
                issues=issues,
                summary=summary,
                original_filename=file_filename,
                output_format=output_format,
                output_filename=output_filename
            )
            
            # Update final status
            status.status = ProcessingStatusEnum.COMPLETED
            status.progress = 100
            status.message = "Report generated successfully"
            status.issues = issues
            status.summary = summary
            status.download_path = download_path
            status.output_filename = f"{output_filename}.{output_format}"
            
            # Update progress tracking for completion
            progress_tracker.update_stage_progress(ProcessingStatusEnum.GENERATING_REPORT, 100)
            stage_info = progress_tracker.get_stage_info(ProcessingStatusEnum.GENERATING_REPORT, 100)
            status.current_stage = stage_info['current_stage']
            status.stage_name = "Completed"
            status.current_stage_progress = 100
            status.estimated_time_remaining = 0
            
            # CRITICAL: Update the global processing status
            processing_status[processing_id] = status
            print(f"✅ Final status updated: {status.status}, {len(issues)} issues, {status.progress}% complete")
            
            # Send final completion message via WebSocket if connected
            if websocket_manager.has_connection(processing_id):
                await websocket_manager.send_processing_complete(
                    processing_id,
                    len(issues),
                    len(lines),
                    0  # skipped_sentences
                )
                print(f"✅ Sent final completion message via WebSocket")
            
            # Update baseline metrics based on actual processing performance
            if progress_tracker.start_time:
                total_processing_time = (datetime.now() - progress_tracker.start_time).total_seconds()
                file_size_kb = len(file_content) / 1024
                progress_tracker.update_baseline_metrics(total_processing_time, file_size_kb, len(lines))
                
                # Log processing statistics
                stats = progress_tracker.get_processing_stats()
                print(f"Processing completed: {stats['file_size_kb']:.1f}KB, {stats['total_lines']} lines, {stats['elapsed_formatted']}")
                print(f"Performance: {stats['lines_per_second']:.2f} lines/s, {stats['baseline_kb_per_second']:.2f} KB/s baseline")
            
        finally:
            # Cancel timeout task
            if 'timeout_task' in locals():
                timeout_task.cancel()
            
            # Clean up temporary file
            if os.path.exists(tmp_file_path):
                os.remove(tmp_file_path)
            
            # Force garbage collection for large files
            import gc
            gc.collect()
                
    except Exception as e:
        status = processing_status[processing_id]
        status.status = ProcessingStatusEnum.ERROR
        status.message = f"Processing failed: {str(e)}"
        print(f"Error processing document {processing_id}: {str(e)}")
        
        # Cancel timeout task on error
        if 'timeout_task' in locals():
            timeout_task.cancel()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        # Increase timeout for large file uploads
        timeout_keep_alive=600,  # 10 minutes
        # Use a more efficient worker
        workers=1,  # Single worker for file processing
        loop="asyncio"  # Use asyncio event loop
    )
