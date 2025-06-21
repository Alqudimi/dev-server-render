import redis
import json
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor
from models.task import Task

class TaskQueue:
    def __init__(self, redis_conn):
        self.redis = redis_conn
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.task_callbacks = {}

    def enqueue(self, task_type: str, payload: Dict[str, Any]) -> str:
        """Add a new task to the queue"""
        task_id = str(uuid.uuid4())
        task = Task(
            id=task_id,
            type=task_type,
            payload=payload,
            status="queued",
            created_at=datetime.now()
        )
        
        self.redis.rpush("task_queue", task.json())
        self.redis.hset(f"task:{task_id}", mapping=task.dict())
        
        return task_id

    def register_handler(self, task_type: str, handler):
        """Register a handler for a task type"""
        self.task_callbacks[task_type] = handler

    def process_tasks(self):
        """Process tasks from the queue"""
        while True:
            _, task_json = self.redis.blpop("task_queue", timeout=30)
            if not task_json:
                continue
                
            task = Task.parse_raw(task_json)
            self._update_task_status(task.id, "processing")
            
            try:
                if task.type in self.task_callbacks:
                    self.executor.submit(
                        self._execute_task,
                        task,
                        self.task_callbacks[task.type]
                    )
                else:
                    self._update_task_status(task.id, "failed", "No handler registered")
            except Exception as e:
                self._update_task_status(task.id, "failed", str(e))

    def _execute_task(self, task: Task, handler):
        """Execute a task with its handler"""
        try:
            result = handler(task.payload)
            self._update_task_status(
                task.id,
                "completed",
                result=result
            )
        except Exception as e:
            self._update_task_status(
                task.id,
                "failed",
                error=str(e)
            )

    def _update_task_status(self, task_id: str, status: str, 
                          error: Optional[str] = None, result: Any = None):
        """Update task status in Redis"""
        updates = {
            "status": status,
            "updated_at": datetime.now().isoformat()
        }
        
        if error:
            updates["error"] = error
        if result:
            updates["result"] = json.dumps(result)
        
        self.redis.hset(f"task:{task_id}", mapping=updates)

    def get_task(self, task_id: str) -> Optional[Task]:
        """Get task details"""
        task_data = self.redis.hgetall(f"task:{task_id}")
        if not task_data:
            return None
        return Task(**task_data)
