#!/usr/bin/env python3
"""
Health Check Endpoint for Tender Scraper Engine

Provides HTTP health check endpoint for monitoring and alerting.

Usage:
    python scripts/health_check.py

Endpoints:
    GET /health          - Basic health check
    GET /health/detailed - Detailed system status
    GET /metrics         - Prometheus-compatible metrics

Run on startup:
    nohup python scripts/health_check.py &

Or use systemd service (recommended for production)
"""

import os
import sys
import sqlite3
import psutil
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, PlainTextResponse
import uvicorn
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
APP_DIR = Path(__file__).parent.parent
DB_PATH = APP_DIR / "data" / "tender_scraper.db"
LOG_DIR = APP_DIR / "data" / "logs"
PORT = int(os.getenv("HEALTH_CHECK_PORT", "8000"))

# Initialize FastAPI app
app = FastAPI(
    title="Tender Scraper Health Check",
    description="Health monitoring endpoint for tender scraper",
    version="1.0.0"
)


##############################################################################
# Health Check Functions
##############################################################################

def check_database() -> Dict[str, Any]:
    """Check database connectivity and status."""
    try:
        if not DB_PATH.exists():
            return {
                "status": "unhealthy",
                "error": "Database file not found"
            }
        
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        
        # Check if tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        if not tables:
            return {
                "status": "unhealthy",
                "error": "No tables found in database"
            }
        
        # Get tender count
        cursor.execute("SELECT COUNT(*) FROM tenders")
        total_tenders = cursor.fetchone()[0]
        
        # Get today's count
        today = datetime.now().date().isoformat()
        cursor.execute("SELECT COUNT(*) FROM tenders WHERE DATE(created_at) = ?", (today,))
        today_tenders = cursor.fetchone()[0]
        
        # Get last scrape time
        cursor.execute("SELECT MAX(created_at) FROM tenders")
        last_scrape = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "status": "healthy",
            "total_tenders": total_tenders,
            "today_tenders": today_tenders,
            "last_scrape": last_scrape,
            "tables": len(tables)
        }
    
    except Exception as e:
        # Log the actual error but return sanitized message to users
        import logging
        logging.error(f"Database check failed: {e}")
        return {
            "status": "unhealthy",
            "error": "Database check failed"
        }


def check_disk_space() -> Dict[str, Any]:
    """Check available disk space."""
    try:
        disk = psutil.disk_usage(str(APP_DIR))
        
        return {
            "status": "healthy" if disk.percent < 90 else "warning",
            "total_gb": round(disk.total / (1024**3), 2),
            "used_gb": round(disk.used / (1024**3), 2),
            "free_gb": round(disk.free / (1024**3), 2),
            "percent_used": disk.percent
        }
    
    except Exception as e:
        import logging
        logging.error(f"Disk space check failed: {e}")
        return {
            "status": "unhealthy",
            "error": "Disk space check failed"
        }


def check_memory() -> Dict[str, Any]:
    """Check system memory usage."""
    try:
        memory = psutil.virtual_memory()
        
        return {
            "status": "healthy" if memory.percent < 90 else "warning",
            "total_gb": round(memory.total / (1024**3), 2),
            "available_gb": round(memory.available / (1024**3), 2),
            "percent_used": memory.percent
        }
    
    except Exception as e:
        import logging
        logging.error(f"Memory check failed: {e}")
        return {
            "status": "unhealthy",
            "error": "Memory check failed"
        }


def check_logs() -> Dict[str, Any]:
    """Check recent log activity."""
    try:
        if not LOG_DIR.exists():
            return {
                "status": "warning",
                "message": "Log directory not found"
            }
        
        log_files = list(LOG_DIR.glob("*.log"))
        
        if not log_files:
            return {
                "status": "warning",
                "message": "No log files found"
            }
        
        # Get most recent log file
        recent_log = max(log_files, key=lambda p: p.stat().st_mtime)
        modified_time = datetime.fromtimestamp(recent_log.stat().st_mtime)
        age_hours = (datetime.now() - modified_time).total_seconds() / 3600
        
        # Check for errors in recent log
        error_count = 0
        try:
            with open(recent_log, 'r') as f:
                last_lines = f.readlines()[-100:]  # Last 100 lines
                error_count = sum(1 for line in last_lines if 'ERROR' in line or 'FATAL' in line)
        except:
            pass
        
        return {
            "status": "healthy" if age_hours < 48 else "warning",
            "latest_log": recent_log.name,
            "last_modified": modified_time.isoformat(),
            "age_hours": round(age_hours, 2),
            "recent_errors": error_count
        }
    
    except Exception as e:
        import logging
        logging.error(f"Log check failed: {e}")
        return {
            "status": "unhealthy",
            "error": "Log check failed"
        }


def check_scraper_process() -> Dict[str, Any]:
    """Check if scraper process is running."""
    try:
        lock_file = APP_DIR / "scraper.lock"
        
        if lock_file.exists():
            with open(lock_file, 'r') as f:
                pid = int(f.read().strip())
            
            if psutil.pid_exists(pid):
                try:
                    process = psutil.Process(pid)
                    return {
                        "status": "running",
                        "pid": pid,
                        "started": datetime.fromtimestamp(process.create_time()).isoformat(),
                        "cpu_percent": process.cpu_percent(interval=0.1),
                        "memory_mb": round(process.memory_info().rss / (1024**2), 2)
                    }
                except:
                    pass
        
        return {
            "status": "idle",
            "message": "No active scraper process"
        }
    
    except Exception as e:
        import logging
        logging.error(f"Scraper process check failed: {e}")
        return {
            "status": "unknown",
            "error": "Process check failed"
        }


##############################################################################
# API Endpoints
##############################################################################

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "Tender Scraper Health Check",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "detailed": "/health/detailed",
            "metrics": "/metrics"
        }
    }


@app.get("/health")
async def health_check():
    """Basic health check endpoint."""
    db_status = check_database()
    disk_status = check_disk_space()
    
    # Determine overall status
    overall_healthy = (
        db_status.get("status") == "healthy" and
        disk_status.get("status") in ["healthy", "warning"]
    )
    
    if overall_healthy:
        return JSONResponse(
            status_code=200,
            content={
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "database": db_status.get("status"),
                "disk": disk_status.get("status")
            }
        )
    else:
        # Sanitize error messages for unhealthy status
        db_error = db_status.get("error", "Unknown error") if db_status.get("status") != "healthy" else None
        disk_error = disk_status.get("error", "Unknown error") if disk_status.get("status") not in ["healthy", "warning"] else None
        
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "timestamp": datetime.now().isoformat(),
                "database": {"status": db_status.get("status"), "error": db_error} if db_error else db_status.get("status"),
                "disk": {"status": disk_status.get("status"), "error": disk_error} if disk_error else disk_status.get("status")
            }
        )


@app.get("/health/detailed")
async def detailed_health():
    """
    Detailed health check with all system metrics.
    
    WARNING: This endpoint exposes detailed system information and should be
    restricted to internal monitoring systems only. Use firewall rules or 
    authentication to prevent public access.
    """
    db_status = check_database()
    disk_status = check_disk_space()
    memory_status = check_memory()
    logs_status = check_logs()
    scraper_status = check_scraper_process()
    
    overall_healthy = (
        db_status.get("status") == "healthy" and
        disk_status.get("status") in ["healthy", "warning"] and
        memory_status.get("status") in ["healthy", "warning"]
    )
    
    # Sanitize error messages for external exposure
    def sanitize_status(status_dict):
        """Remove detailed error traces from status dict."""
        sanitized = status_dict.copy()
        if "error" in sanitized and sanitized.get("status") in ["unhealthy", "warning"]:
            # Keep the error message but ensure it's generic
            pass  # Already sanitized in check functions
        return sanitized
    
    return JSONResponse(
        status_code=200 if overall_healthy else 503,
        content={
            "status": "healthy" if overall_healthy else "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "uptime": get_uptime(),
            "database": sanitize_status(db_status),
            "disk": sanitize_status(disk_status),
            "memory": sanitize_status(memory_status),
            "logs": sanitize_status(logs_status),
            "scraper_process": sanitize_status(scraper_status)
        }
    )


@app.get("/metrics", response_class=PlainTextResponse)
async def metrics():
    """Prometheus-compatible metrics endpoint."""
    db_status = check_database()
    disk_status = check_disk_space()
    memory_status = check_memory()
    scraper_status = check_scraper_process()
    
    metrics_output = []
    
    # Database metrics
    if "total_tenders" in db_status:
        metrics_output.append(f"tender_scraper_total_tenders {db_status['total_tenders']}")
        metrics_output.append(f"tender_scraper_today_tenders {db_status['today_tenders']}")
    
    # Disk metrics
    if "percent_used" in disk_status:
        metrics_output.append(f"tender_scraper_disk_percent {disk_status['percent_used']}")
        metrics_output.append(f"tender_scraper_disk_free_gb {disk_status['free_gb']}")
    
    # Memory metrics
    if "percent_used" in memory_status:
        metrics_output.append(f"tender_scraper_memory_percent {memory_status['percent_used']}")
        metrics_output.append(f"tender_scraper_memory_available_gb {memory_status['available_gb']}")
    
    # Scraper process metrics
    if scraper_status["status"] == "running":
        metrics_output.append(f"tender_scraper_process_running 1")
        if "cpu_percent" in scraper_status:
            metrics_output.append(f"tender_scraper_cpu_percent {scraper_status['cpu_percent']}")
        if "memory_mb" in scraper_status:
            metrics_output.append(f"tender_scraper_memory_mb {scraper_status['memory_mb']}")
    else:
        metrics_output.append(f"tender_scraper_process_running 0")
    
    return "\n".join(metrics_output) + "\n"


##############################################################################
# Utility Functions
##############################################################################

def get_uptime() -> str:
    """Get system uptime."""
    try:
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        uptime = datetime.now() - boot_time
        days = uptime.days
        hours = uptime.seconds // 3600
        minutes = (uptime.seconds % 3600) // 60
        return f"{days}d {hours}h {minutes}m"
    except:
        return "unknown"


##############################################################################
# Main Execution
##############################################################################

def main():
    """Run health check server."""
    print("="*80)
    print("TENDER SCRAPER HEALTH CHECK SERVICE")
    print("="*80)
    print(f"Port: {PORT}")
    print(f"Database: {DB_PATH}")
    print(f"Log directory: {LOG_DIR}")
    print("")
    print("Endpoints:")
    print(f"  http://localhost:{PORT}/health          - Basic health check")
    print(f"  http://localhost:{PORT}/health/detailed - Detailed status")
    print(f"  http://localhost:{PORT}/metrics         - Prometheus metrics")
    print("="*80)
    print("")
    
    # Run server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=PORT,
        log_level="info",
        access_log=True
    )


if __name__ == "__main__":
    main()
