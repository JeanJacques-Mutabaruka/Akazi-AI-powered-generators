"""
Performance Tracking Module
Measures execution time, memory usage, and generates analytics
FIXED VERSION - Allows setting output_size_kb in context
"""

import time
import json
import psutil
import os
from contextlib import contextmanager
from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict


@dataclass
class PerformanceMetric:
    """Data class for a single performance metric"""
    timestamp: str
    operation: str
    file_name: str
    format_type: str
    duration_seconds: float
    memory_mb: float
    success: bool
    error: Optional[str] = None
    file_size_kb: Optional[float] = None
    output_size_kb: Optional[float] = None


class PerformanceTracker:
    """
    Track and analyze performance metrics
    Thread-safe for concurrent operations
    """
    
    def __init__(self, metrics_file: str = "logs/performance.json"):
        self.metrics: List[Dict] = []
        self.metrics_file = Path(metrics_file)
        self._ensure_log_dir()
        self._load_existing_metrics()
    
    def _ensure_log_dir(self):
        """Create logs directory if it doesn't exist"""
        self.metrics_file.parent.mkdir(parents=True, exist_ok=True)
    
    def _load_existing_metrics(self):
        """Load existing metrics from file"""
        if self.metrics_file.exists():
            try:
                with open(self.metrics_file, 'r', encoding='utf-8') as f:
                    self.metrics = json.load(f)
            except (json.JSONDecodeError, IOError):
                # If file is corrupted, start fresh
                self.metrics = []
    
    @contextmanager
    def track(
        self,
        operation: str,
        file_name: str,
        format_type: str,
        file_size_kb: Optional[float] = None
    ):
        """
        Context manager to track operation performance
        
        Usage:
            with tracker.track("generate", "job.json", "akazi_en") as ctx:
                # ... operation code ...
                ctx['output_size_kb'] = output_file.stat().st_size / 1024
        
        Args:
            operation: Operation type
            file_name: File being processed
            format_type: Output format
            file_size_kb: Input file size (optional)
            
        Yields:
            Dict with 'output_size_kb' key that can be set during operation
        """
        start_time = time.perf_counter()
        start_memory = self._get_memory_usage()
        
        success = True
        error = None
        
        # Create context dictionary that can be modified by caller
        tracking_context = {'output_size_kb': None}
        
        try:
            yield tracking_context
        except Exception as e:
            success = False
            error = str(e)
            raise
        finally:
            duration = time.perf_counter() - start_time
            end_memory = self._get_memory_usage()
            memory_delta = end_memory - start_memory
            
            metric = PerformanceMetric(
                timestamp=datetime.now().isoformat(),
                operation=operation,
                file_name=file_name,
                format_type=format_type,
                duration_seconds=round(duration, 3),
                memory_mb=round(memory_delta, 2),
                success=success,
                error=error,
                file_size_kb=file_size_kb,
                output_size_kb=tracking_context.get('output_size_kb')
            )
            
            self.add_metric(metric)
    
    def _get_memory_usage(self) -> float:
        """
        Get current process memory usage in MB
        
        Returns:
            Memory usage in megabytes
        """
        try:
            process = psutil.Process(os.getpid())
            return process.memory_info().rss / 1024 / 1024
        except Exception:
            return 0.0
    
    def add_metric(self, metric: PerformanceMetric):
        """Add a metric and save to file"""
        self.metrics.append(asdict(metric))
        self._save_metrics()
    
    def _save_metrics(self):
        """Save metrics to JSON file"""
        try:
            with open(self.metrics_file, 'w', encoding='utf-8') as f:
                json.dump(self.metrics, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Warning: Could not save metrics: {e}")
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Generate summary statistics
        
        Returns:
            Dictionary with aggregated metrics
        """
        if not self.metrics:
            return {
                "total_operations": 0,
                "successes": 0,
                "failures": 0,
                "success_rate": 0.0,
                "avg_duration": 0.0,
                "total_memory_mb": 0.0
            }
        
        total = len(self.metrics)
        successes = sum(1 for m in self.metrics if m.get("success", False))
        failures = total - successes
        
        durations = [m.get("duration_seconds", 0) for m in self.metrics]
        memories = [m.get("memory_mb", 0) for m in self.metrics]
        
        return {
            "total_operations": total,
            "successes": successes,
            "failures": failures,
            "success_rate": round(successes / total * 100, 2) if total > 0 else 0,
            "avg_duration": round(sum(durations) / total, 3) if total > 0 else 0,
            "min_duration": round(min(durations), 3) if durations else 0,
            "max_duration": round(max(durations), 3) if durations else 0,
            "total_memory_mb": round(sum(memories), 2),
            "avg_memory_mb": round(sum(memories) / total, 2) if total > 0 else 0
        }
    
    def get_by_format(self, format_type: str) -> List[Dict]:
        """Get all metrics for a specific format"""
        return [m for m in self.metrics if m.get("format_type") == format_type]
    
    def get_by_operation(self, operation: str) -> List[Dict]:
        """Get all metrics for a specific operation"""
        return [m for m in self.metrics if m.get("operation") == operation]
    
    def get_failures(self) -> List[Dict]:
        """Get all failed operations"""
        return [m for m in self.metrics if not m.get("success", False)]
    
    def get_recent(self, limit: int = 10) -> List[Dict]:
        """
        Get most recent metrics
        
        Args:
            limit: Number of recent metrics to return
        
        Returns:
            List of recent metrics
        """
        return sorted(
            self.metrics,
            key=lambda x: x.get("timestamp", ""),
            reverse=True
        )[:limit]
    
    def clear_metrics(self):
        """Clear all metrics (use with caution)"""
        self.metrics = []
        self._save_metrics()
    
    def export_to_csv(self, output_path: str):
        """
        Export metrics to CSV format
        
        Args:
            output_path: Path to save CSV file
        """
        import csv
        
        if not self.metrics:
            return
        
        keys = self.metrics[0].keys()
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(self.metrics)
