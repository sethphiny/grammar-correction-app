"""
Progress tracking service for monitoring document processing
"""

from typing import Dict, Any
from enum import Enum

class ProcessingStatus(Enum):
    UPLOADED = "uploaded"
    PARSING = "parsing"
    CHECKING = "checking"
    GENERATING = "generating"
    COMPLETED = "completed"
    ERROR = "error"

class ProgressTracker:
    """Service for tracking and managing processing progress"""
    
    def __init__(self):
        self.status_messages = {
            ProcessingStatus.UPLOADED: "Document uploaded successfully",
            ProcessingStatus.PARSING: "Parsing document structure and extracting text",
            ProcessingStatus.CHECKING: "Analyzing grammar and style issues",
            ProcessingStatus.GENERATING: "Generating correction report",
            ProcessingStatus.COMPLETED: "Report generated successfully",
            ProcessingStatus.ERROR: "An error occurred during processing"
        }
    
    def get_status_message(self, status: str) -> str:
        """
        Get human-readable status message
        
        Args:
            status: Processing status string
            
        Returns:
            Human-readable status message
        """
        try:
            status_enum = ProcessingStatus(status)
            return self.status_messages.get(status_enum, "Unknown status")
        except ValueError:
            return "Unknown status"
    
    def get_progress_percentage(self, status: str, current_step: int = 0, total_steps: int = 1) -> int:
        """
        Calculate progress percentage based on status and current step
        
        Args:
            status: Current processing status
            current_step: Current step number
            total_steps: Total number of steps
            
        Returns:
            Progress percentage (0-100)
        """
        status_progress = {
            ProcessingStatus.UPLOADED: 0,
            ProcessingStatus.PARSING: 10,
            ProcessingStatus.CHECKING: 30,
            ProcessingStatus.GENERATING: 80,
            ProcessingStatus.COMPLETED: 100,
            ProcessingStatus.ERROR: 0
        }
        
        try:
            status_enum = ProcessingStatus(status)
            base_progress = status_progress.get(status_enum, 0)
            
            # Add step-based progress for checking phase
            if status_enum == ProcessingStatus.CHECKING and total_steps > 0:
                step_progress = int((current_step / total_steps) * 50)  # 30-80% range
                return min(base_progress + step_progress, 80)
            
            return base_progress
            
        except ValueError:
            return 0
    
    def update_task_progress(
        self, 
        task_data: Dict[str, Any], 
        status: str, 
        progress: int = None,
        error: str = None
    ) -> Dict[str, Any]:
        """
        Update task progress information
        
        Args:
            task_data: Current task data
            status: New status
            progress: Optional progress percentage
            error: Optional error message
            
        Returns:
            Updated task data
        """
        task_data["status"] = status
        task_data["message"] = self.get_status_message(status)
        
        if progress is not None:
            task_data["progress"] = progress
        else:
            task_data["progress"] = self.get_progress_percentage(status)
        
        if error:
            task_data["error"] = error
            task_data["status"] = ProcessingStatus.ERROR.value
        
        return task_data
    
    def get_estimated_time_remaining(self, status: str, progress: int) -> str:
        """
        Get estimated time remaining based on current progress
        
        Args:
            status: Current processing status
            progress: Current progress percentage
            
        Returns:
            Human-readable time estimate
        """
        if status == ProcessingStatus.COMPLETED.value:
            return "Completed"
        
        if status == ProcessingStatus.ERROR.value:
            return "Error occurred"
        
        # Rough time estimates based on typical processing times
        if progress < 10:
            return "Starting processing..."
        elif progress < 30:
            return "Parsing document... (1-2 minutes remaining)"
        elif progress < 80:
            return "Checking grammar... (2-3 minutes remaining)"
        elif progress < 100:
            return "Generating report... (30 seconds remaining)"
        else:
            return "Almost done..."
    
    def create_progress_callback(self, task_id: str, task_storage: Dict[str, Dict[str, Any]]):
        """
        Create a progress callback function for a specific task
        
        Args:
            task_id: Task identifier
            task_storage: Storage dictionary for task data
            
        Returns:
            Callback function for progress updates
        """
        def progress_callback(progress: int, status: str = None, message: str = None):
            if task_id in task_storage:
                task_data = task_storage[task_id]
                
                if status:
                    task_data["status"] = status
                
                if message:
                    task_data["message"] = message
                else:
                    task_data["message"] = self.get_status_message(task_data.get("status", status))
                
                task_data["progress"] = progress
                task_data["estimated_time"] = self.get_estimated_time_remaining(
                    task_data.get("status", status), progress
                )
        
        return progress_callback
