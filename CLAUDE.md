# XJDash - Digital Dashboard for 1990 Jeep Cherokee XJ

## Tech Stack
- Python 3.9+ with Kivy 2.3.0 (UI framework)
- pyserial for USB serial communication with Renix Engine Monitor (REM)
- RPi.GPIO for relay control (Raspberry Pi only, graceful fallback on desktop)
- SQLite for data logging
- Pillow for background image processing
- pytest for testing

## Architecture
- Entry point: `main.py` — configures Kivy for 480x800 portrait mode (4.3" touchscreen)
- `src/core/` — SerialManager (REM communication), DataManager (logging), MockSerial (dev mode)
- `src/skins/` — SkinManager loads .xjskin JSON theme files from `skins/`
- `src/gpio/` — Relay control with MockGPIO fallback for desktop dev
- `src/screens/` — Kivy Screen subclasses (mostly stubs currently)
- `src/widgets/` — Custom Kivy widgets (stubs)
- `Documentation/` — Architecture docs, REM knowledge base, quick start guide

## Development
- `python main.py` — runs in 480x800 window with simulated REM data on desktop
- `pytest tests/` — run tests
- App uses mock data when REM hardware not connected
- Kivy Config must be set BEFORE Window import (order matters in main.py)

## Hardware Context
- Target: Raspberry Pi 4 with 4.3" IPS touchscreen (800x480 physical, used in portrait)
- REM v4+ connects via USB serial
- Optional 8-channel relay module for fan/solenoid/light control
- Max 30fps to save Pi resources
