import time
from typing import Dict, Optional
from datetime import datetime, timedelta
from models.schemas import ProcessingStatusEnum

class ProgressTracker:
    """Tracks processing progress with dynamic ETA calculation based on file size and processing speed"""
    
    def __init__(self):
        self.stage_timings: Dict[str, Dict] = {}
        self.start_time: Optional[datetime] = None
        self.current_stage_start: Optional[datetime] = None
        self.file_size_bytes: Optional[int] = None
        self.total_lines: Optional[int] = None
        self.processed_lines: int = 0
        
        # Processing speed metrics (bytes per second, lines per second)
        self.processing_speeds = {
            'bytes_per_second': 0,
            'lines_per_second': 0,
            'last_update_time': None
        }
        
        # Baseline metrics for ETA calculation (30KB reference)
        self.baseline_metrics = {
            'reference_size_kb': 30,  # 30KB baseline
            'reference_processing_time_seconds': 10,  # 10 seconds for 30KB
            'reference_lines': 50,  # ~50 lines in 30KB
            'kb_per_second': 3.0,  # 30KB / 10s = 3KB/s
            'lines_per_second': 5.0  # 50 lines / 10s = 5 lines/s
        }
        
        # Define processing stages with base durations (in seconds)
        self.stage_durations = {
            ProcessingStatusEnum.UPLOADING: 5,  # 5 seconds
            ProcessingStatusEnum.PARSING: 10,   # 10 seconds
            ProcessingStatusEnum.CHECKING_GRAMMAR: 30,  # 30 seconds (will be calculated dynamically)
            ProcessingStatusEnum.GENERATING_REPORT: 15,  # 15 seconds
        }
        
        # Stage names for display
        self.stage_names = {
            ProcessingStatusEnum.UPLOADING: "File Upload",
            ProcessingStatusEnum.PARSING: "Document Parsing",
            ProcessingStatusEnum.CHECKING_GRAMMAR: "Grammar Analysis",
            ProcessingStatusEnum.GENERATING_REPORT: "Report Generation",
        }
        
        # Total number of stages
        self.total_stages = len(self.stage_durations)
    
    def start_processing(self):
        """Start tracking processing time"""
        self.start_time = datetime.now()
        self.current_stage_start = self.start_time
        self.processing_speeds['last_update_time'] = self.start_time
    
    def set_file_size(self, file_size_bytes: int):
        """Set the file size for ETA calculations"""
        self.file_size_bytes = file_size_bytes
    
    def set_total_lines(self, total_lines: int):
        """Set the total number of lines for ETA calculations"""
        self.total_lines = total_lines
    
    def start_stage(self, stage: ProcessingStatusEnum):
        """Start tracking a new stage"""
        self.current_stage_start = datetime.now()
        if stage not in self.stage_timings:
            self.stage_timings[stage] = {
                'start_time': self.current_stage_start,
                'duration': None,
                'estimated_duration': self.stage_durations.get(stage, 10)
            }
    
    def update_stage_progress(self, stage: ProcessingStatusEnum, progress: int, total_items: int = None, current_item: int = None):
        """Update progress within a stage and calculate processing speeds"""
        if stage not in self.stage_timings:
            self.start_stage(stage)
        
        stage_info = self.stage_timings[stage]
        
        # Calculate stage progress
        if total_items and current_item:
            stage_progress = int((current_item / total_items) * 100)
            # Update processed lines for grammar checking stage
            if stage == ProcessingStatusEnum.CHECKING_GRAMMAR:
                self.processed_lines = current_item
                self._update_processing_speeds()
        else:
            stage_progress = progress
        
        # Update stage timing based on progress
        if stage_progress > 0:
            elapsed = (datetime.now() - stage_info['start_time']).total_seconds()
            if stage_progress < 100:
                # Estimate remaining time for this stage
                estimated_total = elapsed / (stage_progress / 100)
                stage_info['estimated_duration'] = estimated_total
            else:
                # Stage completed
                stage_info['duration'] = elapsed
    
    def _update_processing_speeds(self):
        """Update processing speed metrics based on current progress"""
        if not self.start_time or not self.processing_speeds['last_update_time']:
            return
        
        current_time = datetime.now()
        total_elapsed = (current_time - self.start_time).total_seconds()
        
        if total_elapsed > 0:
            # Calculate bytes per second
            if self.file_size_bytes:
                self.processing_speeds['bytes_per_second'] = self.file_size_bytes / total_elapsed
            
            # Calculate lines per second
            if self.processed_lines > 0:
                self.processing_speeds['lines_per_second'] = self.processed_lines / total_elapsed
        
        self.processing_speeds['last_update_time'] = current_time
    
    def get_eta(self, current_stage: ProcessingStatusEnum, current_progress: int) -> Optional[int]:
        """Calculate estimated time remaining in seconds using dynamic processing speeds"""
        if not self.start_time:
            return None
        
        current_time = datetime.now()
        elapsed_total = (current_time - self.start_time).total_seconds()
        
        # Use dynamic calculation for grammar checking stage
        if current_stage == ProcessingStatusEnum.CHECKING_GRAMMAR and self.total_lines and self.processed_lines > 0:
            return self._calculate_grammar_eta()
        
        # Use file size-based calculation for other stages
        if self.file_size_bytes and current_stage in [ProcessingStatusEnum.UPLOADING, ProcessingStatusEnum.PARSING]:
            return self._calculate_file_size_eta(current_stage, current_progress)
        
        # Fallback to progress-based calculation
        stage_progress = self._get_stage_progress(current_stage, current_progress)
        if stage_progress <= 0:
            return None
        
        estimated_total_time = elapsed_total / (stage_progress / 100)
        estimated_remaining = estimated_total_time - elapsed_total
        
        return max(0, int(estimated_remaining))
    
    def _calculate_grammar_eta(self) -> Optional[int]:
        """Calculate ETA for grammar checking based on actual processing speeds and baseline metrics"""
        if not self.total_lines or self.processed_lines <= 0:
            return None
        
        # Method 1: Use actual lines per second if we have enough data
        if self.processing_speeds['lines_per_second'] > 0 and self.processed_lines >= 5:
            remaining_lines = self.total_lines - self.processed_lines
            eta_seconds = remaining_lines / self.processing_speeds['lines_per_second']
            return max(0, int(eta_seconds))
        
        # Method 2: Calculate based on file size ratio and baseline metrics
        if self.file_size_bytes and self.start_time:
            elapsed_time = (datetime.now() - self.start_time).total_seconds()
            if elapsed_time > 0:
                # Calculate actual processing speed
                kb_processed = (self.processed_lines / self.total_lines) * (self.file_size_bytes / 1024)
                actual_kb_per_second = kb_processed / elapsed_time
                
                # Use actual speed if reasonable, otherwise use baseline
                if actual_kb_per_second > 0.5:  # At least 0.5KB/s
                    kb_per_second = actual_kb_per_second
                else:
                    kb_per_second = self.baseline_metrics['kb_per_second']
                
                # Calculate remaining KB and ETA
                remaining_kb = (self.file_size_bytes / 1024) - kb_processed
                eta_seconds = remaining_kb / kb_per_second
                return max(0, int(eta_seconds))
        
        # Method 3: Use baseline metrics with file size scaling
        if self.file_size_bytes:
            # Calculate file size ratio compared to baseline
            file_size_kb = self.file_size_bytes / 1024
            size_ratio = file_size_kb / self.baseline_metrics['reference_size_kb']
            
            # Adjust processing speed based on file size (larger files may be slower)
            if size_ratio > 10:  # > 300KB (10x baseline)
                speed_multiplier = 0.3  # 70% slower for very large files
            elif size_ratio > 5:  # > 150KB (5x baseline)
                speed_multiplier = 0.5  # 50% slower for large files
            elif size_ratio > 2:  # > 60KB (2x baseline)
                speed_multiplier = 0.7  # 30% slower for medium files
            else:
                speed_multiplier = 1.0  # Normal speed for small files
            
            adjusted_kb_per_second = self.baseline_metrics['kb_per_second'] * speed_multiplier
            
            # Calculate remaining work
            progress_ratio = self.processed_lines / self.total_lines
            remaining_kb = file_size_kb * (1 - progress_ratio)
            
            eta_seconds = remaining_kb / adjusted_kb_per_second
            return max(0, int(eta_seconds))
        
        return None
    
    def _calculate_file_size_eta(self, current_stage: ProcessingStatusEnum, current_progress: int) -> Optional[int]:
        """Calculate ETA based on file size and baseline processing speeds"""
        if not self.file_size_bytes:
            return None
        
        # Base processing speeds (KB per second) - calibrated from 30KB baseline
        base_speeds = {
            ProcessingStatusEnum.UPLOADING: 1000,  # 1MB/s upload (fast)
            ProcessingStatusEnum.PARSING: 50,      # 50KB/s parsing (medium)
            ProcessingStatusEnum.GENERATING_REPORT: 20,  # 20KB/s report generation (slower)
        }
        
        base_speed = base_speeds.get(current_stage, 10)
        
        # Calculate file size ratio compared to baseline (30KB)
        file_size_kb = self.file_size_bytes / 1024
        size_ratio = file_size_kb / self.baseline_metrics['reference_size_kb']
        
        # Adjust speed based on file size (larger files may be slower)
        if size_ratio > 20:  # > 600KB (20x baseline)
            speed_multiplier = 0.2  # 80% slower for very large files
        elif size_ratio > 10:  # > 300KB (10x baseline)
            speed_multiplier = 0.4  # 60% slower for large files
        elif size_ratio > 5:  # > 150KB (5x baseline)
            speed_multiplier = 0.6  # 40% slower for medium-large files
        elif size_ratio > 2:  # > 60KB (2x baseline)
            speed_multiplier = 0.8  # 20% slower for medium files
        else:
            speed_multiplier = 1.0  # Normal speed for small files
        
        adjusted_speed = base_speed * speed_multiplier
        
        # Calculate remaining time
        kb_remaining = (self.file_size_bytes / 1024) * (100 - current_progress) / 100
        eta_seconds = kb_remaining / adjusted_speed
        
        return max(0, int(eta_seconds))
    
    def _get_stage_progress(self, current_stage: ProcessingStatusEnum, current_progress: int) -> float:
        """Calculate overall progress through all stages"""
        stage_order = [
            ProcessingStatusEnum.UPLOADING,
            ProcessingStatusEnum.PARSING,
            ProcessingStatusEnum.CHECKING_GRAMMAR,
            ProcessingStatusEnum.GENERATING_REPORT
        ]
        
        try:
            current_stage_index = stage_order.index(current_stage)
        except ValueError:
            return 0
        
        # Calculate progress through completed stages
        completed_stages_progress = (current_stage_index / len(stage_order)) * 100
        
        # Calculate progress within current stage
        current_stage_progress = (current_progress / 100) * (100 / len(stage_order))
        
        return completed_stages_progress + current_stage_progress
    
    def get_stage_info(self, current_stage: ProcessingStatusEnum, current_progress: int) -> Dict:
        """Get detailed stage information"""
        stage_order = [
            ProcessingStatusEnum.UPLOADING,
            ProcessingStatusEnum.PARSING,
            ProcessingStatusEnum.CHECKING_GRAMMAR,
            ProcessingStatusEnum.GENERATING_REPORT
        ]
        
        try:
            current_stage_index = stage_order.index(current_stage)
        except ValueError:
            current_stage_index = 0
        
        return {
            'current_stage': current_stage_index + 1,
            'total_stages': len(stage_order),
            'stage_name': self.stage_names.get(current_stage, current_stage.value),
            'current_stage_progress': current_progress,
            'overall_progress': int(self._get_stage_progress(current_stage, current_progress))
        }
    
    def format_eta(self, seconds: int) -> str:
        """Format ETA in human-readable format"""
        if seconds <= 0:
            return "Almost done"
        
        if seconds < 60:
            return f"{seconds} seconds"
        elif seconds < 3600:
            minutes = seconds // 60
            remaining_seconds = seconds % 60
            if remaining_seconds == 0:
                return f"{minutes} minute{'s' if minutes != 1 else ''}"
            else:
                return f"{minutes}m {remaining_seconds}s"
        else:
            hours = seconds // 3600
            remaining_minutes = (seconds % 3600) // 60
            if remaining_minutes == 0:
                return f"{hours} hour{'s' if hours != 1 else ''}"
            else:
                return f"{hours}h {remaining_minutes}m"
    
    def update_baseline_metrics(self, actual_processing_time: float, file_size_kb: float, total_lines: int):
        """Update baseline metrics based on actual processing performance"""
        if actual_processing_time > 0 and file_size_kb > 0:
            # Calculate actual speeds
            actual_kb_per_second = file_size_kb / actual_processing_time
            actual_lines_per_second = total_lines / actual_processing_time if total_lines > 0 else 0
            
            # Update baseline metrics (weighted average with existing values)
            weight = 0.3  # 30% weight for new data, 70% for existing baseline
            self.baseline_metrics['kb_per_second'] = (
                self.baseline_metrics['kb_per_second'] * (1 - weight) + 
                actual_kb_per_second * weight
            )
            self.baseline_metrics['lines_per_second'] = (
                self.baseline_metrics['lines_per_second'] * (1 - weight) + 
                actual_lines_per_second * weight
            )
            
            print(f"Updated baseline metrics: {actual_kb_per_second:.2f} KB/s, {actual_lines_per_second:.2f} lines/s")
    
    def get_processing_stats(self) -> Dict:
        """Get current processing statistics for monitoring"""
        stats = {
            'file_size_kb': self.file_size_bytes / 1024 if self.file_size_bytes else 0,
            'total_lines': self.total_lines or 0,
            'processed_lines': self.processed_lines,
            'lines_per_second': round(self.processing_speeds['lines_per_second'], 2),
            'bytes_per_second': round(self.processing_speeds['bytes_per_second'], 2),
            'baseline_kb_per_second': round(self.baseline_metrics['kb_per_second'], 2),
            'baseline_lines_per_second': round(self.baseline_metrics['lines_per_second'], 2),
        }
        
        if self.start_time:
            elapsed = (datetime.now() - self.start_time).total_seconds()
            stats['elapsed_seconds'] = round(elapsed, 2)
            stats['elapsed_formatted'] = self.format_eta(int(elapsed))
            
            # Calculate estimated total time based on baseline
            if self.file_size_bytes and self.total_lines:
                file_size_kb = self.file_size_bytes / 1024
                estimated_total_time = file_size_kb / self.baseline_metrics['kb_per_second']
                stats['estimated_total_time'] = round(estimated_total_time, 2)
                stats['estimated_total_formatted'] = self.format_eta(int(estimated_total_time))
        
        return stats
