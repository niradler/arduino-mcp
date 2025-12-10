# Arduino MCP Server

A comprehensive [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) server for Arduino CLI interactions, built with [FastMCP](https://gofastmcp.com/). This server enables AI agents to seamlessly interact with Arduino CLI for development, debugging, code verification, and more.

## Features

### 🛠️ **Tools** (All 3 MCP Pillars)

- **CLI Management**: Check installation, get help for commands
- **Board Detection**: List connected boards, find Arduino ports, auto-detect best port
- **Core Management**: Search, install, and list Arduino cores
- **Library Management**: Search, install, and list Arduino libraries
- **Sketch Operations**: Create, compile, and upload sketches
- **Enhanced Serial Monitor**: Bidirectional communication, buffering, file export
- **Image Conversion**: Convert images to C arrays for display applications (requires ImageMagick)
- **Configuration**: Initialize config, clean cache

### 📚 **Resources**

- `sketch://{path}` - Read Arduino sketch files (.ino, .cpp, .h)
- `arduino-config://main` - Access Arduino CLI configuration
- `board-info://{fqbn}` - Get detailed board information

### 💡 **Prompts**

- **Blink LED Example**: Basic LED blinking sketch template
- **Sensor Reading Example**: Analog sensor reading template
- **Sketch Project Workflow**: IDE-like experience with board attach
- **Full Development Workflow**: Complete Arduino development guide
- **Troubleshooting Guide**: Common issues and solutions

### 🚀 **Advanced Features**

- **Logging**: Comprehensive logging with info, warning, error levels ([source](https://gofastmcp.com/servers/logging))
- **Progress Reporting**: Real-time progress updates for long operations ([source](https://gofastmcp.com/servers/progress))
- **Context Integration**: Full MCP context support for enhanced interactions ([source](https://gofastmcp.com/servers/context))
- **Annotations**: Proper tool annotations for better UX (readOnly, destructive, openWorld hints)

## Prerequisites

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) (Python package manager)
- [Arduino CLI](https://arduino.github.io/arduino-cli/latest/installation/)
- [ImageMagick](https://imagemagick.org/script/download.php) (optional, for image conversion)

## Environment Variables

Customize the server behavior with these optional environment variables:

| Variable                     | Default       | Description                         |
| ---------------------------- | ------------- | ----------------------------------- |
| `ARDUINO_CLI_PATH`           | `arduino-cli` | Path to Arduino CLI executable      |
| `MCP_SKETCH_DIR`             | OS-specific\* | Override default sketch directory   |
| `ARDUINO_SERIAL_BUFFER_SIZE` | `10`          | Serial buffer size in MB            |
| `ARDUINO_CONFIG_FILE`        | Auto-detected | Custom Arduino CLI config file path |

\*Default sketch directories:

- Windows: `%DOCUMENTS%\Arduino`
- macOS: `~/Documents/Arduino`
- Linux: `~/Arduino`

## Installation

1. Clone this repository:

```bash
git clone <your-repo-url>
cd arduino-mcp
```

2. Install dependencies with uv:

```bash
uv sync
```

3. Install Arduino CLI:

```bash
# Windows (using winget)
winget install ArduinoSA.CLI

# macOS
brew install arduino-cli

# Linux
curl -fsSL https://raw.githubusercontent.com/arduino/arduino-cli/master/install.sh | sh
```

## Usage

### Running the Server

#### Using uv:

```bash
uv run python -m arduino_mcp.server
```

#### Using FastMCP CLI:

```bash
uv run fastmcp run arduino_mcp/server.py:mcp
```

#### For HTTP transport:

```bash
uv run fastmcp run arduino_mcp/server.py:mcp --transport http --port 8000
```

### Configuration for MCP Clients

#### For Cursor IDE

The project includes `.cursor/mcp.json` configuration. Cursor will automatically detect it when you open the project.

Alternatively, add to your global Cursor settings:

```json
{
  "mcpServers": {
    "arduino": {
      "command": "uvx",
      "args": ["arduino-mcp"]
    }
  }
}
```

#### For Claude Desktop

Add to your MCP configuration file:

**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`  
**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`  
**Linux**: `~/.config/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "arduino": {
      "command": "uvx",
      "args": ["arduino-mcp"]
    }
  }
}
```

## Testing

To verify the Arduino MCP server is working:

```bash
# Test import
uv run python -c "from arduino_mcp import mcp; print('Server imports successfully')"

# Start the server
uv run fastmcp run arduino_mcp/server.py:mcp
```

Once running in Cursor IDE, you can test the tools directly in the chat interface.

## Example Workflows

### 1. Project-Based Workflow with Board Attach (Recommended)

```python
# Find your connected board
list_connected_boards()

# Create a new sketch
create_new_sketch("MyProject")

# Attach board settings to sketch (IDE-like experience!)
arduino_cli_command("board attach -p COM3 -b arduino:avr:uno MyProject")

# This creates sketch.yaml with your board settings

# Now compile and upload without repeating FQBN/port
compile_sketch("MyProject", "")  # Reads from sketch.yaml
upload_sketch("MyProject", "", "")  # Reads from sketch.yaml

# Monitor serial output with bidirectional communication
serial_monitor(
    port="COM3",
    baudrate=115200,
    duration=30,
    send_commands="LED ON\nLED OFF",  # Send commands to device
    save_to_file="output.log"  # Save buffer to file
)
```

**Why use board attach?**

- Settings persist per-sketch (not globally)
- No need to repeat FQBN and port every time
- Team-friendly (sketch.yaml can be version controlled)
- Works exactly like Arduino IDE 2.x

### 2. Basic Setup and Blink LED

```python
# Check if Arduino CLI is installed
check_arduino_cli_installed()

# Find connected Arduino boards
list_connected_boards()
find_arduino_ports()
get_best_port()

# Create a new sketch
create_new_sketch("BlinkLED", "./sketches")

# Use the blink_led_example prompt for code template

# Compile the sketch
compile_sketch("./sketches/BlinkLED", "arduino:avr:uno")

# Upload to board
upload_sketch("./sketches/BlinkLED", "arduino:avr:uno", "COM3")
```

### 2. Basic Setup and Blink LED

```python
# Check if Arduino CLI is installed
arduino_cli_command("version")

# Find connected Arduino boards
list_connected_boards()
list_ports(arduino_only=True)

# Create a new sketch
create_new_sketch("BlinkLED", "./sketches")

# Use the blink_led_example prompt for code template

# Compile the sketch
compile_sketch("./sketches/BlinkLED", "arduino:avr:uno")

# Upload to board
upload_sketch("./sketches/BlinkLED", "arduino:avr:uno", "COM3")

# Monitor output
serial_monitor("COM3", baudrate=115200, duration=20)
```

### 3. Library Installation and Usage

```python
# Search for a library
search_libraries("Adafruit SSD1306")

# Install the library
install_library("Adafruit SSD1306")

# List installed libraries
list_installed_libraries()
```

### 4. Enhanced Serial Monitor Features

```python
# Basic monitoring (115200 is now the default)
serial_monitor("COM3", duration=30)

# Send commands while monitoring (bidirectional)
serial_monitor(
    port="COM3",
    baudrate=115200,
    duration=30,
    send_commands="GET_STATUS\nSET_LED 1"
)

# Save buffer to file for analysis
serial_monitor(
    port="COM3",
    baudrate=115200,
    duration=60,
    save_to_file="sensor_data.log"
)

# Combined: send commands and save output
serial_monitor(
    port="COM3",
    baudrate=115200,
    duration=45,
    send_commands="START_LOGGING",
    save_to_file="experiment_results.txt"
)
```

**Buffer Features:**

- Circular buffer (10MB default, configurable via env var)
- Memory-safe (won't crash on long-running captures)
- Thread-safe operation
- Automatic statistics (lines captured, buffer usage)

### 5. Image to C Array Conversion

```python
# Check ImageMagick installation
check_imagemagick_installed()

# Convert image to C array for Arduino displays
convert_image_to_c_array(
    "logo.png",
    width=128,
    height=64,
    var_name="logo_bitmap",
    output_file="logo.h"
)
```

### 6. Resource Access

```python
# Read a sketch file
read_resource("sketch://./BlinkLED/BlinkLED.ino")

# Get Arduino configuration
read_resource("arduino-config://main")

# Get board details
read_resource("board-info://arduino:avr:uno")
```

## Tools Reference

### Board & Port Detection

- `check_arduino_cli_installed()` - Verify Arduino CLI installation
- `list_connected_boards()` - List all connected Arduino boards
- `list_serial_ports()` - List all serial ports
- `find_arduino_ports()` - Find Arduino-specific ports
- `get_best_port()` - Auto-detect best port candidate
- `verify_port(port)` - Verify if a port is accessible

### Core Management

- `list_installed_cores()` - List installed Arduino cores
- `search_cores(query)` - Search for Arduino cores
- `install_core(core)` - Install an Arduino core

### Library Management

- `search_libraries(query)` - Search for Arduino libraries
- `install_library(library)` - Install an Arduino library
- `list_installed_libraries()` - List installed libraries

### Sketch Operations

- `create_new_sketch(name, path)` - Create a new Arduino sketch
- `compile_sketch(path, fqbn)` - Compile an Arduino sketch
- `upload_sketch(path, fqbn, port)` - Upload sketch to board

### Utilities

- `get_arduino_help(command)` - Get help for Arduino CLI commands
- `initialize_config()` - Initialize Arduino CLI configuration
- `clean_cache()` - Clean Arduino CLI cache
- `check_imagemagick_installed()` - Check ImageMagick installation
- `convert_image_to_c_array(...)` - Convert images to C arrays

## Common FQBNs

- Arduino Uno: `arduino:avr:uno`
- Arduino Mega 2560: `arduino:avr:mega`
- Arduino Nano: `arduino:avr:nano`
- Arduino Leonardo: `arduino:avr:leonardo`
- ESP32: `esp32:esp32:esp32`
- ESP8266: `esp8266:esp8266:generic`

## Architecture

```
arduino-mcp/
├── arduino_mcp/
│   ├── __init__.py          # Package initialization
│   ├── server.py            # Main MCP server with tools, resources, prompts
│   ├── cli_wrapper.py       # Arduino CLI wrapper
│   ├── port_detector.py     # Serial port detection utilities
│   ├── image_converter.py   # ImageMagick image conversion
│   └── platform_utils.py    # Cross-platform OS detection & handling
├── pyproject.toml           # Project configuration
└── README.md               # This file
```

### Cross-Platform Design

- **platform_utils.py**: Centralized OS detection and platform-specific behavior
- **Automatic detection**: Windows (COM*), macOS (/dev/tty.*), Linux (/dev/ttyUSB*, /dev/ttyACM*)
- **Serial keywords**: Platform-specific Arduino device identification
- **Error handling**: PermissionError for Linux, graceful fallbacks
- **Path handling**: OS-appropriate path separators and formats

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## References

- [FastMCP Documentation](https://gofastmcp.com/)
- [Arduino CLI Documentation](https://arduino.github.io/arduino-cli/)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [FastMCP Tools](https://gofastmcp.com/servers/tools)
- [FastMCP Resources](https://gofastmcp.com/servers/resources)
- [FastMCP Prompts](https://gofastmcp.com/servers/prompts)

## License

MIT License
