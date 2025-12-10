import os
import platform
import sys
from pathlib import Path
from typing import Optional


class PlatformConfig:
    def __init__(self):
        self.os_type = platform.system()
        self.is_windows = self.os_type == "Windows"
        self.is_mac = self.os_type == "Darwin"
        self.is_linux = self.os_type == "Linux"
    
    def get_arduino_cli_name(self) -> str:
        if self.is_windows:
            return "arduino-cli.exe"
        return "arduino-cli"
    
    def get_default_arduino_paths(self) -> list[str]:
        if self.is_windows:
            return [
                "%LOCALAPPDATA%\\Arduino15",
                "%USERPROFILE%\\AppData\\Local\\Arduino15",
                "%PROGRAMFILES%\\Arduino CLI",
                "%PROGRAMFILES(X86)%\\Arduino CLI"
            ]
        elif self.is_mac:
            return [
                "~/Library/Arduino15",
                "/Applications/Arduino.app/Contents/Java",
                "/usr/local/bin"
            ]
        else:
            return [
                "~/.arduino15",
                "/usr/local/bin",
                "/usr/bin",
                "~/.local/bin"
            ]
    
    def get_port_pattern(self) -> str:
        if self.is_windows:
            return "COM*"
        elif self.is_mac:
            return "/dev/tty.*"
        else:
            return "/dev/ttyUSB*|/dev/ttyACM*"
    
    def get_serial_keywords(self) -> list[str]:
        common = ["arduino", "ch340", "cp210", "ftdi"]
        
        if self.is_windows:
            return common + ["usb serial", "silicon labs"]
        elif self.is_mac:
            return common + ["usbserial", "usbmodem"]
        else:
            return common + ["ttyUSB", "ttyACM"]
    
    def normalize_path(self, path: str) -> str:
        if self.is_windows:
            return path.replace("/", "\\")
        return path.replace("\\", "/")
    
    def get_line_ending(self) -> str:
        if self.is_windows:
            return "\r\n"
        return "\n"
    
    def supports_color_output(self) -> bool:
        if self.is_windows:
            return sys.stdout.isatty() and hasattr(sys.stdout, 'buffer')
        return sys.stdout.isatty()
    
    def get_encoding(self) -> str:
        if self.is_windows:
            return "cp1252"
        return "utf-8"
    
    def format_status(self, status: str, message: str) -> str:
        if status == "ok":
            prefix = "[OK]" if self.is_windows else "✓"
        elif status == "fail":
            prefix = "[FAIL]" if self.is_windows else "✗"
        elif status == "skip":
            prefix = "[SKIP]" if self.is_windows else "○"
        else:
            prefix = "[INFO]" if self.is_windows else "ℹ"
        
        return f"{prefix} {message}"


class EnvConfig:
    ARDUINO_CLI_PATH: str = os.getenv('ARDUINO_CLI_PATH', 'arduino-cli')
    ARDUINO_LINT_PATH: str = os.getenv('ARDUINO_LINT_PATH', 'arduino-lint')
    ARDUINO_SERIAL_BUFFER_SIZE: int = int(os.getenv('ARDUINO_SERIAL_BUFFER_SIZE', '10'))
    MCP_SKETCH_DIR: Optional[str] = os.getenv('MCP_SKETCH_DIR')
    ARDUINO_CONFIG_FILE: Optional[str] = os.getenv('ARDUINO_CONFIG_FILE')
    
    @staticmethod
    def get_default_sketch_dir() -> Path:
        if EnvConfig.MCP_SKETCH_DIR:
            return Path(EnvConfig.MCP_SKETCH_DIR).expanduser()
        
        os_type = platform.system()
        home = Path.home()
        
        if os_type == "Windows":
            documents = home / "Documents"
            return documents / "Arduino"
        elif os_type == "Darwin":
            return home / "Documents" / "Arduino"
        else:
            return home / "Arduino"
    
    @staticmethod
    def has_overrides() -> bool:
        return bool(
            os.getenv('ARDUINO_CLI_PATH') or
            os.getenv('ARDUINO_LINT_PATH') or
            os.getenv('MCP_SKETCH_DIR') or
            os.getenv('ARDUINO_SERIAL_BUFFER_SIZE') or
            os.getenv('ARDUINO_CONFIG_FILE')
        )


platform_config = PlatformConfig()
env_config = EnvConfig()

