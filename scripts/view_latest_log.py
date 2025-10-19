#!/usr/bin/env python3
"""
View Latest Performance Log
Quick utility to view the most recent performance log
"""

import json
from pathlib import Path
import sys


def view_latest_log(log_dir: str = "logs/performance"):
    """View the latest performance log"""
    log_path = Path(log_dir)
    
    if not log_path.exists():
        print(f"❌ Log directory not found: {log_dir}")
        print(f"\nProcess a document first to generate logs.")
        return
    
    # Find most recent task log
    task_logs = sorted(log_path.glob("task_*.json"), key=lambda x: x.stat().st_mtime, reverse=True)
    
    if not task_logs:
        print(f"❌ No performance logs found in {log_dir}")
        print(f"\nProcess a document first to generate logs.")
        return
    
    latest_log = task_logs[0]
    
    try:
        with open(latest_log, 'r') as f:
            data = json.load(f)
        
        print("=" * 80)
        print(f"LATEST PERFORMANCE LOG: {latest_log.name}")
        print("=" * 80)
        
        # Basic info
        print(f"\n📄 Document:")
        print(f"   File: {data.get('filename', 'N/A')}")
        print(f"   Size: {data.get('file_size_mb', 0):.2f} MB")
        print(f"   Task ID: {data.get('task_id', 'N/A')}")
        print(f"   Timestamp: {data.get('start_datetime', 'N/A')}")
        
        # Configuration
        print(f"\n⚙️  Configuration:")
        print(f"   Categories: {data.get('categories_count', 0)} ({', '.join(data.get('categories_enabled', [])[:5]) if data.get('categories_enabled') else 'All'}...)")
        print(f"   AI Enhancement: {'✅ Yes' if data.get('ai_enhancement') else '❌ No'}")
        print(f"   AI Detection: {'✅ Yes' if data.get('ai_detection') else '❌ No'}")
        
        # Performance
        metrics = data.get('metrics', {})
        print(f"\n⚡ Performance:")
        print(f"   Total Duration: {metrics.get('total_duration', 'N/A')}")
        print(f"   Processing Speed: {metrics.get('mb_per_second', 'N/A')} MB/s")
        print(f"   Issues Found: {metrics.get('issues_found', 0)}")
        print(f"   Issues/Second: {metrics.get('issues_per_second', 'N/A')}")
        
        # Stages
        print(f"\n📊 Stage Breakdown:")
        stages = data.get('stages', {})
        for stage, stage_data in stages.items():
            duration = stage_data.get('duration_seconds', 0)
            percentage = metrics.get('stage_percentages', {}).get(stage, '0%')
            print(f"   • {stage}: {duration:.3f}s ({percentage})")
        
        # API Usage
        if data.get('api_calls'):
            print(f"\n🤖 API Usage:")
            print(f"   Total Calls: {metrics.get('api_call_count', 0)}")
            print(f"   Success Rate: {metrics.get('api_success_rate', 'N/A')}")
            print(f"   Total Cost: ${metrics.get('total_api_cost', 0):.4f}")
            print(f"   Cost/MB: {metrics.get('cost_per_mb', 'N/A')}")
        
        # Errors
        errors = data.get('errors', [])
        if errors:
            print(f"\n❌ Errors ({len(errors)}):")
            for error in errors:
                print(f"   • [{error.get('type', 'Unknown')}] {error.get('message', 'N/A')}")
        
        # Bottlenecks
        total_duration = data.get('total_duration_seconds', 1)
        bottlenecks = []
        for stage, stage_data in stages.items():
            duration = stage_data.get('duration_seconds', 0)
            percentage = (duration / total_duration) * 100 if total_duration > 0 else 0
            if percentage > 25:
                bottlenecks.append((stage, duration, percentage))
        
        if bottlenecks:
            print(f"\n⚠️  Bottlenecks (>25% of time):")
            for stage, duration, percentage in sorted(bottlenecks, key=lambda x: x[2], reverse=True):
                print(f"   • {stage}: {duration:.2f}s ({percentage:.1f}%)")
        
        print("\n" + "=" * 80)
        print("✅ Log viewed successfully")
        print("=" * 80)
        print(f"\nFull log available at: {latest_log}")
        print(f"Run 'python3 scripts/analyze_performance.py' for aggregate analysis\n")
        
    except Exception as e:
        print(f"❌ Error reading log: {e}")


if __name__ == "__main__":
    view_latest_log()

