# Arduino MCP - LLM Companion Guide

## Project Overview

This is an MCP (Model Context Protocol) server that bridges AI/LLM agents with Arduino CLI for embedded development. Built with FastMCP and Python 3.10+, it provides comprehensive Arduino development capabilities through a standardized AI interface.

**Repository**: https://github.com/niradler/arduino-mcp

## Core Technologies

- **FastMCP**: Python framework for building MCP servers
- **Arduino CLI**: Command-line interface for Arduino development
- **PySerial**: Serial communication library
- **Python 3.10+**: Modern Python with type hints
- **uv**: Fast Python package manager

## Architecture

### Module Structure

```
arduino_mcp/
├── server.py           # Main MCP server (tools, resources, prompts)
├── cli_wrapper.py      # Arduino CLI command wrapper
├── port_detector.py    # Serial port detection (cross-platform)
├── image_converter.py  # Image to C array converter
└── platform_utils.py   # OS detection and platform-specific handling
```

### Design Principles

1. **FastMCP Framework**: Leverage all 3 MCP pillars (Tools, Resources, Prompts)
2. **Cross-Platform**: Windows/macOS/Linux support with automatic detection
3. **Error Handling**: Graceful failures with informative error messages
4. **Context-Aware**: Full MCP Context integration for logging and progress
5. **Type Safety**: Type hints throughout for better IDE support

## Best Practices

### 1. Arduino CLI Integration

**Always check CLI availability first:**

```python
if not cli.is_installed():
    return "Arduino CLI not installed. Install from: https://arduino.github.io/arduino-cli/"
```

**Use structured command execution:**

```python
result = cli.run_command(args)
if result["success"]:
    output = result["stdout"]
else:
    error = result["stderr"]
```

**Common CLI patterns:**
- Board operations: `board list`, `board details --fqbn <FQBN>`
- Core management: `core search`, `core install`, `core list`
- Library management: `lib search`, `lib install`, `lib list`
- Sketch operations: `sketch new`, `compile`, `upload`

### 2. Port Detection Best Practices

**Use platform-aware detection:**

```python
from port_detector import PortDetector

arduino_ports = PortDetector.find_arduino_ports()
best_port = PortDetector.get_best_port()
```

**Platform-specific patterns:**
- Windows: `COM*` ports (e.g., COM3, COM4)
- macOS: `/dev/tty.*` and `/dev/cu.*` (prefer `cu` for writing)
- Linux: `/dev/ttyUSB*`, `/dev/ttyACM*`

**Arduino identification keywords:**
- "Arduino"
- "CH340" (common USB-to-serial chip)
- "CP210" (Silicon Labs chip)
- "FTDI" (FTDI chip)
- "USB-SERIAL"

**Always verify ports before upload:**

```python
if not PortDetector.verify_port(port):
    return f"Port {port} is not accessible"
```

### 3. MCP Context Usage

**Leverage Context for better UX:**

```python
async def my_tool(ctx: Context):
    await ctx.info("Starting operation...")
    await ctx.report_progress(progress=50, total=100)
    await ctx.warning("Potential issue detected")
    await ctx.error("Operation failed")
```

**Context benefits:**
- User visibility into long operations
- Progress tracking for uploads/downloads
- Error distinction (info/warning/error)
- Better debugging experience

### 4. Tool Annotations

**Use proper MCP annotations:**

```python
@mcp.tool(
    annotations={
        "title": "Human-Readable Title",
        "readOnlyHint": True,        # Doesn't modify system
        "destructiveHint": True,      # Can delete/overwrite data
        "openWorldHint": True         # Accesses external resources
    }
)
```

**Annotation guidelines:**
- `readOnlyHint=True`: List, search, check operations
- `readOnlyHint=False`: Install, create, compile operations
- `destructiveHint=True`: Upload (overwrites board firmware)
- `openWorldHint=True`: Network access, external CLI calls

### 5. Error Handling Patterns

**Structured error responses:**

```python
try:
    result = cli.run_command(args)
    if result["success"]:
        return format_success(result["stdout"])
    else:
        return format_error(result["stderr"], result["returncode"])
except ArduinoCLIError as e:
    return f"Error: {str(e)}"
```

**User-friendly error messages:**

```python
if not output_lines:
    return f"""No serial output received on {port} in {duration} seconds.

Tips:
- Check if sketch is running
- Verify correct baud rate (current: {baudrate})
- Ensure Serial.begin() in sketch"""
```

### 6. Resource Implementation

**Three resource types implemented:**

```python
@mcp.resource("sketch://{path}")
async def read_sketch_file(path: str) -> str:
    pass

@mcp.resource("arduino-config://main")
async def read_arduino_config() -> str:
    pass

@mcp.resource("board-info://{fqbn}")
async def get_board_info(fqbn: str) -> str:
    pass
```

**Resource benefits:**
- Declarative data access
- Cacheable by MCP clients
- Clean separation from tools

### 7. Prompt Templates

**Provide reusable templates:**

```python
@mcp.prompt()
def full_development_workflow():
    return """Complete Arduino development workflow:
    
    1. Check installation
    2. Detect boards
    3. Install cores/libraries
    4. Create/compile/upload sketch
    5. Debug with serial monitor"""
```

**Prompt types:**
- Example code (blink_led_example)
- Templates (sensor_reading_example)
- Workflows (full_development_workflow)
- Troubleshooting (troubleshooting_guide)

### 8. Image Conversion for Embedded Displays

**Image to C array conversion:**

```python
result = ImageConverter.image_to_c_array(
    image_path="logo.png",
    width=128,
    height=64,
    var_name="logo_bitmap",
    format_type="monochrome",
    rotation=0,
    threshold="50%"
)
```

**Supported formats:**
- `monochrome`: 1-bit (OLED displays)
- `grayscale_2bit`: 4-level grayscale
- `grayscale_4bit`: 16-level grayscale
- `grayscale`: 8-bit grayscale
- `rgb565`: 16-bit color (TFT displays)
- `rgb888`: 24-bit color

**Best practices:**
- Test all rotations (0, 90, 180, 270) to find correct orientation
- Adjust threshold for monochrome (50%-70% typical)
- Use `keep_aspect=True` to maintain proportions
- Invert colors if display shows negative

### 9. Serial Monitor Implementation

**Safe serial reading:**

```python
try:
    ser = serial.Serial(port, baudrate, timeout=1)
    time.sleep(0.5)  # Allow port to stabilize
    
    while (time.time() - start_time) < duration:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8', errors='ignore')
finally:
    ser.close()
```

**Common baud rates:**
- 9600 (default, most compatible)
- 115200 (fast, modern boards)
- 57600, 38400 (alternatives)

### 10. Common FQBNs (Fully Qualified Board Names)

**AVR Boards:**
- `arduino:avr:uno` - Arduino Uno
- `arduino:avr:mega` - Arduino Mega 2560
- `arduino:avr:nano` - Arduino Nano
- `arduino:avr:leonardo` - Arduino Leonardo

**ESP Boards:**
- `esp32:esp32:esp32` - ESP32 DevKit
- `esp8266:esp8266:generic` - ESP8266
- `esp32:esp32:esp32s3` - ESP32-S3

**Other:**
- `arduino:samd:mkr1000` - Arduino MKR1000
- `STMicroelectronics:stm32:GenF1` - STM32 boards

### 11. Development Workflow

**Standard Arduino development cycle:**

```
1. Check Installation → arduino_cli_installed
2. Board Detection → list_connected_boards, find_arduino_ports
3. Core Installation → search("esp32", "core"), install_core("esp32:esp32")
4. Library Installation → search("Adafruit SSD1306", "library"), install_library("Adafruit SSD1306")
5. Create Sketch → create_new_sketch("MyProject")
6. Edit Code → Use resources or file system
7. Compile → compile_sketch("./MyProject", "arduino:avr:uno")
8. Upload → upload_sketch("./MyProject", "arduino:avr:uno", "COM3")
9. Monitor → serial_monitor("COM3", duration=20, baudrate=9600)
```

### 12. Troubleshooting Common Issues

**Upload Failures:**
- Verify board is connected: `list_connected_boards()`
- Check port access: `verify_port(port)`
- Correct FQBN: Use exact FQBN from `board list`
- Close other serial monitors
- Try different USB port/cable

**Compilation Errors:**
- Install required libraries: `search_libraries()` → `install_library()`
- Install board core: `list_installed_cores()` → `install_core()`
- Check sketch syntax

**Port Detection:**
- Windows: May need driver installation (CH340, CP210x)
- Linux: Add user to `dialout` group: `sudo usermod -a -G dialout $USER`
- macOS: Use `/dev/cu.*` not `/dev/tty.*` for uploads

**Serial Monitor No Output:**
- Verify correct baud rate
- Check `Serial.begin()` in sketch
- Ensure sketch is running (compile + upload)
- Wait longer (some sketches have startup delay)

### 13. Cross-Platform Considerations

**Platform detection:**

```python
from platform_utils import platform_config

os_type = platform_config.os_type  # "windows", "darwin", "linux"
serial_keywords = platform_config.serial_keywords
port_patterns = platform_config.port_patterns
```

**Platform-specific handling:**
- Windows: No permission errors, COM ports
- macOS: Both tty/cu devices, prefer cu for writing
- Linux: Permission issues common, USB device paths

### 14. Package Management

**Always use uv in this project:**

```bash
# Install dependencies
uv sync

# Run server
uv run python -m arduino_mcp.server

# Add new dependency
uv add package-name

# Run with FastMCP
uv run fastmcp run arduino_mcp/server.py:mcp
```

**Why uv:**
- Fast dependency resolution
- Lock file for reproducibility (uv.lock)
- Modern Python tooling
- Better than pip/venv for projects

### 15. Testing Considerations

**Manual testing workflow:**

```bash
# 1. Test import
uv run python -c "from arduino_mcp import mcp; print('OK')"

# 2. Check CLI availability
uv run python -c "from arduino_mcp.cli_wrapper import ArduinoCLI; print(ArduinoCLI().is_installed())"

# 3. Run server
uv run fastmcp run arduino_mcp/server.py:mcp

# 4. Test in Cursor/Claude Desktop
```

**Test scenarios:**
- Board detection without boards connected
- Upload without port access
- Install non-existent library
- Compile with syntax errors
- Serial monitor on invalid port

### 16. Performance Optimization

**Command execution:**
- Reuse CLI instance (singleton pattern)
- Cache board lists for repeated queries
- Avoid repeated core/library searches

**Serial operations:**
- Use appropriate timeouts
- Buffer serial data efficiently
- Close ports immediately after use

**JSON formatting:**
- Use `json.dumps(data, indent=2)` for readability
- Return structured data when possible

### 17. Security Considerations

**CLI injection prevention:**
- Arduino CLI wrapper validates commands
- No arbitrary shell execution
- Command arguments are properly escaped

**Port access:**
- Verify port exists before opening
- Handle permission errors gracefully
- Close serial connections properly

**File system access:**
- Validate sketch paths
- Use Path objects for cross-platform safety
- No arbitrary file system access in tools

### 18. MCP Client Configuration

**Cursor IDE (.cursor/mcp.json):**

```json
{
  "mcpServers": {
    "arduino": {
      "command": "uv",
      "args": [
        "--directory",
        "C:/Projects/mcp/arduino-mcp",
        "run",
        "python",
        "-m",
        "arduino_mcp.server"
      ]
    }
  }
}
```

**Claude Desktop:**
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Linux: `~/.config/Claude/claude_desktop_config.json`

### 19. Future Enhancements

**Potential additions:**
- Board configuration management
- Multi-board upload support
- Sketch testing framework integration
- Real-time serial plotting
- OTA (Over-The-Air) updates for WiFi boards
- Library dependency resolution
- Sketch template management
- Code linting and style checking

### 20. Common Pitfalls

**Avoid:**
- ❌ Assuming Arduino CLI is installed
- ❌ Hardcoding COM ports or paths
- ❌ Not closing serial ports
- ❌ Missing Context in async tools
- ❌ Generic error messages
- ❌ Platform-specific path handling
- ❌ Not checking command success
- ❌ Forgetting to install board cores
- ❌ Using wrong FQBN for board
- ❌ Not waiting for port stabilization

**Do:**
- ✅ Check CLI installation first
- ✅ Use PortDetector for platform-aware detection
- ✅ Always close serial connections
- ✅ Use Context for logging and progress
- ✅ Provide actionable error messages
- ✅ Use Path objects for file paths
- ✅ Check result["success"] on all CLI calls
- ✅ Guide users through core installation
- ✅ Validate FQBN with board list
- ✅ Add delays after opening serial ports

## Quick Reference

### Essential Commands

```bash
# Development
uv sync                                          # Install dependencies
uv run python -m arduino_mcp.server             # Run server
uv run fastmcp run arduino_mcp/server.py:mcp    # Run with FastMCP

# Arduino CLI
arduino-cli core search esp32                    # Search cores
arduino-cli core install esp32:esp32            # Install core
arduino-cli lib search ssd1306                   # Search libraries
arduino-cli lib install "Adafruit SSD1306"      # Install library
arduino-cli board list                           # List connected boards
arduino-cli compile --fqbn arduino:avr:uno .    # Compile
arduino-cli upload -p COM3 --fqbn arduino:avr:uno . # Upload
```

### Key Files

- `server.py` - Main MCP server, all tools/resources/prompts
- `cli_wrapper.py` - Arduino CLI integration, command execution
- `port_detector.py` - Serial port detection, platform-aware
- `image_converter.py` - ImageMagick integration for displays
- `platform_utils.py` - OS detection, cross-platform utilities
- `pyproject.toml` - Project metadata, dependencies
- `uv.lock` - Dependency lock file (committed to repo)

### Useful Links

- FastMCP Documentation: https://gofastmcp.com/
- Arduino CLI Docs: https://arduino.github.io/arduino-cli/
- MCP Specification: https://modelcontextprotocol.io/
- PySerial Docs: https://pyserial.readthedocs.io/

## Embedded Development Context

### Arduino Programming Fundamentals

**Basic sketch structure:**

```cpp
void setup() {
  // Runs once at startup
  Serial.begin(9600);
  pinMode(LED_BUILTIN, OUTPUT);
}

void loop() {
  // Runs repeatedly
  digitalWrite(LED_BUILTIN, HIGH);
  delay(1000);
  digitalWrite(LED_BUILTIN, LOW);
  delay(1000);
}
```

**Common patterns:**
- Digital I/O: `pinMode()`, `digitalWrite()`, `digitalRead()`
- Analog I/O: `analogRead()`, `analogWrite()` (PWM)
- Serial: `Serial.begin()`, `Serial.print()`, `Serial.read()`
- Timing: `delay()`, `millis()`, `micros()`

### Memory Constraints

**Arduino Uno limitations:**
- Flash: 32KB (program storage)
- SRAM: 2KB (runtime memory)
- EEPROM: 1KB (persistent storage)

**Best practices:**
- Use `PROGMEM` for large constants (images, strings)
- Minimize global variables
- Use `F()` macro for string literals: `Serial.println(F("Hello"))`
- Avoid String class, use char arrays
- Be careful with recursion (limited stack)

### Display Integration

**OLED displays (SSD1306, SH1106):**
- I2C or SPI communication
- Typically 128x64 or 128x32 pixels
- Monochrome (1-bit per pixel)
- Use image converter with `format_type="monochrome"`

**TFT displays (ILI9341, ST7735):**
- SPI communication
- Color displays (RGB565)
- Use image converter with `format_type="rgb565"`

**E-Paper displays:**
- Ultra-low power
- Slow refresh (1-2 seconds)
- Excellent outdoor visibility
- Use monochrome or grayscale formats

### Communication Protocols

**Serial (UART):**
- Simple 2-wire (TX/RX)
- Common baud rates: 9600, 115200
- Used for debugging and PC communication

**I2C:**
- 2-wire bus (SDA, SCL)
- Multiple devices on same bus
- Common for sensors and displays

**SPI:**
- 4-wire (MOSI, MISO, SCK, CS)
- Faster than I2C
- Common for displays and SD cards

### Power Management

**Low-power techniques:**
- Use `sleep` modes between operations
- Turn off peripherals when not in use
- Lower clock speed for battery operation
- Use external interrupts for wake-up

**Power considerations:**
- USB power: ~500mA max
- Battery operation: Calculate runtime
- External power supply: Check voltage regulator limits

### Debugging Strategies

**Serial debugging:**
```cpp
Serial.print("Value: ");
Serial.println(value);
```

**LED indicators:**
```cpp
digitalWrite(LED_BUILTIN, state);  // Visual feedback
```

**Timing checks:**
```cpp
unsigned long start = millis();
// ... operation ...
Serial.print("Time: ");
Serial.println(millis() - start);
```

**Common issues:**
- Watchdog timer resets
- Memory corruption (check RAM usage)
- Timing issues (avoid delay in interrupts)
- Floating pins (use INPUT_PULLUP)

## LLM Interaction Tips

### When helping users with Arduino tasks:

1. **Always check prerequisites first** (CLI installed, board connected)
2. **Detect boards automatically** before asking for manual input
3. **Suggest the best port** rather than making users guess
4. **Provide complete workflows** not just single commands
5. **Include error recovery steps** in suggestions
6. **Use prompts as templates** when appropriate
7. **Explain FQBNs** when first mentioned
8. **Recommend appropriate libraries** for common tasks
9. **Consider memory constraints** when suggesting code
10. **Test sketch logic** before uploading to hardware

### Example user request handling:

**User**: "I want to make an LED blink"

**Good Response:**
1. Check if Arduino CLI is installed
2. Detect connected boards
3. Use blink_led_example prompt
4. Create sketch with provided code
5. Compile for detected board
6. Upload to detected port
7. Confirm upload success

**Don't:**
- Assume user knows FQBN
- Skip board detection
- Provide code without context
- Forget to mention required libraries
- Skip compilation before upload

## Conclusion

This MCP server provides a comprehensive bridge between AI agents and Arduino development. By following these best practices, you can create robust, cross-platform Arduino development workflows that work seamlessly with LLM-based assistants.

Key takeaways:
- Leverage all MCP features (Tools, Resources, Prompts, Context)
- Handle platform differences transparently
- Provide clear error messages and recovery paths
- Structure responses for both humans and AI agents
- Test across platforms and error scenarios
- Keep embedded constraints in mind

For questions or contributions: https://github.com/niradler/arduino-mcp

