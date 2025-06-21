from prometheus_client import start_http_server, Counter, Gauge, Histogram
import psutil
import asyncio

# Metrics definitions
API_REQUESTS = Counter(
    'api_requests_total',
    'Total number of API requests',
    ['endpoint', 'method', 'status']
)

API_LATENCY = Histogram(
    'api_request_latency_seconds',
    'API request latency in seconds',
    ['endpoint', 'method']
)

SYSTEM_CPU_USAGE = Gauge(
    'system_cpu_usage_percent',
    'Current system CPU usage percent'
)

SYSTEM_MEMORY_USAGE = Gauge(
    'system_memory_usage_percent',
    'Current system memory usage percent'
)

PROCESS_COUNT = Gauge(
    'running_processes_count',
    'Number of currently running processes'
)

def start_monitoring(port=8001):
    """Start Prometheus metrics server"""
    start_http_server(port)
    
async def update_system_metrics():
    """Update system metrics periodically"""
    while True:
        # Get CPU usage
        cpu_percent = psutil.cpu_percent()
        SYSTEM_CPU_USAGE.set(cpu_percent)
        
        # Get memory usage
        mem = psutil.virtual_memory()
        SYSTEM_MEMORY_USAGE.set(mem.percent)
        
        await asyncio.sleep(5)
