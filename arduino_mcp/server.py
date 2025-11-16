from fastmcp import FastMCP, Context
import json
from typing import Optional
from pathlib import Path
import glob
from .cli_wrapper import ArduinoCLI, ArduinoCLIError
from .port_detector import PortDetector
from .image_converter import ImageConverter
from .platform_utils import platform_config

mcp = FastMCP("Arduino MCP Server")

cli = ArduinoCLI()

print("\n" + "="*60)
print("Arduino MCP Server - Dependency Check")
print(f"Platform: {platform_config.os_type}")
print("="*60)
if cli.is_installed():
    version = cli.get_version()
    print(platform_config.format_status("ok", f"Arduino CLI: {version}"))
else:
    print(platform_config.format_status("fail", "Arduino CLI: Not Found"))
    print("  Install: https://arduino.github.io/arduino-cli/latest/installation/")

if ImageConverter.is_imagemagick_installed():
    print(platform_config.format_status("ok", "ImageMagick: Installed"))
else:
    print(platform_config.format_status("skip", "ImageMagick: Not Found (optional)"))
    print("  Install: https://imagemagick.org/script/download.php")
print("="*60 + "\n")


@mcp.tool(
    annotations={
        "title": "Execute Raw Arduino CLI Command",
        "readOnlyHint": False,
        "openWorldHint": True
    }
)
async def arduino_cli_command(command: str, ctx: Context) -> str:
    try:
        await ctx.info(f"Executing: arduino-cli {command}")
        
        args = command.split()
        result = cli.run_command(args)
        
        if result["success"]:
            await ctx.info("Command completed successfully")
            output = result["stdout"]
            if result["stderr"]:
                output += f"\n\nWarnings:\n{result['stderr']}"
            return output if output else "Command executed successfully (no output)"
        else:
            await ctx.error("Command failed")
            return f"Error (exit code {result['returncode']}):\n{result['stderr']}"
    except ArduinoCLIError as e:
        await ctx.error(f"Command execution error: {str(e)}")
        return f"Error: {str(e)}"


@mcp.tool(
    annotations={
        "title": "List Serial Ports",
        "readOnlyHint": True
    }
)
async def list_ports(arduino_only: bool = False, ctx: Context = None) -> str:
    if ctx:
        await ctx.info(f"Scanning for {'Arduino' if arduino_only else 'all'} ports...")
    
    if arduino_only:
        ports = PortDetector.find_arduino_ports()
        if not ports:
            if ctx:
                await ctx.warning("No Arduino devices found")
            all_ports = PortDetector.list_ports()
            return f"No Arduino-like devices found.\n\nAll available ports ({len(all_ports)}):\n" + json.dumps(all_ports, indent=2)
        if ctx:
            await ctx.info(f"Found {len(ports)} Arduino device(s)")
        
        best = PortDetector.get_best_port()
        result = f"Arduino Devices Found ({len(ports)}):\n"
        result += json.dumps(ports, indent=2)
        if best:
            result += f"\n\nRecommended Port: {best}"
        return result
    else:
        ports = PortDetector.list_ports()
        if ctx:
            await ctx.info(f"Found {len(ports)} port(s)")
        return json.dumps(ports, indent=2)


@mcp.tool(annotations={"readOnlyHint": True, "openWorldHint": True})
async def list_connected_boards(ctx: Context) -> str:
    try:
        await ctx.info("Scanning for connected boards...")
        result = cli.board_list()
        await ctx.info(f"Found boards: {len(result.get('detected_ports', []))}")
        return json.dumps(result, indent=2)
    except ArduinoCLIError as e:
        await ctx.error(f"Failed to list boards: {str(e)}")
        return f"Error: {str(e)}"


@mcp.tool(annotations={"readOnlyHint": True})
async def verify_port(port: str, ctx: Context) -> str:
    await ctx.info(f"Verifying port {port}...")
    if PortDetector.verify_port(port):
        await ctx.info(f"Port {port} is accessible")
        return f"Port {port} is accessible"
    await ctx.warning(f"Port {port} is not accessible")
    return f"Port {port} is not accessible or does not exist"


@mcp.tool(
    annotations={
        "title": "Search Arduino Packages",
        "readOnlyHint": True,
        "openWorldHint": True
    }
)
async def search(query: str, package_type: str, ctx: Context) -> str:
    if package_type not in ["core", "library"]:
        return "Error: package_type must be 'core' or 'library'"
    
    try:
        await ctx.info(f"Searching for {package_type}s: {query}")
        
        if package_type == "core":
            result = cli.core_search(query)
        else:
            result = cli.lib_search(query)
        
        return json.dumps(result, indent=2)
    except ArduinoCLIError as e:
        await ctx.error(f"Search failed: {str(e)}")
        return f"Error: {str(e)}"


@mcp.tool(annotations={"readOnlyHint": True})
async def list_installed_cores(ctx: Context) -> str:
    try:
        await ctx.info("Fetching installed cores...")
        result = cli.core_list()
        return json.dumps(result, indent=2)
    except ArduinoCLIError as e:
        await ctx.error(f"Failed to list cores: {str(e)}")
        return f"Error: {str(e)}"


@mcp.tool(
    annotations={
        "title": "Install Arduino Core",
        "readOnlyHint": False,
        "openWorldHint": True
    }
)
async def install_core(core: str, ctx: Context) -> str:
    try:
        await ctx.info(f"Installing Arduino core: {core}")
        await ctx.report_progress(progress=0, total=100)
        
        result = cli.core_install(core)
        
        await ctx.report_progress(progress=100, total=100)
        
        if result["success"]:
            await ctx.info(f"Core {core} installed successfully")
            return f"Successfully installed core: {core}\n{result['stdout']}"
        
        await ctx.error(f"Failed to install core: {core}")
        return f"Failed to install core: {core}\n{result['stderr']}"
    except ArduinoCLIError as e:
        await ctx.error(f"Core installation error: {str(e)}")
        return f"Error: {str(e)}"


@mcp.tool(
    annotations={
        "title": "Install Arduino Library",
        "readOnlyHint": False,
        "openWorldHint": True
    }
)
async def install_library(library: str, ctx: Context) -> str:
    try:
        await ctx.info(f"Installing Arduino library: {library}")
        await ctx.report_progress(progress=0, total=100)
        
        result = cli.lib_install(library)
        
        await ctx.report_progress(progress=100, total=100)
        
        if result["success"]:
            await ctx.info(f"Library {library} installed successfully")
            return f"Successfully installed library: {library}\n{result['stdout']}"
        
        await ctx.error(f"Failed to install library: {library}")
        return f"Failed to install library: {library}\n{result['stderr']}"
    except ArduinoCLIError as e:
        await ctx.error(f"Library installation error: {str(e)}")
        return f"Error: {str(e)}"


@mcp.tool(annotations={"readOnlyHint": True})
async def list_installed_libraries(ctx: Context) -> str:
    try:
        await ctx.info("Fetching installed libraries...")
        result = cli.lib_list()
        return json.dumps(result, indent=2)
    except ArduinoCLIError as e:
        await ctx.error(f"Failed to list libraries: {str(e)}")
        return f"Error: {str(e)}"


@mcp.tool(
    annotations={
        "title": "Compile Arduino Sketch",
        "readOnlyHint": False,
        "openWorldHint": False
    }
)
async def compile_sketch(sketch_path: str, fqbn: str, ctx: Context) -> str:
    try:
        await ctx.info(f"Starting compilation of {sketch_path} for {fqbn}")
        await ctx.report_progress(progress=0, total=100)
        
        result = cli.compile(sketch_path, fqbn)
        
        await ctx.report_progress(progress=100, total=100)
        
        if result["success"]:
            await ctx.info("Compilation successful")
            return f"Compilation successful:\n{result['stdout']}"
        
        await ctx.error("Compilation failed")
        return f"Compilation failed:\n{result['stderr']}"
    except ArduinoCLIError as e:
        await ctx.error(f"Compilation error: {str(e)}")
        return f"Error: {str(e)}"


@mcp.tool(
    annotations={
        "title": "Upload Sketch to Board",
        "readOnlyHint": False,
        "destructiveHint": True,
        "openWorldHint": True
    }
)
async def upload_sketch(sketch_path: str, fqbn: str, port: str, ctx: Context) -> str:
    try:
        await ctx.info(f"Starting upload to {port}")
        await ctx.report_progress(progress=0, total=100)
        
        await ctx.report_progress(progress=30, total=100)
        result = cli.upload(sketch_path, fqbn, port)
        
        await ctx.report_progress(progress=100, total=100)
        
        if result["success"]:
            await ctx.info("Upload successful")
            return f"Upload successful:\n{result['stdout']}"
        
        await ctx.error("Upload failed")
        return f"Upload failed:\n{result['stderr']}"
    except ArduinoCLIError as e:
        await ctx.error(f"Upload error: {str(e)}")
        return f"Error: {str(e)}"


@mcp.tool(annotations={"readOnlyHint": False})
async def create_new_sketch(sketch_name: str, path: Optional[str] = None, ctx: Context = None) -> str:
    try:
        if ctx:
            await ctx.info(f"Creating new sketch: {sketch_name}")
        result = cli.sketch_new(sketch_name, path)
        if result["success"]:
            if ctx:
                await ctx.info(f"Sketch {sketch_name} created successfully")
            return f"Sketch created successfully:\n{result['stdout']}"
        return f"Failed to create sketch:\n{result['stderr']}"
    except ArduinoCLIError as e:
        if ctx:
            await ctx.error(f"Sketch creation failed: {str(e)}")
        return f"Error: {str(e)}"


@mcp.tool(annotations={"readOnlyHint": False, "destructiveHint": False})
async def clean_cache(ctx: Context) -> str:
    try:
        await ctx.info("Cleaning Arduino CLI cache...")
        result = cli.cache_clean()
        if result["success"]:
            await ctx.info("Cache cleaned successfully")
            return f"Cache cleaned successfully:\n{result['stdout']}"
        await ctx.error("Failed to clean cache")
        return f"Failed to clean cache:\n{result['stderr']}"
    except ArduinoCLIError as e:
        await ctx.error(f"Cache cleaning error: {str(e)}")
        return f"Error: {str(e)}"


@mcp.tool(
    annotations={
        "title": "Serial Monitor",
        "readOnlyHint": True,
        "openWorldHint": True
    }
)
async def serial_monitor(
    port: str,
    duration: int = 20,
    baudrate: int = 9600,
    ctx: Context = None
) -> str:
    import serial
    import time
    
    if ctx:
        await ctx.info(f"Opening serial monitor on {port} at {baudrate} baud for {duration}s")
        await ctx.report_progress(progress=0, total=duration)
    
    try:
        ser = serial.Serial(port, baudrate, timeout=1)
        time.sleep(0.5)
        
        output_lines = []
        start_time = time.time()
        
        while (time.time() - start_time) < duration:
            if ser.in_waiting > 0:
                try:
                    line = ser.readline().decode('utf-8', errors='ignore').strip()
                    if line:
                        output_lines.append(line)
                        if ctx:
                            await ctx.info(f"Serial: {line[:50]}...")
                except Exception as decode_error:
                    output_lines.append(f"[Decode Error: {decode_error}]")
            
            if ctx:
                elapsed = int(time.time() - start_time)
                await ctx.report_progress(progress=elapsed, total=duration)
            
            time.sleep(0.1)
        
        ser.close()
        
        if ctx:
            await ctx.info(f"Serial monitor closed. Captured {len(output_lines)} lines")
        
        if not output_lines:
            return f"No serial output received on {port} in {duration} seconds.\n\nTips:\n- Check if sketch is running\n- Verify correct baud rate (current: {baudrate})\n- Ensure Serial.begin() in sketch"
        
        result = f"Serial Monitor Output ({port} @ {baudrate} baud, {duration}s):\n"
        result += "=" * 60 + "\n"
        result += "\n".join(output_lines)
        result += "\n" + "=" * 60
        result += f"\n\nCaptured {len(output_lines)} lines in {duration} seconds"
        
        return result
        
    except serial.SerialException as e:
        if ctx:
            await ctx.error(f"Serial port error: {str(e)}")
        return f"Error: Could not open serial port {port}\n\nDetails: {str(e)}\n\nTips:\n- Check if port exists\n- Close other serial monitors\n- Verify port permissions"
    except Exception as e:
        if ctx:
            await ctx.error(f"Unexpected error: {str(e)}")
        return f"Error: {str(e)}"


@mcp.tool(
    annotations={
        "title": "Convert Image to C Array for Hardware Displays",
        "readOnlyHint": False,
        "openWorldHint": True
    }
)
async def convert_image_to_c_array(
    image_path: str,
    width: int,
    height: int,
    var_name: str,
    format_type: str = "monochrome",
    output_file: Optional[str] = None,
    invert: bool = False,
    rotation: int = 0,
    threshold: Optional[str] = None,
    keep_aspect: bool = False,
    ctx: Context = None
) -> str:
    """
    Convert images to C arrays for hardware displays (OLED, E-Paper, TFT, LEDs)
    
    Supports: monochrome (1-bit), grayscale_2bit (4-level), grayscale_4bit (16-level),
    grayscale (8-bit), rgb565 (16-bit color), rgb888 (24-bit color)
    
    Parameters:
    - rotation: 0, 90, 180, or 270 degrees (test all to find correct orientation)
    - threshold: Black/white cutoff for monochrome (e.g., "50%", "60%", "70%")
    - keep_aspect: True to maintain proportions, False to force exact size
    """
    if ctx:
        await ctx.info(f"Converting {image_path} to {format_type} C array ({width}x{height}, rotation={rotation}°)")
        await ctx.report_progress(progress=0, total=100)
    
    result = ImageConverter.image_to_c_array(
        image_path, width, height, var_name, output_file, 
        format_type, invert, "horizontal", rotation, threshold, keep_aspect
    )
    
    if ctx:
        await ctx.report_progress(progress=100, total=100)
    
    if result["success"]:
        if ctx:
            await ctx.info(f"Conversion successful: {result['format']} - {result['bytes']} bytes")
        output = f"Successfully converted image to C array\n\n"
        output += f"**Format**: {result['format']}\n"
        output += f"**Size**: {width}x{height} pixels ({result['bytes']} bytes)\n"
        output += f"**Usage**: {result['usage']}\n"
        if rotation != 0:
            output += f"**Rotation**: {rotation}°\n"
        if threshold:
            output += f"**Threshold**: {threshold}\n"
        if output_file:
            output += f"**Saved to**: {output_file}\n\n"
        output += "```c\n" + result["c_array"] + "```"
        return output
    
    if ctx:
        await ctx.error(f"Conversion failed: {result['error']}")
    return f"Error: {result['error']}"


@mcp.resource("sketch://{path}")
async def read_sketch_file(path: str) -> str:
    sketch_path = Path(path)
    
    if not sketch_path.exists():
        return f"Sketch file not found: {path}"
    
    if sketch_path.is_file() and sketch_path.suffix in ['.ino', '.cpp', '.h']:
        return sketch_path.read_text()
    
    if sketch_path.is_dir():
        ino_files = list(sketch_path.glob("*.ino"))
        if ino_files:
            return ino_files[0].read_text()
        return f"No .ino file found in directory: {path}"
    
    return f"Invalid sketch path: {path}"


@mcp.resource("arduino-config://main")
async def read_arduino_config() -> str:
    result = cli.run_command(["config", "dump", "--format", "json"])
    if result["success"]:
        return result["stdout"]
    return "Arduino CLI config not found. Run 'arduino-cli config init' first."


@mcp.resource("board-info://{fqbn}")
async def get_board_info(fqbn: str) -> str:
    result = cli.run_command(["board", "details", "--fqbn", fqbn, "--format", "json"])
    if result["success"]:
        return result["stdout"]
    return f"Board info not found for FQBN: {fqbn}"


@mcp.prompt()
def blink_led_example():
    return """Create a basic Arduino sketch that blinks an LED:

1. Use pin 13 (built-in LED on most Arduino boards)
2. Set up the pin as OUTPUT in setup()
3. Toggle the LED every 1000ms in loop()
4. Add serial output to show LED state

Example structure:
```cpp
void setup() {
  Serial.begin(9600);
  pinMode(13, OUTPUT);
}

void loop() {
  digitalWrite(13, HIGH);
  Serial.println("LED ON");
  delay(1000);
  digitalWrite(13, LOW);
  Serial.println("LED OFF");
  delay(1000);
}
```"""


@mcp.prompt()
def sensor_reading_example():
    return """Create an Arduino sketch for reading an analog sensor:

1. Read from analog pin A0
2. Print the value to Serial Monitor
3. Add averaging to smooth readings
4. Include proper serial initialization

Template:
```cpp
const int sensorPin = A0;

void setup() {
  Serial.begin(9600);
}

void loop() {
  int sensorValue = analogRead(sensorPin);
  Serial.print("Sensor: ");
  Serial.println(sensorValue);
  delay(100);
}
```"""


@mcp.prompt()
def full_development_workflow():
    return """Complete Arduino development workflow:

1. **Setup**: Check if Arduino CLI is installed using `check_arduino_cli_installed`
2. **Board Detection**: Find connected boards with `list_connected_boards` and `find_arduino_ports`
3. **Core Installation**: Search and install the appropriate core for your board using `search_cores` and `install_core`
4. **Library Management**: Search for required libraries with `search_libraries` and install with `install_library`
5. **Sketch Creation**: Create a new sketch using `create_new_sketch` or read existing with `sketch://path`
6. **Compilation**: Compile the sketch with `compile_sketch` providing sketch path and FQBN
7. **Upload**: Upload to board using `upload_sketch` with correct port
8. **Debugging**: Use serial monitor or check compilation errors

Common FQBNs:
- Arduino Uno: `arduino:avr:uno`
- Arduino Mega: `arduino:avr:mega`
- Arduino Nano: `arduino:avr:nano`
- ESP32: `esp32:esp32:esp32`
- ESP8266: `esp8266:esp8266:generic`"""


@mcp.prompt()
def troubleshooting_guide():
    return """Arduino troubleshooting steps:

**Compilation Errors:**
1. Check if required libraries are installed with `list_installed_libraries`
2. Verify core is installed for your board with `list_installed_cores`
3. Check sketch syntax and includes

**Upload Errors:**
1. Verify board is connected: `list_connected_boards`
2. Check correct port: `find_arduino_ports` and `verify_port`
3. Ensure correct FQBN is used
4. Try different USB cable or port

**Port Detection:**
1. Use `list_serial_ports` to see all available ports
2. Use `find_arduino_ports` to filter Arduino devices
3. Use `get_best_port` for automatic detection
4. Verify with `verify_port` before uploading

**Library Issues:**
1. Search for library: `search_libraries`
2. Install missing libraries: `install_library`
3. Check installed: `list_installed_libraries`"""


if __name__ == "__main__":
    mcp.run()
