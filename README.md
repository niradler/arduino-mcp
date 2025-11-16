# Arduino MCP Server

A comprehensive [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) server for Arduino CLI interactions, built with [FastMCP](https://gofastmcp.com/). This server enables AI agents to seamlessly interact with Arduino CLI for development, debugging, code verification, and more.

## Features

### 🛠️ **Tools** (All 3 MCP Pillars)

- **CLI Management**: Check installation, get help for commands
- **Board Detection**: List connected boards, find Arduino ports, auto-detect best port
- **Core Management**: Search, install, and list Arduino cores
- **Library Management**: Search, install, and list Arduino libraries
- **Sketch Operations**: Create, compile, and upload sketches
- **Image Conversion**: Convert images to C arrays for display applications (requires ImageMagick)
- **Configuration**: Initialize config, clean cache

### 📚 **Resources**

- `sketch://{path}` - Read Arduino sketch files (.ino, .cpp, .h)
- `arduino-config://main` - Access Arduino CLI configuration
- `board-info://{fqbn}` - Get detailed board information

### 💡 **Prompts**

- **Blink LED Example**: Basic LED blinking sketch template
- **Sensor Reading Example**: Analog sensor reading template
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

#### For Claude Desktop

Add to your MCP configuration file:

**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`  
**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`  
**Linux**: `~/.config/Claude/claude_desktop_config.json`

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

### 1. Basic Setup and Blink LED

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

### 2. Library Installation and Usage

```python
# Search for a library
search_libraries("Adafruit SSD1306")

# Install the library
install_library("Adafruit SSD1306")

# List installed libraries
list_installed_libraries()
```

### 3. Image to C Array Conversion

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

### 4. Resource Access

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
