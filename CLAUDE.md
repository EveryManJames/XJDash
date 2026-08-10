# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# XJDash - Digital Dashboard for 1990 Jeep Cherokee XJ

## Tech Stack
- Python 3.9-3.13 with Kivy 2.3.1 (UI framework)
- pyserial for USB serial communication with Renix Engine Monitor (REM)
- pymodbus 3.7.4 for RS485/Modbus RTU relay control (Waveshare 8-ch module)
- pytest for testing (hardware-free unit tests in tests/; Kivy widgets are not covered)

## Commands
- `python main.py` — run the app in a 480x800 desktop window with simulated REM data (a `venv/` exists at the repo root; activate it or use `venv/bin/python`)
- `pytest tests/` — run all tests; `pytest tests/test_file.py::test_name` for one test
- No lint/format tooling is configured
- The venv must be Python 3.13 or older: Kivy 2.3.1 has no 3.14 wheels, and a source build silently loses the SDL2 window backend ("Unable to find any valuable Window provider")
- On a retina Mac the UI renders at half scale (fixed pixel sizes, density-2 display); on the Pi's density-1 screen it renders as designed

## Architecture

### Data flow
1. `SerialManager` (src/core/serial_manager.py) runs a daemon thread reading REM "Normal mode" lines — 25 space-delimited fields defined in `FIELD_NAMES` (RPM, CTS, MAP, TPS, Batt, etc.) — and pushes each parsed field into `DataManager`.
2. `DataManager` (src/core/data_manager.py) is a **thread-safe singleton** in-memory store with a subscribe/callback API. Instantiating `DataManager()` anywhere returns the same shared instance. (Despite older docs, there is no SQLite logging implemented yet.)
3. Widgets **poll** rather than subscribe: `DashWidget._schedule_update(hz=10)` uses Kivy `Clock` to call `_update(dt)`, which reads `self.data_manager.get(key)` and redraws. UI updates must happen on the Kivy main thread, which is why polling is used instead of serial-thread callbacks.

### Mock fallback pattern (desktop dev always works)
Both hardware interfaces silently fall back to mocks when the library is missing or the device fails to connect:
- `SerialManager` → `MockREMSerial` (src/core/mock_serial.py) generates realistic simulated engine data
- `RelayController` (src/relay/relay_controller.py) → `MockRelayController`
Never assume real hardware; check `use_mock` / `is_mock` if behavior differs.

### Screens
All screens extend `BaseScreen` (src/screens/base_screen.py), which builds a fixed vertical layout: `HeaderBar` (44px) / `self.content` (692px, subclass fills this) / `NavBar` (64px). Screens are registered in `main.py` with `name`, `screen_name`, `title`, and `screen_manager`; `NavBar` switches screens via the ScreenManager with `NoTransition`.

Five screens: gauges (default), transmission (AW-4), relay, diagnostics, settings.

### Widgets
Custom widgets extend `DashWidget` (src/widgets/base_widget.py), which provides:
- `self.skin` — the running app's `SkinManager`
- `self._c(color_name, alpha)` — skin color as Kivy-normalized RGBA (skins store 0-255 RGB)
- `_schedule_update(hz)` / `_update(dt)` — polling lifecycle
Widgets draw with the Kivy canvas API (no .kv files anywhere; all UI is built in Python).

`src/widgets/icons.py` is a self-contained canvas-drawn icon library: `draw_icon(name, x, y, size)` inside a `with self.canvas:` block; icons inherit the active canvas `Color`.

### Skins
`.xjskin` files in `skins/` are JSON themes loaded by `SkinManager` (src/skins/skin_manager.py): `colors` (0-255 RGB lists), `fonts`, `background`, `gauges`, `effects`. **Adding a skin requires two changes**: the `skins/*.xjskin` file AND the hardcoded `SKINS` list in src/screens/settings_screen.py.

Skin changes propagate two ways: polling widgets pick up colors on their next tick automatically; change-gated widgets subscribe via `SkinManager.subscribe(callback)` (use `DashWidget._watch_skin()` or `BaseScreen.register_skin_label()`). `BaseScreen` draws the skin background (solid color, or image with darken overlay — falls back to solid if the image file is missing).

### Relay control
`RelayController` speaks Modbus RTU (`write_coil`/`read_coils`) to the Waveshare module. Safety behaviors: 1.0s minimum cycle time per channel (`MIN_CYCLE_TIME`), and `all_off()` on connect and disconnect (`all_off` bypasses the cycle limit via `set_relay(..., force=True)` — a shutdown must never skip a channel). Channel mapping lives in `DEFAULT_CHANNELS`.

**UI widgets must call `get_cached()`, never `get_relay()`/`get_all_states()`** — the latter are blocking Modbus transactions (9600-baud RS485, 1s timeout) and will freeze the Kivy main thread on real hardware. A background poller thread refreshes the cache with one `read_coils` transaction per cycle; all bus I/O is serialized by `_io_lock`. pymodbus is pinned to 3.7.4: version 3.10+ renamed the `slave` kwarg to `device_id`.

## Critical Constraints
- Kivy `Config.set(...)` calls in main.py MUST come before any `kivy.core.window` import (order matters)
- Max 30fps (`maxfps` config) to save Pi resources; widget polling defaults to 10Hz
- Fixed 480x800 portrait layout — pixel sizes are hardcoded throughout, not responsive

## Hardware Context
- Target: Raspberry Pi 4 (4GB) with Freenove 4.3" DSI touchscreen (800x480, portrait mode)
- REM v4+ connects via USB serial at 115200 baud (`/dev/ttyACM0`)
- Waveshare Modbus RTU 8-Ch Relay Module (B) — remote-mounted via RS485
  - Pi USB-to-RS485 adapter → 2-wire twisted pair → relay module (`/dev/ttyUSB0`, 9600 8N1, slave address 0x01)
  - Relay module powered by Jeep 12V (7-36V input), no GPIO pins used
  - Intended use: AW-4 solenoids, electric fan, light bar, aux relays

## Documentation/
Reference docs for the surrounding hardware project: REM knowledge base, AW-4 TCU replacement plan (Arduino shifter sketches), Kivy architecture doc, and HTML/PNG design mockups in `Documentation/screenshots/`.
