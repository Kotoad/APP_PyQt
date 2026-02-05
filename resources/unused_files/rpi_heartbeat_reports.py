"""
RPi Heartbeat Reports - Real-time execution monitoring
Sends complete execution reports every 0.5 seconds via stdout (for SSH streaming)
"""

import json
import time
import threading
from dataclasses import dataclass, asdict
from enum import Enum
from typing import Dict, List, Optional, Any


class BlockStatus(Enum):
    """Block execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    ERROR = "error"


@dataclass
class BlockExecution:
    """Single block execution record"""
    block_id: str
    block_type: str
    status: str = "pending"
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    duration: Optional[float] = None

    def to_dict(self):
        return {
            "block_id": self.block_id,
            "block_type": self.block_type,
            "status": self.status,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration": self.duration
        }


@dataclass
class VariableSnapshot:
    """Variable state snapshot"""
    name: str
    value: str
    type: str
    timestamp: float


class HeartbeatGenerator:
    """
    Background thread that sends complete execution reports every 0.5 seconds.
    
    Usage:
        hb = HeartbeatGenerator(total_blocks=10)
        hb.start_execution()
        
        hb.record_block_start("b1", "If")
        hb.record_variable("counter", 5, "INT")
        hb.record_device("GPIO17", "HIGH")
        hb.record_block_end("b1")
        
        hb.end_execution()
    """

    def __init__(self, total_blocks: int):
        """
        Initialize HeartbeatGenerator
        
        Args:
            total_blocks: Total number of blocks in execution
        """
        self.total_blocks = total_blocks
        self.start_time = None
        self.running = False
        self.heartbeat_thread = None
        
        # Shared state (accessed by both threads)
        self.blocks: Dict[str, BlockExecution] = {}
        self.variables: Dict[str, VariableSnapshot] = {}
        self.devices: Dict[str, Any] = {}
        self.errors: List[str] = []
        self.execution_state = "idle"

    def start_execution(self):
        """Start background heartbeat thread"""
        self.start_time = time.time()
        self.running = True
        self.execution_state = "running"
        self.errors = []
        
        # Start background thread
        self.heartbeat_thread = threading.Thread(target=self._heartbeat_worker, daemon=True)
        self.heartbeat_thread.start()
        
        # Send initial heartbeat
        self._send_heartbeat()

    def _heartbeat_worker(self):
        """Background thread: send heartbeat every 0.5s"""
        while self.running:
            time.sleep(0.5)
            if self.running:
                self._send_heartbeat()

    def _send_heartbeat(self):
        """Generate and send complete JSON heartbeat"""
        try:
            heartbeat = self._generate_heartbeat()
            json_str = json.dumps(heartbeat)
            print(json_str, flush=True)
        except Exception as e:
            self.record_error(f"Heartbeat generation error: {str(e)}")

    def _generate_heartbeat(self) -> Dict[str, Any]:
        """Generate complete heartbeat report"""
        current_time = time.time() - self.start_time if self.start_time else 0
        
        # Count completed blocks
        executed_blocks = sum(
            1 for b in self.blocks.values() 
            if b.status == "completed"
        )
        
        # Calculate progress
        progress = (executed_blocks / self.total_blocks * 100) if self.total_blocks > 0 else 0
        progress = min(100, max(0, progress))  # Clamp 0-100
        
        # Convert blocks to dict format
        blocks_list = [block.to_dict() for block in self.blocks.values()]
        
        # Convert variables to dict format
        variables_dict = {
            name: {
                "name": var.name,
                "value": var.value,
                "type": var.type,
                "timestamp": var.timestamp
            }
            for name, var in self.variables.items()
        }
        
        return {
            "type": "execution_heartbeat",
            "timestamp": round(current_time, 3),
            "progress": round(progress, 1),
            "total_blocks": self.total_blocks,
            "executed_blocks": executed_blocks,
            "execution_duration": round(current_time, 3),
            "blocks": blocks_list,
            "variables": variables_dict,
            "devices": self.devices,
            "errors": self.errors
        }

    def record_block_start(self, block_id: str, block_type: str):
        """Record block execution start"""
        current_time = time.time() - self.start_time if self.start_time else 0
        
        self.blocks[block_id] = BlockExecution(
            block_id=block_id,
            block_type=block_type,
            status="running",
            start_time=round(current_time, 3)
        )

    def record_block_end(self, block_id: str):
        """Record block execution end"""
        if block_id in self.blocks:
            current_time = time.time() - self.start_time if self.start_time else 0
            block = self.blocks[block_id]
            block.end_time = round(current_time, 3)
            block.status = "completed"
            
            if block.start_time is not None:
                block.duration = round(block.end_time - block.start_time, 3)

    def record_variable(self, name: str, value: Any, var_type: str = ""):
        """Record variable change"""
        current_time = time.time() - self.start_time if self.start_time else 0
        
        self.variables[name] = VariableSnapshot(
            name=name,
            value=str(value),
            type=var_type,
            timestamp=round(current_time, 3)
        )

    def record_device(self, name: str, state: Any):
        """Record device state change"""
        self.devices[name] = str(state)

    def record_error(self, error_message: str):
        """Record error"""
        current_time = time.time() - self.start_time if self.start_time else 0
        self.errors.append({
            "message": error_message,
            "timestamp": round(current_time, 3)
        })

    def end_execution(self):
        """End execution and stop heartbeat thread"""
        self.running = False
        self.execution_state = "completed"
        
        # Send final heartbeat
        try:
            self._send_heartbeat()
        except Exception as e:
            print(json.dumps({
                "type": "error",
                "message": f"Final heartbeat error: {str(e)}"
            }), flush=True)
        
        # Wait for thread to finish (with timeout)
        if self.heartbeat_thread:
            self.heartbeat_thread.join(timeout=1.0)


class HeartbeatParser:
    """Parse heartbeat JSON from stdout"""
    
    @staticmethod
    def is_heartbeat_line(line: str) -> bool:
        """Check if line is a valid heartbeat JSON"""
        try:
            data = json.loads(line)
            return data.get("type") == "execution_heartbeat"
        except (json.JSONDecodeError, AttributeError):
            return False

    @staticmethod
    def parse_line(line: str) -> Optional[Dict[str, Any]]:
        """Parse heartbeat line to dict"""
        try:
            data = json.loads(line)
            if data.get("type") == "execution_heartbeat":
                return data
        except json.JSONDecodeError:
            pass
        return None


# Example usage for testing
if __name__ == "__main__":
    print("Testing HeartbeatGenerator...")
    
    hb = HeartbeatGenerator(total_blocks=3)
    hb.start_execution()
    
    # Simulate execution
    hb.record_block_start("b1", "Setup")
    hb.record_variable("counter", 0, "INT")
    time.sleep(0.2)
    hb.record_block_end("b1")
    
    hb.record_block_start("b2", "Loop")
    for i in range(3):
        hb.record_variable("counter", i, "INT")
        time.sleep(0.3)
    hb.record_block_end("b2")
    
    hb.record_block_start("b3", "Cleanup")
    hb.record_device("LED", "OFF")
    time.sleep(0.1)
    hb.record_block_end("b3")
    
    hb.end_execution()
    
    print("Test complete!")