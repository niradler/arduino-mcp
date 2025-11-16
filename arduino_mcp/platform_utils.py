import platform
import sys
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


platform_config = PlatformConfig()

