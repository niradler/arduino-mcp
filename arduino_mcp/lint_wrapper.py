import subprocess
import json
import shutil
from typing import Optional, Dict, Any
from pathlib import Path
from .platform_utils import env_config


class ArduinoLintError(Exception):
    pass


class ArduinoLint:
    def __init__(self, lint_path: Optional[str] = None):
        if lint_path:
            self.lint_path = lint_path
        else:
            self.lint_path = shutil.which(env_config.ARDUINO_LINT_PATH) or env_config.ARDUINO_LINT_PATH
    
    def is_installed(self) -> bool:
        if not self.lint_path:
            return False
        return Path(self.lint_path).exists()
    
    def get_version(self) -> Optional[str]:
        try:
            result = subprocess.run(
                [self.lint_path, "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return result.stdout.strip().split()[0]
            return None
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return None
    
    def lint_project(
        self,
        path: str,
        compliance: str = "specification",
        library_manager: Optional[str] = None
    ) -> Dict[str, Any]:
        if not self.is_installed():
            raise ArduinoLintError("Arduino Lint is not installed or not in PATH")
        
        args = [self.lint_path, "--compliance", compliance, "--format", "json", path]
        
        if library_manager:
            args = [self.lint_path, "--compliance", compliance, "--library-manager", library_manager, "--format", "json", path]
        
        try:
            result = subprocess.run(
                args,
                stdin=subprocess.DEVNULL,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore',
                timeout=60,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            )
            
            output = {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
            
            if result.stdout.strip():
                try:
                    lint_data = json.loads(result.stdout)
                    output["lint_results"] = lint_data
                except json.JSONDecodeError:
                    pass
            
            return output
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Linting operation timed out after 60 seconds",
                "returncode": -1
            }
        except FileNotFoundError:
            raise ArduinoLintError(f"Arduino Lint not found at: {self.lint_path}")
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "returncode": -1
            }
