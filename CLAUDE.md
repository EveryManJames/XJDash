# XJDash - Digital Dashboard for 1990 Jeep Cherokee XJ

## Tech Stack
- Python 3.9+ with Kivy 2.3.0 (UI framework)
- pyserial for USB serial communication with Renix Engine Monitor (REM)
- pymodbus for RS485/Modbus RTU relay control (Waveshare 8-ch module)
- SQLite for data logging
- Pillow for background image processing
- pytest for testing

## Architecture
- Entry point: `main.py` — configures Kivy for 480x800 portrait mode (4.3" touchscreen)
- `src/core/` — SerialManager (REM communication), DataManager (logging), MockSerial (dev mode)
- `src/skins/` — SkinManager loads .xjskin JSON theme files from `skins/`
- `src/relay/` — RS485/Modbus RTU relay control with MockRelay fallback for desktop dev
- `src/screens/` — Kivy Screen subclasses (mostly stubs currently)
- `src/widgets/` — Custom Kivy widgets (stubs)
- `Documentation/` — Architecture docs, REM knowledge base, quick start guide

## Development
- `python main.py` — runs in 480x800 window with simulated REM data on desktop
- `pytest tests/` — run tests
- App uses mock data when REM hardware not connected
- Kivy Config must be set BEFORE Window import (order matters in main.py)

## Hardware Context
- Target: Raspberry Pi 4 (4GB) with Freenove 4.3" DSI touchscreen (800x480, portrait mode)
- REM v4+ connects via USB serial
- Waveshare Modbus RTU 8-Ch Relay Module (B) — remote-mounted via RS485
  - RS485 interface: Pi USB-to-RS485 adapter → 2-wire twisted pair → relay module
  - Relay module powered by Jeep 12V (7-36V input), no GPIO pins used
  - Modbus RTU protocol, configurable address (1-255), 10A/250VAC per channel
  - Intended use: AW-4 solenoids, electric fan, light bar, aux relays
- Max 30fps to save Pi resources
