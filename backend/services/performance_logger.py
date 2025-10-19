"""
Performance logging system for monitoring and optimizing the grammar checker
"""

import time
import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path
import asyncio

class PerformanceLogger:
    """
    Comprehensive performance logging system to track processing times,
    API usage, and identify bottlenecks for optimization
    """
    
    def __init__(self, log_dir: str = "logs/performance"):
        """
        Initialize performance logger
        
        Args:
            log_dir: Directory to store performance logs
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Current session data
        self.current_task: Optional[Dict[str, Any]] = None
        self.stage_timers: Dict[str, float] = {}
        self.api_calls: List[Dict[str, Any]] = []
        self.category_stats: Dict[str, Dict[str, Any]] = {}
        
        # Session-wide statistics
        self.session_stats = {
            "session_start": datetime.now().isoformat(),
            "total_tasks": 0,
            "total_processing_time": 0.0,
            "total_api_calls": 0,
            "total_api_cost": 0.0,
            "errors": []
        }
    
    def start_task(self, task_id: str, filename: str, file_size: int, categories: List[str], ai_mode: Dict[str, bool]) -> None:
        """
        Start tracking a new task
        
        Args:
            task_id: Unique task identifier
            filename: Document filename
            file_size: File size in bytes
            categories: List of enabled categories
            ai_mode: Dict with llm_enhancement and llm_detection flags
        """
        self.current_task = {
            "task_id": task_id,
            "filename": filename,
            "file_size": file_size,
            "file_size_mb": file_size / (1024 * 1024),
            "categories_enabled": categories,
            "categories_count": len(categories) if categories else 13,  # Default all
            "ai_enhancement": ai_mode.get("enhancement", False),
            "ai_detection": ai_mode.get("detection", False),
            "start_time": time.time(),
            "start_datetime": datetime.now().isoformat(),
            "stages": {},
            "api_calls": [],
            "category_stats": {},
            "errors": []
        }
        self.stage_timers = {}
        self.api_calls = []
        self.category_stats = {}
        
        print(f"[PerfLog] Started task {task_id}: {filename} ({file_size/1024:.1f} KB)")
    
    def start_stage(self, stage_name: str) -> None:
        """
        Start timing a processing stage
        
        Args:
            stage_name: Name of the stage (parsing, checking, generating, etc.)
        """
        if not self.current_task:
            return
        
        self.stage_timers[stage_name] = time.time()
        print(f"[PerfLog] Stage '{stage_name}' started")
    
    def end_stage(self, stage_name: str, metadata: Optional[Dict[str, Any]] = None) -> float:
        """
        End timing a processing stage
        
        Args:
            stage_name: Name of the stage
            metadata: Optional metadata about the stage (lines processed, issues found, etc.)
            
        Returns:
            Duration of the stage in seconds
        """
        if not self.current_task or stage_name not in self.stage_timers:
            return 0.0
        
        start_time = self.stage_timers[stage_name]
        duration = time.time() - start_time
        
        self.current_task["stages"][stage_name] = {
            "duration_seconds": duration,
            "metadata": metadata or {}
        }
        
        print(f"[PerfLog] Stage '{stage_name}' completed in {duration:.3f}s")
        
        return duration
    
    def log_api_call(
        self, 
        api_type: str, 
        model: str, 
        tokens_used: Optional[int] = None,
        cost: Optional[float] = None,
        duration: Optional[float] = None,
        success: bool = True,
        error: Optional[str] = None
    ) -> None:
        """
        Log an API call (LLM detection, enhancement, etc.)
        
        Args:
            api_type: Type of API call (detection, enhancement, etc.)
            model: Model used (gpt-4o-mini, gpt-4o, etc.)
            tokens_used: Number of tokens consumed
            cost: Cost of the API call
            duration: Duration in seconds
            success: Whether the call succeeded
            error: Error message if failed
        """
        if not self.current_task:
            return
        
        api_call = {
            "timestamp": datetime.now().isoformat(),
            "type": api_type,
            "model": model,
            "tokens_used": tokens_used,
            "cost": cost,
            "duration_seconds": duration,
            "success": success,
            "error": error
        }
        
        self.api_calls.append(api_call)
        self.current_task["api_calls"].append(api_call)
        
        if cost:
            self.session_stats["total_api_cost"] += cost
        self.session_stats["total_api_calls"] += 1
        
        status = "✓" if success else "✗"
        cost_str = f"${cost:.4f}" if cost else "N/A"
        print(f"[PerfLog] API {status} [{api_type}] {model} - {cost_str}")
    
    def log_category_performance(self, category: str, issues_found: int, duration: float) -> None:
        """
        Log performance for a specific category
        
        Args:
            category: Category name
            issues_found: Number of issues found in this category
            duration: Time taken to check this category
        """
        if not self.current_task:
            return
        
        self.category_stats[category] = {
            "issues_found": issues_found,
            "duration_seconds": duration
        }
        
        self.current_task["category_stats"][category] = self.category_stats[category]
    
    def log_error(self, error_type: str, error_message: str, stage: Optional[str] = None) -> None:
        """
        Log an error that occurred during processing
        
        Args:
            error_type: Type of error
            error_message: Error message
            stage: Stage where error occurred (optional)
        """
        error_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": error_type,
            "message": error_message,
            "stage": stage
        }
        
        if self.current_task:
            self.current_task["errors"].append(error_entry)
        
        self.session_stats["errors"].append(error_entry)
        
        print(f"[PerfLog] ERROR [{error_type}] {error_message}")
    
    def end_task(self, results_metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        End tracking current task and generate performance report
        
        Args:
            results_metadata: Optional metadata about results (issues found, etc.)
            
        Returns:
            Performance data for the task
        """
        if not self.current_task:
            return {}
        
        # Calculate total duration
        total_duration = time.time() - self.current_task["start_time"]
        self.current_task["total_duration_seconds"] = total_duration
        self.current_task["end_datetime"] = datetime.now().isoformat()
        
        # Add results metadata
        if results_metadata:
            self.current_task["results"] = results_metadata
        
        # Calculate derived metrics
        self.current_task["metrics"] = self._calculate_metrics()
        
        # Update session stats
        self.session_stats["total_tasks"] += 1
        self.session_stats["total_processing_time"] += total_duration
        
        # Save to file
        self._save_task_log()
        
        # Generate summary
        summary = self._generate_task_summary()
        
        print(f"[PerfLog] Task completed in {total_duration:.2f}s - Log saved")
        
        # Clear current task
        task_data = self.current_task
        self.current_task = None
        
        return task_data
    
    def _calculate_metrics(self) -> Dict[str, Any]:
        """Calculate derived performance metrics"""
        if not self.current_task:
            return {}
        
        total_duration = self.current_task["total_duration_seconds"]
        file_size_mb = self.current_task["file_size_mb"]
        
        # Calculate stage percentages
        stage_percentages = {}
        for stage, data in self.current_task["stages"].items():
            percentage = (data["duration_seconds"] / total_duration) * 100 if total_duration > 0 else 0
            stage_percentages[stage] = f"{percentage:.1f}%"
        
        # Calculate processing speed
        lines_processed = 0
        issues_found = 0
        if "results" in self.current_task and self.current_task["results"]:
            issues_found = self.current_task["results"].get("total_issues", 0)
            lines_processed = self.current_task["results"].get("lines_with_issues", 0)
        
        metrics = {
            "total_duration": f"{total_duration:.2f}s",
            "mb_per_second": f"{file_size_mb / total_duration if total_duration > 0 else 0:.4f}",
            "seconds_per_mb": f"{total_duration / file_size_mb if file_size_mb > 0 else 0:.2f}",
            "stage_percentages": stage_percentages,
            "api_call_count": len(self.current_task["api_calls"]),
            "api_success_rate": self._calculate_api_success_rate(),
            "total_api_cost": sum(call.get("cost", 0) for call in self.current_task["api_calls"]),
            "cost_per_mb": self._calculate_cost_per_mb(),
            "issues_found": issues_found,
            "issues_per_second": f"{issues_found / total_duration if total_duration > 0 else 0:.2f}",
            "error_count": len(self.current_task["errors"])
        }
        
        return metrics
    
    def _calculate_api_success_rate(self) -> str:
        """Calculate API call success rate"""
        if not self.current_task or not self.current_task["api_calls"]:
            return "N/A"
        
        total_calls = len(self.current_task["api_calls"])
        successful_calls = sum(1 for call in self.current_task["api_calls"] if call.get("success", False))
        
        rate = (successful_calls / total_calls) * 100 if total_calls > 0 else 0
        return f"{rate:.1f}%"
    
    def _calculate_cost_per_mb(self) -> str:
        """Calculate cost per MB processed"""
        if not self.current_task:
            return "N/A"
        
        total_cost = sum(call.get("cost", 0) for call in self.current_task["api_calls"])
        file_size_mb = self.current_task["file_size_mb"]
        
        if file_size_mb > 0:
            return f"${total_cost / file_size_mb:.4f}"
        return "N/A"
    
    def _save_task_log(self) -> None:
        """Save task log to file"""
        if not self.current_task:
            return
        
        # Create timestamped filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        task_id = self.current_task["task_id"][:8]  # Short ID
        filename = f"task_{timestamp}_{task_id}.json"
        filepath = self.log_dir / filename
        
        # Save as JSON
        with open(filepath, 'w') as f:
            json.dump(self.current_task, f, indent=2)
        
        # Also append to daily summary log
        self._append_to_daily_summary()
    
    def _append_to_daily_summary(self) -> None:
        """Append task summary to daily summary file"""
        if not self.current_task:
            return
        
        date_str = datetime.now().strftime("%Y%m%d")
        summary_file = self.log_dir / f"daily_summary_{date_str}.jsonl"
        
        # Create summary entry (one line per task)
        summary = {
            "timestamp": self.current_task["start_datetime"],
            "task_id": self.current_task["task_id"],
            "filename": self.current_task["filename"],
            "file_size_mb": self.current_task["file_size_mb"],
            "total_duration": self.current_task["total_duration_seconds"],
            "ai_enhancement": self.current_task["ai_enhancement"],
            "ai_detection": self.current_task["ai_detection"],
            "categories_count": self.current_task["categories_count"],
            "api_calls": len(self.current_task["api_calls"]),
            "api_cost": self.current_task["metrics"]["total_api_cost"],
            "issues_found": self.current_task["metrics"]["issues_found"],
            "errors": len(self.current_task["errors"])
        }
        
        # Append as JSON line
        with open(summary_file, 'a') as f:
            f.write(json.dumps(summary) + '\n')
    
    def _generate_task_summary(self) -> str:
        """Generate human-readable summary"""
        if not self.current_task:
            return ""
        
        metrics = self.current_task["metrics"]
        
        summary = f"""
Performance Summary for Task {self.current_task['task_id']}
{'='*70}
File: {self.current_task['filename']} ({self.current_task['file_size_mb']:.2f} MB)
Total Duration: {metrics['total_duration']}
Speed: {metrics['mb_per_second']} MB/s

Stages:
"""
        for stage, data in self.current_task["stages"].items():
            duration = data["duration_seconds"]
            percentage = metrics["stage_percentages"].get(stage, "0%")
            summary += f"  • {stage}: {duration:.3f}s ({percentage})\n"
        
        summary += f"""
API Usage:
  • Total calls: {metrics['api_call_count']}
  • Success rate: {metrics['api_success_rate']}
  • Total cost: ${metrics['total_api_cost']:.4f}
  • Cost per MB: {metrics['cost_per_mb']}

Results:
  • Issues found: {metrics['issues_found']}
  • Issues per second: {metrics['issues_per_second']}
  • Errors: {metrics['error_count']}
"""
        
        return summary
    
    def get_bottlenecks(self, threshold_percentage: float = 20.0) -> List[Dict[str, Any]]:
        """
        Identify performance bottlenecks (stages taking > threshold% of total time)
        
        Args:
            threshold_percentage: Percentage threshold for identifying bottlenecks
            
        Returns:
            List of bottleneck stages with details
        """
        if not self.current_task or "stages" not in self.current_task:
            return []
        
        bottlenecks = []
        total_duration = self.current_task["total_duration_seconds"]
        
        for stage, data in self.current_task["stages"].items():
            duration = data["duration_seconds"]
            percentage = (duration / total_duration) * 100 if total_duration > 0 else 0
            
            if percentage > threshold_percentage:
                bottlenecks.append({
                    "stage": stage,
                    "duration_seconds": duration,
                    "percentage": percentage,
                    "recommendation": self._get_optimization_recommendation(stage, percentage)
                })
        
        return bottlenecks
    
    def _get_optimization_recommendation(self, stage: str, percentage: float) -> str:
        """Get optimization recommendation for a bottleneck stage"""
        recommendations = {
            "parsing": "Consider using faster document parser or caching parsed results",
            "checking": "Optimize pattern matching or reduce enabled categories",
            "llm_detection": "Reduce LLM calls - use selective detection or batch processing",
            "llm_enhancement": "Batch more issues per API call or reduce enhancement scope",
            "generating": "Optimize report generation or use simpler templates"
        }
        
        base_rec = recommendations.get(stage, "Profile this stage for specific bottlenecks")
        
        if percentage > 50:
            return f"CRITICAL: {base_rec} (taking {percentage:.1f}% of total time)"
        elif percentage > 30:
            return f"HIGH: {base_rec} (taking {percentage:.1f}% of total time)"
        else:
            return f"MODERATE: {base_rec} (taking {percentage:.1f}% of total time)"
    
    def generate_session_report(self) -> str:
        """
        Generate session-wide performance report
        
        Returns:
            Human-readable session report
        """
        session_duration = (datetime.now() - datetime.fromisoformat(self.session_stats["session_start"])).total_seconds()
        
        avg_processing_time = (
            self.session_stats["total_processing_time"] / self.session_stats["total_tasks"]
            if self.session_stats["total_tasks"] > 0
            else 0
        )
        
        report = f"""
Session Performance Report
{'='*70}
Session Duration: {session_duration:.1f}s
Total Tasks: {self.session_stats['total_tasks']}
Average Processing Time: {avg_processing_time:.2f}s per task

API Usage:
  • Total API calls: {self.session_stats['total_api_calls']}
  • Total cost: ${self.session_stats['total_api_cost']:.4f}
  • Average cost per task: ${self.session_stats['total_api_cost'] / self.session_stats['total_tasks'] if self.session_stats['total_tasks'] > 0 else 0:.4f}

Errors: {len(self.session_stats['errors'])}
"""
        
        return report
    
    def export_analytics(self, output_file: Optional[str] = None) -> str:
        """
        Export analytics data for analysis
        
        Args:
            output_file: Optional output filepath (defaults to timestamped file)
            
        Returns:
            Path to exported file
        """
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = str(self.log_dir / f"analytics_{timestamp}.json")
        
        # Read all daily summaries
        all_tasks = []
        for summary_file in self.log_dir.glob("daily_summary_*.jsonl"):
            with open(summary_file, 'r') as f:
                for line in f:
                    all_tasks.append(json.loads(line))
        
        # Generate analytics
        analytics = {
            "generated_at": datetime.now().isoformat(),
            "total_tasks": len(all_tasks),
            "session_stats": self.session_stats,
            "tasks": all_tasks,
            "summary": self._calculate_aggregate_stats(all_tasks)
        }
        
        with open(output_file, 'w') as f:
            json.dump(analytics, f, indent=2)
        
        print(f"[PerfLog] Analytics exported to {output_file}")
        return output_file
    
    def _calculate_aggregate_stats(self, tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate aggregate statistics across all tasks"""
        if not tasks:
            return {}
        
        total_duration = sum(t.get("total_duration", 0) for t in tasks)
        total_api_calls = sum(t.get("api_calls", 0) for t in tasks)
        total_cost = sum(t.get("api_cost", 0) for t in tasks)
        total_issues = sum(t.get("issues_found", 0) for t in tasks)
        total_size = sum(t.get("file_size_mb", 0) for t in tasks)
        
        # Count by AI mode
        ai_enhancement_tasks = sum(1 for t in tasks if t.get("ai_enhancement", False))
        ai_detection_tasks = sum(1 for t in tasks if t.get("ai_detection", False))
        pattern_only_tasks = sum(1 for t in tasks if not t.get("ai_enhancement", False))
        
        return {
            "total_tasks": len(tasks),
            "total_duration_seconds": total_duration,
            "average_duration": total_duration / len(tasks) if tasks else 0,
            "total_size_mb": total_size,
            "total_api_calls": total_api_calls,
            "average_api_calls_per_task": total_api_calls / len(tasks) if tasks else 0,
            "total_cost": total_cost,
            "average_cost_per_task": total_cost / len(tasks) if tasks else 0,
            "cost_per_mb": total_cost / total_size if total_size > 0 else 0,
            "total_issues_found": total_issues,
            "average_issues_per_task": total_issues / len(tasks) if tasks else 0,
            "mode_distribution": {
                "pattern_only": pattern_only_tasks,
                "ai_enhancement": ai_enhancement_tasks,
                "ai_detection": ai_detection_tasks
            }
        }
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """
        Get current task performance summary
        
        Returns:
            Dict with performance metrics
        """
        if not self.current_task:
            return {}
        
        return {
            "task_id": self.current_task.get("task_id"),
            "duration_so_far": time.time() - self.current_task["start_time"],
            "stages_completed": list(self.current_task["stages"].keys()),
            "api_calls": len(self.current_task["api_calls"]),
            "errors": len(self.current_task["errors"])
        }


# Global instance for easy access
_performance_logger = None

def get_performance_logger() -> PerformanceLogger:
    """Get or create global performance logger instance"""
    global _performance_logger
    if _performance_logger is None:
        _performance_logger = PerformanceLogger()
    return _performance_logger

