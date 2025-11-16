import subprocess
import os
from pathlib import Path
from typing import Optional, Dict, Literal


class ImageConverter:
    DEFAULTS = {
        "monochrome": {
            "threshold": "50%",
            "depth": "1",
            "description": "1-bit black/white for OLED (SSD1306, SH1106) and monochrome E-ink displays"
        },
        "grayscale_2bit": {
            "colors": "4",
            "depth": "2",
            "description": "2-bit grayscale (4 levels) for E-paper displays like WaveShare 4.3\""
        },
        "grayscale_4bit": {
            "colors": "16",
            "depth": "4",
            "description": "4-bit grayscale (16 levels) for advanced E-ink displays"
        },
        "grayscale": {
            "depth": "8",
            "description": "8-bit grayscale (256 levels) for high-quality E-ink"
        },
        "rgb565": {
            "description": "16-bit color for TFT displays (ILI9341, ST7735, ST7789)"
        },
        "rgb888": {
            "description": "24-bit true color for NeoPixel/WS2812B LEDs and high-color displays"
        }
    }
    
    @staticmethod
    def is_imagemagick_installed() -> bool:
        try:
            result = subprocess.run(
                ["magick", "--version"],
                capture_output=True,
                timeout=5,
                shell=True
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            try:
                result = subprocess.run(
                    ["magick.exe", "--version"],
                    capture_output=True,
                    timeout=5
                )
                return result.returncode == 0
            except:
                return False
    
    @staticmethod
    def image_to_c_array(
        image_path: str,
        width: int,
        height: int,
        var_name: str,
        output_file: Optional[str] = None,
        format_type: Literal["monochrome", "grayscale_2bit", "grayscale_4bit", "grayscale", "rgb565", "rgb888"] = "monochrome",
        invert: bool = False,
        orientation: Literal["horizontal", "vertical"] = "horizontal",
        rotation: Literal[0, 90, 180, 270] = 0,
        threshold: Optional[str] = None,
        keep_aspect: bool = False
    ) -> Dict[str, any]:
        if not os.path.exists(image_path):
            return {
                "success": False,
                "error": f"Image file not found: {image_path}"
            }
        
        if not ImageConverter.is_imagemagick_installed():
            return {
                "success": False,
                "error": "ImageMagick is not installed or not in PATH"
            }
        
        temp_file = f"temp_convert.{format_type}.bmp"
        
        try:
            if format_type == "monochrome":
                return ImageConverter._convert_monochrome(
                    image_path, width, height, var_name, output_file, temp_file, 
                    invert, orientation, rotation, threshold, keep_aspect
                )
            elif format_type == "grayscale_2bit":
                return ImageConverter._convert_grayscale_nbit(
                    image_path, width, height, var_name, output_file, temp_file,
                    invert, orientation, rotation, 2, 4, threshold, keep_aspect
                )
            elif format_type == "grayscale_4bit":
                return ImageConverter._convert_grayscale_nbit(
                    image_path, width, height, var_name, output_file, temp_file,
                    invert, orientation, rotation, 4, 16, threshold, keep_aspect
                )
            elif format_type == "rgb565":
                return ImageConverter._convert_rgb565(
                    image_path, width, height, var_name, output_file, temp_file, 
                    orientation, rotation, keep_aspect
                )
            elif format_type == "rgb888":
                return ImageConverter._convert_rgb888(
                    image_path, width, height, var_name, output_file, temp_file, 
                    orientation, rotation, keep_aspect
                )
            elif format_type == "grayscale":
                return ImageConverter._convert_grayscale(
                    image_path, width, height, var_name, output_file, temp_file, 
                    invert, orientation, rotation, keep_aspect
                )
            else:
                return {
                    "success": False,
                    "error": f"Unsupported format: {format_type}"
                }
                
        except subprocess.CalledProcessError as e:
            if os.path.exists(temp_file):
                os.remove(temp_file)
            return {
                "success": False,
                "error": f"ImageMagick conversion failed: {e.stderr.decode() if e.stderr else str(e)}"
            }
        except Exception as e:
            if os.path.exists(temp_file):
                os.remove(temp_file)
            return {
                "success": False,
                "error": str(e)
            }
    
    @staticmethod
    def _convert_monochrome(
        image_path: str,
        width: int,
        height: int,
        var_name: str,
        output_file: Optional[str],
        temp_file: str,
        invert: bool,
        orientation: str,
        rotation: int,
        threshold: Optional[str],
        keep_aspect: bool
    ) -> Dict[str, any]:
        negate = ["-negate"] if invert else []
        thresh = threshold or ImageConverter.DEFAULTS["monochrome"]["threshold"]
        resize_mode = f"{width}x{height}" if keep_aspect else f"{width}x{height}!"
        rotate_cmd = ["-rotate", str(rotation)] if rotation != 0 else []
        
        subprocess.run([
            "magick", "convert",
            image_path,
            "-background", "white",
            "-alpha", "remove",
            "-alpha", "off",
            *rotate_cmd,
            "-resize", resize_mode,
            "-colorspace", "Gray",
            "-threshold", thresh,
            "-monochrome",
            "-depth", "1",
            "-type", "bilevel",
            *negate,
            "BMP3:" + temp_file
        ], check=True, capture_output=True, shell=True)
        
        with open(temp_file, 'rb') as f:
            bmp_data = f.read()
            if len(bmp_data) < 14:
                raise Exception("Invalid BMP file")
            offset = int.from_bytes(bmp_data[10:14], byteorder='little')
            f.seek(offset)
            data = f.read()
        
        bytes_per_row = (width + 7) // 8
        total_bytes = bytes_per_row * height
        
        c_array = f"// '{Path(image_path).stem}', {width}x{height}px, monochrome\n"
        c_array += f"const unsigned char {var_name}[] PROGMEM = {{\n\t"
        
        byte_data = []
        for i in range(total_bytes):
            if i < len(data):
                byte_data.append(f"0x{data[i]:02x}")
            else:
                byte_data.append("0xff")
        
        for i, byte in enumerate(byte_data):
            c_array += byte
            if i < len(byte_data) - 1:
                c_array += ", "
                if (i + 1) % 12 == 0:
                    c_array += "\n\t"
        
        c_array += "\n};\n"
        
        if os.path.exists(temp_file):
            os.remove(temp_file)
        
        if output_file:
            with open(output_file, 'w') as f:
                f.write(c_array)
        
        return {
            "success": True,
            "c_array": c_array,
            "output_file": output_file,
            "bytes": total_bytes,
            "format": "monochrome (1-bit)",
            "usage": ImageConverter.DEFAULTS["monochrome"]["description"]
        }
    
    @staticmethod
    def _convert_grayscale_nbit(
        image_path: str,
        width: int,
        height: int,
        var_name: str,
        output_file: Optional[str],
        temp_file: str,
        invert: bool,
        orientation: str,
        rotation: int,
        bits: int,
        colors: int,
        threshold: Optional[str],
        keep_aspect: bool
    ) -> Dict[str, any]:
        negate = ["-negate"] if invert else []
        resize_mode = f"{width}x{height}" if keep_aspect else f"{width}x{height}!"
        rotate_cmd = ["-rotate", str(rotation)] if rotation != 0 else []
        
        subprocess.run([
            "magick", "convert",
            image_path,
            "-background", "white",
            "-alpha", "remove",
            "-alpha", "off",
            *rotate_cmd,
            "-resize", resize_mode,
            "-colorspace", "Gray",
            "-colors", str(colors),
            "-depth", str(bits),
            *negate,
            "BMP3:" + temp_file
        ], check=True, capture_output=True, shell=True)
        
        with open(temp_file, 'rb') as f:
            bmp_data = f.read()
            if len(bmp_data) < 14:
                raise Exception("Invalid BMP file")
            offset = int.from_bytes(bmp_data[10:14], byteorder='little')
            width_read = int.from_bytes(bmp_data[18:22], byteorder='little')
            height_read = int.from_bytes(bmp_data[22:26], byteorder='little')
            f.seek(offset)
            data = f.read()
        
        if bits == 2:
            bytes_per_row = (width + 3) // 4
        elif bits == 4:
            bytes_per_row = (width + 1) // 2
        else:
            bytes_per_row = width
            
        row_padding = (4 - (bytes_per_row % 4)) % 4
        
        clean_data = []
        for row in range(height):
            row_start = row * (bytes_per_row + row_padding)
            row_end = row_start + bytes_per_row
            for byte_idx in range(row_start, row_end):
                if byte_idx < len(data):
                    clean_data.append(f"0x{data[byte_idx]:02x}")
        
        c_array = f"// '{Path(image_path).stem}', {width}x{height}px, {bits}-bit grayscale ({colors} levels)\n"
        c_array += f"const unsigned char {var_name}[] PROGMEM = {{\n\t"
        
        for i, byte in enumerate(clean_data):
            c_array += byte
            if i < len(clean_data) - 1:
                c_array += ", "
                if (i + 1) % 12 == 0:
                    c_array += "\n\t"
        
        c_array += "\n};\n"
        
        if os.path.exists(temp_file):
            os.remove(temp_file)
        
        if output_file:
            with open(output_file, 'w') as f:
                f.write(c_array)
        
        format_key = f"grayscale_{bits}bit"
        return {
            "success": True,
            "c_array": c_array,
            "output_file": output_file,
            "bytes": len(clean_data),
            "format": f"{bits}-bit grayscale ({colors} levels)",
            "usage": ImageConverter.DEFAULTS[format_key]["description"]
        }
    
    @staticmethod
    def _convert_rgb565(
        image_path: str,
        width: int,
        height: int,
        var_name: str,
        output_file: Optional[str],
        temp_file: str,
        orientation: str,
        rotation: int,
        keep_aspect: bool
    ) -> Dict[str, any]:
        resize_mode = f"{width}x{height}" if keep_aspect else f"{width}x{height}!"
        rotate_cmd = ["-rotate", str(rotation)] if rotation != 0 else []
        
        subprocess.run([
            "magick", "convert",
            image_path,
            "-background", "white",
            "-alpha", "remove",
            "-alpha", "off",
            *rotate_cmd,
            "-resize", resize_mode,
            "-depth", "8",
            "BMP3:" + temp_file
        ], check=True, capture_output=True, shell=True)
        
        with open(temp_file, 'rb') as f:
            bmp_data = f.read()
            if len(bmp_data) < 14:
                raise Exception("Invalid BMP file")
            offset = int.from_bytes(bmp_data[10:14], byteorder='little')
            f.seek(offset)
            data = f.read()
        
        rgb565_data = []
        for i in range(0, len(data), 3):
            if i + 2 < len(data):
                b = data[i]
                g = data[i + 1]
                r = data[i + 2]
                
                r5 = (r >> 3) & 0x1F
                g6 = (g >> 2) & 0x3F
                b5 = (b >> 3) & 0x1F
                
                rgb565 = (r5 << 11) | (g6 << 5) | b5
                rgb565_data.append(f"0x{rgb565:04x}")
        
        c_array = f"// '{Path(image_path).stem}', {width}x{height}px, RGB565\n"
        c_array += f"const uint16_t {var_name}[] PROGMEM = {{\n\t"
        
        for i, val in enumerate(rgb565_data):
            c_array += val
            if i < len(rgb565_data) - 1:
                c_array += ", "
                if (i + 1) % 8 == 0:
                    c_array += "\n\t"
        
        c_array += "\n};\n"
        
        if os.path.exists(temp_file):
            os.remove(temp_file)
        
        if output_file:
            with open(output_file, 'w') as f:
                f.write(c_array)
        
        return {
            "success": True,
            "c_array": c_array,
            "output_file": output_file,
            "bytes": len(rgb565_data) * 2,
            "format": "RGB565 (16-bit color)",
            "usage": ImageConverter.DEFAULTS["rgb565"]["description"]
        }
    
    @staticmethod
    def _convert_rgb888(
        image_path: str,
        width: int,
        height: int,
        var_name: str,
        output_file: Optional[str],
        temp_file: str,
        orientation: str,
        rotation: int,
        keep_aspect: bool
    ) -> Dict[str, any]:
        resize_mode = f"{width}x{height}" if keep_aspect else f"{width}x{height}!"
        rotate_cmd = ["-rotate", str(rotation)] if rotation != 0 else []
        
        subprocess.run([
            "magick", "convert",
            image_path,
            "-background", "white",
            "-alpha", "remove",
            "-alpha", "off",
            *rotate_cmd,
            "-resize", resize_mode,
            "-depth", "8",
            "BMP3:" + temp_file
        ], check=True, capture_output=True, shell=True)
        
        with open(temp_file, 'rb') as f:
            bmp_data = f.read()
            if len(bmp_data) < 14:
                raise Exception("Invalid BMP file")
            offset = int.from_bytes(bmp_data[10:14], byteorder='little')
            f.seek(offset)
            data = f.read()
        
        rgb_data = []
        for i in range(0, len(data), 3):
            if i + 2 < len(data):
                b = data[i]
                g = data[i + 1]
                r = data[i + 2]
                rgb_data.extend([f"0x{r:02x}", f"0x{g:02x}", f"0x{b:02x}"])
        
        c_array = f"// '{Path(image_path).stem}', {width}x{height}px, RGB888\n"
        c_array += f"const unsigned char {var_name}[] PROGMEM = {{\n\t"
        
        for i, val in enumerate(rgb_data):
            c_array += val
            if i < len(rgb_data) - 1:
                c_array += ", "
                if (i + 1) % 12 == 0:
                    c_array += "\n\t"
        
        c_array += "\n};\n"
        
        if os.path.exists(temp_file):
            os.remove(temp_file)
        
        if output_file:
            with open(output_file, 'w') as f:
                f.write(c_array)
        
        return {
            "success": True,
            "c_array": c_array,
            "output_file": output_file,
            "bytes": len(rgb_data),
            "format": "RGB888 (24-bit true color)",
            "usage": ImageConverter.DEFAULTS["rgb888"]["description"]
        }
    
    @staticmethod
    def _convert_grayscale(
        image_path: str,
        width: int,
        height: int,
        var_name: str,
        output_file: Optional[str],
        temp_file: str,
        invert: bool,
        orientation: str,
        rotation: int,
        keep_aspect: bool
    ) -> Dict[str, any]:
        negate = ["-negate"] if invert else []
        resize_mode = f"{width}x{height}" if keep_aspect else f"{width}x{height}!"
        rotate_cmd = ["-rotate", str(rotation)] if rotation != 0 else []
        
        subprocess.run([
            "magick", "convert",
            image_path,
            "-background", "white",
            "-alpha", "remove",
            "-alpha", "off",
            *rotate_cmd,
            "-resize", resize_mode,
            "-colorspace", "Gray",
            "-depth", "8",
            *negate,
            "BMP3:" + temp_file
        ], check=True, capture_output=True, shell=True)
        
        with open(temp_file, 'rb') as f:
            bmp_data = f.read()
            if len(bmp_data) < 14:
                raise Exception("Invalid BMP file")
            offset = int.from_bytes(bmp_data[10:14], byteorder='little')
            f.seek(offset)
            data = f.read()
        
        gray_data = [f"0x{b:02x}" for b in data]
        
        c_array = f"// '{Path(image_path).stem}', {width}x{height}px, grayscale 8-bit\n"
        c_array += f"const unsigned char {var_name}[] PROGMEM = {{\n\t"
        
        for i, val in enumerate(gray_data):
            c_array += val
            if i < len(gray_data) - 1:
                c_array += ", "
                if (i + 1) % 12 == 0:
                    c_array += "\n\t"
        
        c_array += "\n};\n"
        
        if os.path.exists(temp_file):
            os.remove(temp_file)
        
        if output_file:
            with open(output_file, 'w') as f:
                f.write(c_array)
        
        return {
            "success": True,
            "c_array": c_array,
            "output_file": output_file,
            "bytes": len(gray_data),
            "format": "Grayscale 8-bit (256 levels)",
            "usage": ImageConverter.DEFAULTS["grayscale"]["description"]
        }
