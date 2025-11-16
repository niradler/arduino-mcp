from collections import deque
from threading import Lock
from pathlib import Path
from typing import List, Optional


class SerialBuffer:
    def __init__(self, max_size_mb: int = 10):
        max_lines = (max_size_mb * 1024 * 1024) // 100
        self.buffer = deque(maxlen=max_lines)
        self.lock = Lock()
        self.total_lines = 0
    
    def append(self, line: str):
        with self.lock:
            self.buffer.append(line)
            self.total_lines += 1
    
    def get_all(self) -> List[str]:
        with self.lock:
            return list(self.buffer)
    
    def dump_to_file(self, filepath: str):
        output_path = Path(filepath)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with self.lock:
            lines = list(self.buffer)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
    
    def clear(self):
        with self.lock:
            self.buffer.clear()
            self.total_lines = 0
    
    def get_stats(self) -> dict:
        with self.lock:
            return {
                "current_lines": len(self.buffer),
                "total_lines_captured": self.total_lines,
                "max_capacity": self.buffer.maxlen
            }

