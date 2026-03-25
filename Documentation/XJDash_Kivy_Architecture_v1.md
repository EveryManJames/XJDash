# XJDash - Kivy-Based Digital Dashboard Architecture
**Version:** 1.0
**Framework:** Kivy + Python 3.9+
**Hardware:** Raspberry Pi 4 + 4.3" Touchscreen (Portrait)
**Last Updated:** December 26, 2024

---

## Why Kivy?

**Advantages for this project:**
- ✅ **Native Python** - Single codebase with REM serial reader
- ✅ **Touchscreen-first** - Built for touch interfaces
- ✅ **Custom theming** - Full control over appearance via KV language
- ✅ **Image backgrounds** - Users can use photos, graphics, custom designs
- ✅ **Widget library** - Pre-built components we can customize
- ✅ **Cross-platform** - Develop on desktop, deploy to Pi
- ✅ **Active community** - Good Pi support and documentation
- ✅ **GPU acceleration** - OpenGL rendering on Pi

**Key Resources:**
- [Kivy Installation Guide](https://kivy.org/doc/stable/gettingstarted/installation.html)
- [Kivy Raspberry Pi Setup](https://kivy.org/doc/stable/installation/installation-rpi.html)
- [Kivy Theming Wiki](https://github.com/kivy/kivy/wiki/Theming-Kivy)
- [Kivy Custom Widgets](https://kivy.org/doc/stable/guide/widgets.html)
- [KivyMD Material Design](https://kivymd.readthedocs.io/en/latest/themes/theming/index.html)

---

## System Architecture

```
┌──────────────────────────────────────────────────────────┐
│  XJDash - Kivy Application (main.py)                     │
│                                                           │
│  ┌────────────────────────────────────────────────────┐  │
│  │  Serial Communication Manager                      │  │
│  │  ────────────────────────────────────────────      │  │
│  │  - Background thread reading REM USB               │  │
│  │  - Parses Normal/Raw mode data                     │  │
│  │  - Publishes to Event Bus                          │  │
│  │  - Auto-reconnect on disconnect                    │  │
│  │  - Status: Connected/Disconnected/Error            │  │
│  └────────────────────────────────────────────────────┘  │
│                                                           │
│  ┌────────────────────────────────────────────────────┐  │
│  │  GPIO Relay Control Manager (OPTIONAL MODULE)      │  │
│  │  ────────────────────────────────────────────      │  │
│  │  - Controls up to 8 relays via GPIO pins           │  │
│  │  - User-configurable:                              │  │
│  │    • AW-4 Solenoid 1, 2, 3 (for Nifty Shifter)    │  │
│  │    • Electric fan control (3-speed)                │  │
│  │    • Light bar / auxiliary lights                  │  │
│  │    • Custom relay assignments                      │  │
│  │  - Safety lockouts and timers                      │  │
│  │  - Touch-based ON/OFF controls on screen           │  │
│  └────────────────────────────────────────────────────┘  │
│                                                           │
│  ┌────────────────────────────────────────────────────┐  │
│  │  Data Logger                                       │  │
│  │  ────────────────────────────────────────────      │  │
│  │  - SQLite database per session                     │  │
│  │  - Records all REM data + GPIO states              │  │
│  │  - Auto-archive old logs                           │  │
│  │  - Export to CSV                                   │  │
│  │  - Optional: WiFi upload to cloud                  │  │
│  └────────────────────────────────────────────────────┘  │
│                                                           │
│  ┌────────────────────────────────────────────────────┐  │
│  │  Skin Manager                                      │  │
│  │  ────────────────────────────────────────────      │  │
│  │  - Loads .xjskin files (JSON config)               │  │
│  │  - Supports:                                       │  │
│  │    • Color schemes                                 │  │
│  │    • Background images (girlfriend pic? ✅)        │  │
│  │    • Custom fonts                                  │  │
│  │    • Gauge layouts                                 │  │
│  │    • Animations/effects                            │  │
│  │  - Hot-reload skins without restart                │  │
│  │  - Share skins with community                      │  │
│  └────────────────────────────────────────────────────┘  │
│                                                           │
│  ┌────────────────────────────────────────────────────┐  │
│  │  Screen Manager (Kivy ScreenManager)               │  │
│  │  ────────────────────────────────────────────      │  │
│  │  Screens:                                          │  │
│  │    1. MainGaugeScreen - Primary gauges            │  │
│  │    2. TransmissionScreen - AW-4 specific           │  │
│  │    3. DiagnosticScreen - Fault codes               │  │
│  │    4. RelayControlScreen - GPIO relays             │  │
│  │    5. SettingsScreen - Configuration               │  │
│  │    6. DataLogScreen - View/export logs             │  │
│  │                                                     │  │
│  │  Navigation: Swipe left/right or bottom tab bar    │  │
│  └────────────────────────────────────────────────────┘  │
│                                                           │
│  ┌────────────────────────────────────────────────────┐  │
│  │  Custom Widgets (Kivy Widgets)                     │  │
│  │  ────────────────────────────────────────────      │  │
│  │  - RPMGauge (circular, customizable)               │  │
│  │  - TemperatureGauge (vertical bar or circle)       │  │
│  │  - BarGraph (horizontal bars for MAP, TPS, etc.)   │  │
│  │  - LCDNumber (segmented LCD digit display)         │  │
│  │  - StatusIndicator (lights for A/C, EGR, etc.)     │  │
│  │  - RelayButton (on/off toggle with status LED)     │  │
│  └────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────┘
```

---

## Project Structure (Updated for Kivy)

```
XJDash/
├── main.py                      # Kivy app entry point
├── xjdash.kv                    # Main Kivy UI definition
├── requirements.txt
├── README.md
│
├── src/
│   ├── __init__.py
│   ├── config.py                # App configuration
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── serial_manager.py    # REM serial communication
│   │   ├── data_manager.py      # Central data store (singleton)
│   │   ├── logger.py            # Data logging to SQLite
│   │   └── event_bus.py         # Pub/sub for data updates
│   │
│   ├── gpio/
│   │   ├── __init__.py
│   │   ├── relay_controller.py  # GPIO relay control
│   │   └── relay_config.json    # User relay assignments
│   │
│   ├── skins/
│   │   ├── __init__.py
│   │   ├── skin_manager.py      # Load/apply skins
│   │   └── base_skin.py         # Base skin class
│   │
│   ├── widgets/
│   │   ├── __init__.py
│   │   ├── rpm_gauge.py         # Circular RPM gauge widget
│   │   ├── temp_gauge.py        # Temperature gauge
│   │   ├── bar_graph.py         # Horizontal bar widget
│   │   ├── lcd_number.py        # LCD-style number display
│   │   ├── status_light.py      # Indicator light widget
│   │   └── relay_button.py      # Relay control button
│   │
│   ├── screens/
│   │   ├── __init__.py
│   │   ├── main_screen.py       # Primary gauge screen
│   │   ├── transmission_screen.py
│   │   ├── diagnostic_screen.py
│   │   ├── relay_screen.py      # GPIO relay controls
│   │   ├── settings_screen.py
│   │   └── datalog_screen.py
│   │
│   └── utils/
│       ├── __init__.py
│       ├── calculations.py      # REM data calculations
│       └── constants.py         # App constants
│
├── skins/                       # Skin library
│   ├── default_amber.xjskin     # Default 1990 amber LCD
│   ├── green_vfd.xjskin         # Green VFD theme
│   ├── red_led.xjskin           # Red LED theme
│   ├── modern_dark.xjskin       # Modern dark theme
│   ├── girlfriend.xjskin        # Example custom background
│   └── README.md                # Skin creation guide
│
├── assets/
│   ├── fonts/
│   │   ├── digital_7.ttf
│   │   ├── lcd_mono.ttf
│   │   └── vt323.ttf
│   │
│   ├── images/
│   │   ├── backgrounds/         # User background images
│   │   ├── icons/               # Status icons
│   │   └── logos/
│   │
│   └── sounds/
│       ├── warning.wav
│       └── notification.wav
│
├── Documentation/               # Your existing docs
│   ├── Renix_Engine_Monitor_Knowledge_Base_v2.md
│   ├── Quick_Start_Dashboard_Implementation_v2.md
│   ├── XJDash_Kivy_Architecture_v1.md  # This file
│   └── Skin_Creation_Guide.md   # To be created
│
├── logs/                        # Session data logs
│   └── .gitkeep
│
└── tests/
    ├── __init__.py
    ├── test_serial.py
    ├── test_gpio.py
    └── test_widgets.py
```

---

## GPIO Relay Control Module

### Hardware Setup

**Recommended Relay Board:** 8-Channel 5V Relay Module (active-low trigger)

**GPIO Pin Mapping** (BCM numbering):
```python
RELAY_PINS = {
    1: 17,  # GPIO17 - Relay 1 (AW-4 Solenoid 1)
    2: 27,  # GPIO27 - Relay 2 (AW-4 Solenoid 2)
    3: 22,  # GPIO22 - Relay 3 (AW-4 Solenoid 3)
    4: 23,  # GPIO23 - Relay 4 (Electric Fan Low)
    5: 24,  # GPIO24 - Relay 5 (Electric Fan High)
    6: 25,  # GPIO25 - Relay 6 (Light Bar 1)
    7: 5,   # GPIO5  - Relay 7 (Light Bar 2)
    8: 6,   # GPIO6  - Relay 8 (Spare / Custom)
}
```

### Safety Features

1. **Ignition Interlock** - Read ignition signal from GPIO pin
   - Relays auto-disable when ignition OFF
   - Prevents battery drain

2. **Timers** - Prevent rapid cycling
   - Minimum ON time: 1 second
   - Minimum OFF time: 1 second

3. **Max Current Protection** - User sets max relays active simultaneously

4. **Override Lock** - Admin PIN to unlock dangerous combinations

### User Configuration

Users can configure each relay via touchscreen:

```json
{
  "relay_1": {
    "name": "Trans Solenoid 1",
    "description": "AW-4 Shift Solenoid 1",
    "enabled": true,
    "auto_control": false,
    "manual_control": true,
    "icon": "transmission"
  },
  "relay_4": {
    "name": "Electric Fan",
    "description": "High-flow electric fan",
    "enabled": true,
    "auto_control": true,
    "trigger_temp": 210,
    "trigger_temp_off": 195,
    "manual_override": true
  }
}
```

### Relay Control Screen UI

```
┌────────────────────────────────┐
│  Relay Control                 │
├────────────────────────────────┤
│                                │
│  [●] Trans Sol 1      [MANUAL] │
│  [○] Trans Sol 2      [MANUAL] │
│  [●] Trans Sol 3      [MANUAL] │
│                                │
│  [●] Fan - Auto       [AUTO]   │
│      Trigger: 210°F            │
│      Current: 195°F            │
│                                │
│  [○] Light Bar 1      [MANUAL] │
│  [○] Light Bar 2      [MANUAL] │
│                                │
│  [○] Spare Relay      [MANUAL] │
│                                │
│  [Settings] [Test All] [Lock]  │
└────────────────────────────────┘
```

---

## Skin System (Enhanced for Kivy)

### Skin File Format (.xjskin)

XJDash skins are JSON files with optional image assets.

**Example: girlfriend.xjskin**
```json
{
  "name": "Sarah's Face",
  "author": "YourName",
  "version": "1.0",
  "description": "Custom background with my girlfriend's photo",

  "background": {
    "type": "image",
    "path": "assets/images/backgrounds/sarah.jpg",
    "opacity": 0.3,
    "blur": 5,
    "darken": 0.6
  },

  "colors": {
    "primary": [255, 255, 255],
    "secondary": [200, 200, 200],
    "accent": [255, 100, 150],
    "warning": [255, 200, 0],
    "critical": [255, 50, 50],
    "background_overlay": [0, 0, 0, 180]
  },

  "fonts": {
    "gauge_numbers": "digital_7.ttf",
    "labels": "lcd_mono.ttf",
    "ui_text": "vt323.ttf"
  },

  "gauges": {
    "rpm_gauge": {
      "style": "circular",
      "color": [255, 255, 255],
      "needle_color": [255, 100, 150],
      "glow": true
    },
    "temp_gauge": {
      "style": "vertical_bar",
      "gradient": [[0, 255, 0], [255, 255, 0], [255, 0, 0]]
    }
  },

  "effects": {
    "smooth_animations": true,
    "glow": true,
    "shadows": true
  }
}
```

### Included Skins

1. **default_amber.xjskin** - 1990 amber LCD (your original vision)
2. **green_vfd.xjskin** - Classic green vacuum fluorescent
3. **red_led.xjskin** - Red LED display
4. **modern_dark.xjskin** - Sleek dark theme with blue accents
5. **retro_crt.xjskin** - CRT monitor with scan lines
6. **girlfriend.xjskin** - Template for custom photo backgrounds

### Skin Sharing Community

Users can:
- Export their skin + assets as .zip
- Share on GitHub/forums
- Import others' skins with one click
- Rate and comment on skins

---

## Development Without Hardware

Since you don't have the Pi with you, here's how we'll develop:

### 1. Desktop Development
Kivy runs on Windows/Mac/Linux! Develop and test on your computer:

```bash
# Install Kivy on your Mac
pip3 install kivy
pip3 install pillow

# Run the app
python3 main.py
```

The app will display in a window (480x800 portrait) on your desktop.

### 2. Mock REM Data
We'll create a **mock serial reader** that simulates REM data:

```python
# src/core/mock_serial.py
import random
import time

class MockREMSerial:
    """Simulates REM serial data for development"""

    def __init__(self):
        self.rpm = 750
        self.cts = 195
        # ... etc

    def read_line(self):
        # Simulate realistic data changes
        self.rpm += random.randint(-50, 50)
        self.cts += random.uniform(-0.5, 0.5)

        return self.format_normal_mode()
```

### 3. GPIO Simulation
Mock GPIO module for desktop development:

```python
# src/gpio/mock_gpio.py
class MockGPIO:
    """Simulates RPi.GPIO for development"""

    BCM = "BCM"
    OUT = "OUT"
    LOW = 0
    HIGH = 1

    @staticmethod
    def setmode(mode):
        print(f"[MOCK GPIO] Set mode: {mode}")

    @staticmethod
    def setup(pin, mode):
        print(f"[MOCK GPIO] Setup pin {pin} as {mode}")

    @staticmethod
    def output(pin, state):
        print(f"[MOCK GPIO] Pin {pin} = {state}")
```

### 4. Mockup Generation
For visual mockups, we'll use **Pillow (PIL)** to render screens as images:

```python
# tools/generate_mockup.py
from kivy.core.window import Window
from kivy.graphics import RenderContext
from PIL import Image

def export_screen_as_image(screen, filename):
    """Export Kivy screen as PNG"""
    # Render screen to texture
    # Save as image file
    pass
```

Run: `python tools/generate_mockup.py --screen main --output mockup_main.png`

---

## Installation Script for Raspberry Pi

When you get your hardware, this one-liner sets everything up:

```bash
curl -sSL https://raw.githubusercontent.com/YourGitHub/XJDash/main/install.sh | bash
```

**What it does:**
1. Updates system packages
2. Installs Python 3.9+ and dependencies
3. Installs Kivy from PiWheels
4. Configures touchscreen input
5. Sets up auto-start on boot
6. Configures GPIO permissions
7. Clones XJDash repo
8. Runs first-time setup wizard

---

## Next Steps

**What would you like to do next?**

1. **Create the base project structure** - Set up all directories and skeleton files
2. **Build a mockup generator** - Create tools to render screens as PNGs
3. **Design the first skin** - Create `default_amber.xjskin` with that sweet 1990s vibe
4. **Build a demo widget** - Create RPM gauge with Kivy and render it as image
5. **Set up GPIO relay module** - Design the relay control system
6. **Write the Skin Creation Guide** - Document how users can make their own skins

My recommendation: **Start with #4** - Build a working RPM gauge widget that we can render as an image. That way you can see what it'll look like and we can iterate on the design before building everything else.

Sound good?

---

**Sources:**
- [Kivy Installation](https://kivy.org/doc/stable/gettingstarted/installation.html)
- [Kivy on Raspberry Pi](https://kivy.org/doc/stable/installation/installation-rpi.html)
- [Kivy Theming Guide](https://github.com/kivy/kivy/wiki/Theming-Kivy)
- [Kivy Widgets](https://kivy.org/doc/stable/guide/widgets.html)
- [Pi GPIO Control](https://opensource.com/article/17/3/operate-relays-control-gpio-pins-raspberry-pi)
- [GPIO Relay Examples](https://gist.github.com/johnwargo/ea5edc8516b24e0658784ae116628277)
