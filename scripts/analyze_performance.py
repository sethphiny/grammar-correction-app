#!/usr/bin/env python3
"""
Performance Log Analyzer
Analyzes performance logs and generates optimization recommendations
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from typing import List, Dict, Any

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


def load_all_logs(log_dir: str = "logs/performance") -> List[Dict[str, Any]]:
    """Load all performance logs"""
    log_path = Path(log_dir)
    
    if not log_path.exists():
        print(f"❌ Log directory not found: {log_dir}")
        return []
    
    logs = []
    
    # Load individual task logs
    for log_file in sorted(log_path.glob("task_*.json")):
        try:
            with open(log_file, 'r') as f:
                logs.append(json.load(f))
        except Exception as e:
            print(f"Warning: Could not load {log_file}: {e}")
    
    return logs


def analyze_performance(logs: List[Dict[str, Any]]) -> None:
    """Analyze performance logs and generate report"""
    if not logs:
        print("No logs found to analyze")
        return
    
    print("=" * 80)
    print("PERFORMANCE ANALYSIS REPORT")
    print("=" * 80)
    print(f"\nAnalyzing {len(logs)} tasks...\n")
    
    # 1. Overall Statistics
    print("="*80)
    print("1. OVERALL STATISTICS")
    print("="*80)
    
    total_duration = sum(log.get("total_duration_seconds", 0) for log in logs)
    total_size = sum(log.get("file_size_mb", 0) for log in logs)
    total_cost = sum(log.get("metrics", {}).get("total_api_cost", 0) for log in logs)
    total_issues = sum(log.get("results", {}).get("total_issues", 0) for log in logs)
    
    print(f"Total tasks: {len(logs)}")
    print(f"Total processing time: {total_duration:.2f}s ({total_duration/60:.2f} minutes)")
    print(f"Total data processed: {total_size:.2f} MB")
    print(f"Total API cost: ${total_cost:.4f}")
    print(f"Total issues found: {total_issues}")
    print(f"\nAverages:")
    print(f"  • Duration per task: {total_duration/len(logs):.2f}s")
    print(f"  • Size per task: {total_size/len(logs):.3f} MB")
    print(f"  • Cost per task: ${total_cost/len(logs):.4f}")
    print(f"  • Issues per task: {total_issues/len(logs):.1f}")
    print(f"  • Processing speed: {total_size/total_duration if total_duration > 0 else 0:.3f} MB/s")
    print(f"  • Cost per MB: ${total_cost/total_size if total_size > 0 else 0:.4f}/MB")
    
    # 2. Stage Analysis
    print("\n" + "="*80)
    print("2. STAGE PERFORMANCE BREAKDOWN")
    print("="*80)
    
    stage_stats = defaultdict(lambda: {"total_time": 0, "count": 0})
    
    for log in logs:
        for stage, data in log.get("stages", {}).items():
            stage_stats[stage]["total_time"] += data.get("duration_seconds", 0)
            stage_stats[stage]["count"] += 1
    
    print(f"\n{'Stage':<20} {'Avg Time':<12} {'Total Time':<12} {'Count':<8} {'% of Total'}")
    print("-" * 80)
    
    for stage, stats in sorted(stage_stats.items(), key=lambda x: x[1]["total_time"], reverse=True):
        avg_time = stats["total_time"] / stats["count"] if stats["count"] > 0 else 0
        percentage = (stats["total_time"] / total_duration) * 100 if total_duration > 0 else 0
        print(f"{stage:<20} {avg_time:>10.3f}s  {stats['total_time']:>10.2f}s  {stats['count']:>6}  {percentage:>6.1f}%")
    
    # 3. Bottleneck Detection
    print("\n" + "="*80)
    print("3. BOTTLENECK ANALYSIS")
    print("="*80)
    
    # Find stages taking > 30% of total time on average
    bottlenecks = []
    for stage, stats in stage_stats.items():
        avg_time = stats["total_time"] / stats["count"] if stats["count"] > 0 else 0
        avg_total = total_duration / len(logs)
        percentage = (avg_time / avg_total) * 100 if avg_total > 0 else 0
        
        if percentage > 30:
            bottlenecks.append({
                "stage": stage,
                "avg_time": avg_time,
                "percentage": percentage
            })
    
    if bottlenecks:
        print("\n⚠️  Detected bottlenecks (>30% of processing time):\n")
        for bn in sorted(bottlenecks, key=lambda x: x["percentage"], reverse=True):
            print(f"  • {bn['stage']}: {bn['avg_time']:.2f}s ({bn['percentage']:.1f}% of total)")
            print(f"    → Recommendation: {get_recommendation(bn['stage'])}\n")
    else:
        print("\n✅ No major bottlenecks detected!")
    
    # 4. AI Usage Analysis
    print("=" * 80)
    print("4. AI USAGE ANALYSIS")
    print("="*80)
    
    ai_enhancement_count = sum(1 for log in logs if log.get("ai_enhancement", False))
    ai_detection_count = sum(1 for log in logs if log.get("ai_detection", False))
    pattern_only_count = sum(1 for log in logs if not log.get("ai_enhancement", False))
    
    print(f"\nMode distribution:")
    print(f"  • Pattern-only: {pattern_only_count} tasks ({pattern_only_count/len(logs)*100:.1f}%)")
    print(f"  • AI Enhancement: {ai_enhancement_count} tasks ({ai_enhancement_count/len(logs)*100:.1f}%)")
    print(f"  • AI Detection: {ai_detection_count} tasks ({ai_detection_count/len(logs)*100:.1f}%)")
    
    total_api_calls = sum(len(log.get("api_calls", [])) for log in logs)
    print(f"\nAPI calls:")
    print(f"  • Total: {total_api_calls}")
    print(f"  • Average per task: {total_api_calls/len(logs):.1f}")
    print(f"  • Total cost: ${total_cost:.4f}")
    print(f"  • Average cost: ${total_cost/len(logs):.4f}")
    
    # 5. Error Analysis
    print("\n" + "="*80)
    print("5. ERROR ANALYSIS")
    print("="*80)
    
    total_errors = sum(len(log.get("errors", [])) for log in logs)
    tasks_with_errors = sum(1 for log in logs if len(log.get("errors", [])) > 0)
    
    print(f"\nTotal errors: {total_errors}")
    print(f"Tasks with errors: {tasks_with_errors} ({tasks_with_errors/len(logs)*100:.1f}%)")
    print(f"Success rate: {(len(logs)-tasks_with_errors)/len(logs)*100:.1f}%")
    
    if total_errors > 0:
        error_types = defaultdict(int)
        for log in logs:
            for error in log.get("errors", []):
                error_type = error.get("type", "Unknown")
                error_types[error_type] += 1
        
        print(f"\nError breakdown:")
        for error_type, count in sorted(error_types.items(), key=lambda x: x[1], reverse=True):
            print(f"  • {error_type}: {count} occurrences")
    
    # 6. Category Performance
    print("\n" + "="*80)
    print("6. CATEGORY PERFORMANCE")
    print("="*80)
    
    category_issues = defaultdict(int)
    for log in logs:
        for category, count in log.get("results", {}).get("categories", {}).items():
            category_issues[category] += count
    
    if category_issues:
        print(f"\nIssues found by category (across all tasks):")
        for category, count in sorted(category_issues.items(), key=lambda x: x[1], reverse=True):
            avg_per_task = count / len(logs)
            print(f"  • {category}: {count} total ({avg_per_task:.1f} avg per task)")
    
    # 7. Recommendations
    print("\n" + "="*80)
    print("7. OPTIMIZATION RECOMMENDATIONS")
    print("="*80)
    
    recommendations = []
    
    # Check average processing time
    avg_duration = total_duration / len(logs)
    if avg_duration > 60:
        recommendations.append(f"HIGH: Average processing time is {avg_duration:.1f}s - Consider optimization")
    
    # Check API costs
    avg_cost = total_cost / len(logs) if len(logs) > 0 else 0
    if avg_cost > 0.10:
        recommendations.append(f"MODERATE: Average API cost is ${avg_cost:.4f} - Consider batch optimization")
    
    # Check error rate
    error_rate = (tasks_with_errors / len(logs)) * 100 if len(logs) > 0 else 0
    if error_rate > 10:
        recommendations.append(f"HIGH: Error rate is {error_rate:.1f}% - Investigate error causes")
    
    # Check bottlenecks
    if bottlenecks:
        for bn in bottlenecks:
            if bn["percentage"] > 50:
                recommendations.append(f"CRITICAL: {bn['stage']} stage takes {bn['percentage']:.1f}% of time")
    
    if recommendations:
        print("\n⚠️  Action items:")
        for i, rec in enumerate(recommendations, 1):
            print(f"  {i}. {rec}")
    else:
        print("\n✅ System is running optimally!")
    
    print("\n" + "="*80)
    print("END OF REPORT")
    print("="*80)


def get_recommendation(stage: str) -> str:
    """Get optimization recommendation for a stage"""
    recommendations = {
        "parsing": "Optimize document parser or cache parsed results",
        "checking": "Profile pattern matching, consider selective category checking",
        "llm_detection": "Reduce API calls with better filtering or batch processing",
        "llm_enhancement": "Batch more issues per call or cache common enhancements",
        "generating": "Optimize report templates or use faster PDF/DOCX generation"
    }
    return recommendations.get(stage, "Profile this stage for optimization opportunities")


def export_csv_report(logs: List[Dict[str, Any]], output_file: str = "logs/performance/analysis.csv") -> None:
    """Export simplified CSV report for spreadsheet analysis"""
    import csv
    
    if not logs:
        print("No logs to export")
        return
    
    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f)
        
        # Header
        writer.writerow([
            'Task ID', 'Filename', 'File Size (MB)', 'Duration (s)',
            'AI Enhancement', 'AI Detection', 'Categories Count',
            'Issues Found', 'API Calls', 'API Cost ($)',
            'Parsing (s)', 'Checking (s)', 'Generating (s)', 'Errors'
        ])
        
        # Data rows
        for log in logs:
            writer.writerow([
                log.get('task_id', '')[:8],
                log.get('filename', ''),
                f"{log.get('file_size_mb', 0):.3f}",
                f"{log.get('total_duration_seconds', 0):.2f}",
                log.get('ai_enhancement', False),
                log.get('ai_detection', False),
                log.get('categories_count', 0),
                log.get('results', {}).get('total_issues', 0),
                len(log.get('api_calls', [])),
                f"{log.get('metrics', {}).get('total_api_cost', 0):.4f}",
                f"{log.get('stages', {}).get('parsing', {}).get('duration_seconds', 0):.2f}",
                f"{log.get('stages', {}).get('checking', {}).get('duration_seconds', 0):.2f}",
                f"{log.get('stages', {}).get('generating', {}).get('duration_seconds', 0):.2f}",
                len(log.get('errors', []))
            ])
    
    print(f"✅ CSV report exported to: {output_file}")


def main():
    """Main analysis function"""
    log_dir = os.path.join(os.path.dirname(__file__), '..', 'logs', 'performance')
    
    print(f"Loading logs from: {log_dir}\n")
    
    logs = load_all_logs(log_dir)
    
    if not logs:
        print("❌ No performance logs found!")
        print(f"\nLogs will be created in: {log_dir}")
        print("Process some documents first, then run this script again.\n")
        return
    
    # Analyze
    analyze_performance(logs)
    
    # Export CSV
    csv_path = os.path.join(log_dir, "analysis.csv")
    export_csv_report(logs, csv_path)
    
    print(f"\n📊 Full data available in:")
    print(f"   • JSON logs: {log_dir}/task_*.json")
    print(f"   • Daily summaries: {log_dir}/daily_summary_*.jsonl")
    print(f"   • CSV export: {csv_path}")
    print(f"\n💡 Use CSV file for spreadsheet analysis and visualization\n")


if __name__ == "__main__":
    main()

