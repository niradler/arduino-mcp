import subprocess
import json
from typing import Optional, List, Dict, Any
from pathlib import Path


class ArduinoCLIError(Exception):
    pass


class ArduinoCLI:
    def __init__(self, cli_path: str = "arduino-cli"):
        self.cli_path = cli_path
    
    def run_command(self, args: List[str], check_installation: bool = True) -> Dict[str, Any]:
        if check_installation and not self.is_installed():
            raise ArduinoCLIError("Arduino CLI is not installed or not in PATH")
        
        try:
            result = subprocess.run(
                [self.cli_path] + args,
                capture_output=True,
                text=True,
                check=True
            )
            return {
                "success": True,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": 0
            }
        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "stdout": e.stdout,
                "stderr": e.stderr,
                "returncode": e.returncode,
                "error": str(e)
            }
        except FileNotFoundError:
            raise ArduinoCLIError(f"Arduino CLI not found at: {self.cli_path}")
    
    def is_installed(self) -> bool:
        try:
            result = subprocess.run(
                [self.cli_path, "version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def get_version(self) -> Optional[str]:
        result = self.run_command(["version"])
        if result["success"]:
            return result["stdout"].strip()
        return None
    
    def get_help(self, command: Optional[str] = None) -> str:
        args = ["--help"] if command is None else [command, "--help"]
        result = self.run_command(args, check_installation=False)
        return result["stdout"] if result["success"] else result["stderr"]
    
    def board_list(self) -> Dict[str, Any]:
        result = self.run_command(["board", "list", "--format", "json"])
        if result["success"]:
            try:
                return json.loads(result["stdout"])
            except json.JSONDecodeError:
                return {"error": "Failed to parse JSON", "raw": result["stdout"]}
        return result
    
    def core_list(self) -> Dict[str, Any]:
        result = self.run_command(["core", "list", "--format", "json"])
        if result["success"]:
            try:
                return json.loads(result["stdout"])
            except json.JSONDecodeError:
                return {"error": "Failed to parse JSON", "raw": result["stdout"]}
        return result
    
    def core_search(self, query: str) -> Dict[str, Any]:
        result = self.run_command(["core", "search", query, "--format", "json"])
        if result["success"]:
            try:
                return json.loads(result["stdout"])
            except json.JSONDecodeError:
                return {"error": "Failed to parse JSON", "raw": result["stdout"]}
        return result
    
    def core_install(self, core: str) -> Dict[str, Any]:
        return self.run_command(["core", "install", core])
    
    def lib_search(self, query: str) -> Dict[str, Any]:
        result = self.run_command(["lib", "search", query, "--format", "json"])
        if result["success"]:
            try:
                return json.loads(result["stdout"])
            except json.JSONDecodeError:
                return {"error": "Failed to parse JSON", "raw": result["stdout"]}
        return result
    
    def lib_install(self, library: str) -> Dict[str, Any]:
        return self.run_command(["lib", "install", library])
    
    def lib_list(self) -> Dict[str, Any]:
        result = self.run_command(["lib", "list", "--format", "json"])
        if result["success"]:
            try:
                stdout = result.get("stdout", "")
                if stdout and stdout.strip():
                    return json.loads(stdout)
                else:
                    return {"installed_libraries": []}
            except json.JSONDecodeError:
                return {"error": "Failed to parse JSON", "raw": result.get("stdout", "")}
        return result
    
    def compile(self, sketch_path: str, fqbn: str) -> Dict[str, Any]:
        return self.run_command(["compile", "--fqbn", fqbn, sketch_path])
    
    def upload(self, sketch_path: str, fqbn: str, port: str) -> Dict[str, Any]:
        return self.run_command(["upload", "--fqbn", fqbn, "--port", port, sketch_path])
    
    def sketch_new(self, sketch_name: str, path: Optional[str] = None) -> Dict[str, Any]:
        args = ["sketch", "new", sketch_name]
        if path:
            args.extend(["--sketch-dir", path])
        return self.run_command(args)
    
    def monitor(self, port: str, config: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        args = ["monitor", "--port", port]
        if config:
            for key, value in config.items():
                args.extend([f"--{key}", value])
        return self.run_command(args)
    
    def config_init(self) -> Dict[str, Any]:
        return self.run_command(["config", "init"])
    
    def cache_clean(self) -> Dict[str, Any]:
        return self.run_command(["cache", "clean"])

