# XJDash - Digital Dashboard for 1990 Jeep Cherokee XJ

A modern digital dashboard interface for the Renix Engine Monitor (REM), built with Python and Kivy.

## Features

- 🎨 **Customizable Skins** - Create your own themes with custom colors, fonts, and background images
- 📊 **Live Engine Data** - Real-time display of all REM parameters via USB serial
- ⚡ **RS485 Relay Control** - Waveshare Modbus RTU 8-channel module for AW-4 solenoids, fans, light bars, and more
- 💾 **Data Logging** - SQLite database logging with CSV export (planned)
- 🎯 **Touch-Friendly** - Designed for 4.3" touchscreen in portrait mode
- 🖼️ **Custom Backgrounds** - Show your girlfriend, dog, or favorite landscape while monitoring engine vitals
- 📱 **Responsive** - Multiple screens: gauges, transmission, diagnostics, relay control, settings

## Hardware Requirements

- Raspberry Pi 4 (2GB+ RAM recommended)
- 4.3" IPS touchscreen (800x480 portrait mode)
- Renix Engine Monitor (REM) v4+
- USB cable (REM to Pi)
- Optional: Waveshare Modbus RTU 8-Ch Relay Module (B) + USB-to-RS485 adapter

## Quick Start

### On Your Computer (Development)

```bash
# Clone the repository
git clone https://github.com/YourGitHub/XJDash.git
cd XJDash

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the app
python main.py
```

The app will run in a 480x800 window on your desktop with simulated REM data.

### On Raspberry Pi

```bash
# One-liner installer (coming soon)
curl -sSL https://raw.githubusercontent.com/YourGitHub/XJDash/main/install.sh | bash

# Or manual installation:
git clone https://github.com/YourGitHub/XJDash.git
cd XJDash
pip3 install -r requirements.txt
python3 main.py
```

## Creating Custom Skins

1. Copy an existing `.xjskin` file from the `skins/` directory
2. Edit colors, fonts, gauge styles, and background images
3. Save with a new name: `my_custom_skin.xjskin`
4. Select it in Settings screen

See [Documentation/Skin_Creation_Guide.md](Documentation/Skin_Creation_Guide.md) for details.

### Example: Custom Photo Background

```json
{
  "name": "My Custom Theme",
  "background": {
    "type": "image",
    "path": "assets/images/backgrounds/my_photo.jpg",
    "opacity": 0.3,
    "blur": 5,
    "darken": 0.6
  },
  "colors": {
    "primary": [255, 255, 255],
    "accent": [255, 100, 150]
  }
}
```

## Relay Configuration

Control up to 8 relays from the touchscreen via RS485/Modbus RTU:

```json
{
  "relay_1": {
    "name": "Electric Fan",
    "auto_control": true,
    "trigger_temp": 210,
    "trigger_temp_off": 195
  }
}
```

See [Documentation/XJDash_Kivy_Architecture_v1.md](Documentation/XJDash_Kivy_Architecture_v1.md) for complete relay setup.

## Project Structure

```
XJDash/
├── main.py                  # App entry point
├── requirements.txt
├── src/                     # Source code
│   ├── core/               # Serial, data management
│   ├── relay/              # RS485/Modbus RTU relay control
│   ├── skins/              # Skin system
│   ├── widgets/            # Custom Kivy widgets
│   └── screens/            # UI screens
├── skins/                   # Skin library (.xjskin files)
├── assets/                  # Fonts, images, sounds
├── Documentation/           # Technical docs
└── tools/                   # Development utilities
```

## Documentation

- [XJDash Kivy Architecture](Documentation/XJDash_Kivy_Architecture_v1.md) - Complete system design
- [Renix Engine Monitor Knowledge Base](Documentation/Renix_Engine_Monitor_Knowledge_Base_v2.md) - REM technical details
- [Quick Start Guide](Documentation/Quick_Start_Dashboard_Implementation_v2.md) - Getting started
- Skin Creation Guide (coming soon)

## Development

### Running Tests

```bash
pytest tests/
```

### Generating Mockups

```bash
python tools/generate_mockup.py --screen main --output mockup_main.png
```

## Contributing

This is an open-source project! Contributions welcome:

- Report bugs
- Submit feature requests
- Create and share custom skins
- Improve documentation
- Add new widgets

## Credits

- **Renix Engine Monitor** by Nick Risley - [nickintimedesign.com](https://nickintimedesign.com)
- **XJDash** by James Martin
- Built with [Kivy](https://kivy.org)

## License

MIT License - See LICENSE file for details

## Support

- Issues: [GitHub Issues](https://github.com/YourGitHub/XJDash/issues)
- REM Support: [nickintimedesign.com/support](https://nickintimedesign.com/support/)
- Jeep XJ Community: [jeepforum.com](https://www.jeepforum.com/)

---

**Made with ❤️ for the XJ community**
