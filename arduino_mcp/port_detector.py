import serial.tools.list_ports
from typing import List, Dict, Optional
from .platform_utils import platform_config


class PortDetector:
    @staticmethod
    def list_ports() -> List[Dict[str, str]]:
        ports = serial.tools.list_ports.comports()
        return [
            {
                "device": port.device,
                "description": port.description,
                "hwid": port.hwid,
                "vid": hex(port.vid) if port.vid else None,
                "pid": hex(port.pid) if port.pid else None,
                "serial_number": port.serial_number,
                "manufacturer": port.manufacturer,
                "product": port.product,
            }
            for port in ports
        ]
    
    @staticmethod
    def find_arduino_ports() -> List[Dict[str, str]]:
        ports = PortDetector.list_ports()
        arduino_keywords = platform_config.get_serial_keywords()
        
        arduino_ports = []
        for port in ports:
            description_lower = port["description"].lower()
            manufacturer_lower = (port["manufacturer"] or "").lower()
            device_lower = port["device"].lower()
            
            if any(keyword in description_lower or 
                   keyword in manufacturer_lower or 
                   keyword in device_lower
                   for keyword in arduino_keywords):
                arduino_ports.append(port)
        
        return arduino_ports
    
    @staticmethod
    def get_best_port() -> Optional[str]:
        arduino_ports = PortDetector.find_arduino_ports()
        
        if arduino_ports:
            priority_chips = ["cp210", "ch340", "ftdi", "arduino"]
            
            for chip in priority_chips:
                for port in arduino_ports:
                    description_lower = port["description"].lower()
                    manufacturer_lower = (port["manufacturer"] or "").lower()
                    if chip in description_lower or chip in manufacturer_lower:
                        return port["device"]
            
            return arduino_ports[0]["device"]
        
        all_ports = PortDetector.list_ports()
        if all_ports:
            return all_ports[0]["device"]
        
        return None
    
    @staticmethod
    def verify_port(port: str) -> bool:
        try:
            with serial.Serial(port, timeout=1):
                return True
        except (serial.SerialException, FileNotFoundError, PermissionError):
            return False

