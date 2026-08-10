# AW-4 TCU Replacement Module — Product Plan

**Date:** March 26, 2026
**Status:** Draft / Planning
**Codename:** XJShift

---

## Concept

A microcontroller-based module that **fully replaces** the factory AW-4 Transmission Control Unit (TCU) on Renix-era Jeep Cherokee XJs (1987-1990). The factory TCU is primitive — it uses a simple lookup table of throttle position and vehicle speed to fire two shift solenoids. We can do better.

### Competitive Landscape

**Nick Risley's Nifty Shifter JR ($225-$275):**
- Passthrough controller — sits between factory TCU and solenoids
- Auto mode passes through stock TCU behavior, manual mode gives gear control
- LED display (1" or 2") shows current gear
- Supports joystick/switch/sequential inputs
- **Does NOT replace the TCU** — requires it to still be present for auto mode
- Plug-and-play, no wire cutting

**XJShift (our product, ~$25-45):**
- **Fully replaces the factory TCU** — no need for the stock unit at all
- Built-in auto-shift logic (better than stock — user-tunable schedules)
- Manual mode, sport mode, custom shift schedules
- Integrates with XJDash for touchscreen control
- Open source, hackable
- Requires cutting the TCU pigtail (one-time, ~6 wires)

### Two Product Configurations

| Config | Target | Connection | Price Point |
|---|---|---|---|
| **Standalone** | Users without XJDash | Reads own sensors (TPS, VSS, PRNDL) | ~$25-45 |
| **Add-On** | XJDash users | Connects to Pi 4 via UART, gets REM data | ~$20 |

---

## How the AW-4 Works

The AW-4 is a 4-speed automatic with **only 2 shift solenoids** plus a TCC lockup solenoid:

### Shift Table (from Nick Risley's AW4_Shifter.ino)

| Gear | Solenoid 1 (S1) | Solenoid 2 (S2) | Notes |
|---|---|---|---|
| **1st** | ON | OFF | Low range, off-road |
| **2nd** | ON | ON | Both energized |
| **3rd** | OFF | ON | Normal cruising |
| **4th (OD)** | OFF | OFF | Both de-energized (failsafe) |

**TCC Lockup:** 3rd solenoid, locks torque converter to eliminate slippage at cruise.

**Failsafe:** If the module loses power → solenoids de-energize → 4th/OD. Safe at highway speed.

### Factory TCU Datastream (from Nick's research)

The stock TCU transmits a 7-byte diagnostic datastream:
- **Protocol:** UART, standard logic, **500 baud**
- **Frame:** 7 bytes, sent every 30ms, 70ms delay after last byte
- **TX pin:** C4 on TCU connector → Pin D2-15 on Renix diagnostic adapter

| Byte | Content |
|---|---|
| 0 | Module ID |
| 1 | Throttle position steps |
| 2 | Output RPM (× 34) |
| 3 | Brake status, PRNDL position, power mode (bit flags) |
| 4 | Solenoid states + current gear (bits 5-7) |
| 5 | Solenoid fault codes (stored + current) |
| 6 | TPS fault indicators |

**XJShift should replicate this datastream** on its TX pin so the Renix diagnostic adapter still works, and the REM can read transmission data.

### TCU Connector Pinout (32-Way, from FSM MJ-XJ 114)

| Pin | Wire | Signal | XJShift Use |
|---|---|---|---|
| C3 | T9 18TN* | **Road Speed** (VSS) | INPUT — reed switch, 1 pulse/rev |
| C4 | 137 16YL* | Trans Diagnostic Connector | OUTPUT — replicate TCU datastream |
| C5 | 99 18BK | Shift Point Logic Ground | GROUND |
| C8 | T12 18LG | **1-2 Gear Input** (PRNDL) | INPUT — shifter position |
| C9 | T11 18GY* | **D Gear Input** (PRNDL) | INPUT — shifter position |
| C10 | I16 18LB* | **Brake/Torque Converter** | INPUT — brake switch |
| C11 | 177 18TN | Power Input Signal | INPUT |
| C14 | T8 18WT* | **Converter Lockup** (TCC) | OUTPUT — solenoid 3 |
| C15 | T7 18VT* | **S2 Solenoid** | OUTPUT — shift solenoid 2 |
| C16 | T6 18BL* | **S1 Solenoid** | OUTPUT — shift solenoid 1 |
| D1 | T3 18RD | **TPS Voltage Supply** (5V) | POWER — 5V reference to TPS |
| D2 | T4 18GY* | **TPS Input** (0-5V analog) | INPUT — throttle position |
| D3 | T5 18TN/OR | **TPS Ground** | GROUND |
| D7 | 99 18BK | Ground | GROUND |
| D14 | 10 16RD | **Battery** (12V constant) | POWER — always-on 12V |
| D16 | 11 18YL | **Ignition** (12V switched) | POWER — switched 12V |

### Neutral Safety Switch (PRNDL)

The NSS is a separate mechanical switch on the transmission. It provides:
- **Pins B-C:** Continuity in Park and Neutral only (starter lockout — handled independently, NOT our concern)
- **Pins A-E:** Continuity in Reverse
- **Pins A-G:** Continuity in 3rd gear
- **Pins A-H:** Continuity in 1-2 gear

The TCU reads gear position via C8 (1-2 input) and C9 (D gear input) to know whether the shifter is in D, 3, or 1-2. XJShift reads these same inputs to determine user-selected range.

### Speed Sensor (VSS)

- **Type:** 2-wire magnetic reed switch
- **Signal:** 1 pulse per revolution of the output shaft
- **Location:** Driver's side, transmission-to-transfer case adapter
- **Compatibility:** 1987-1997 models (1998+ changed to inductive 4-pulse)
- **Interface:** Simple pulse counting on a GPIO interrupt

---

## Hardware Choice: ESP32 (Not Pi Zero)

After research, the **ESP32** is significantly better than a Pi Zero for this application:

| Factor | Pi Zero | ESP32 |
|---|---|---|
| **ADC** | None (needs external ADS1115) | Built-in 12-bit ADC — reads TPS directly |
| **Boot time** | 20-30 seconds | Milliseconds |
| **Real-time** | Linux, unpredictable timing | Bare metal, deterministic GPIO |
| **Power draw** | 100mA idle | 20-50mA active, µA in sleep |
| **Cost** | $15 | $5-8 |
| **Automotive fit** | Overkill, fragile | Purpose-built for embedded |
| **User programming** | Linux/Python | MicroPython or Arduino IDE |
| **UART** | 1 (shared with console) | 3 hardware UARTs |
| **Pi 4 communication** | USB/UART (fine) | UART, WiFi, or BLE (more options) |
| **CAN bus** | Needs SPI adapter | Native CAN support (ESP32-S3) |

### Recommended Board: ESP32-S3 DevKit

- ~$8 on Amazon
- Built-in WiFi + BLE (wireless XJDash communication possible)
- Native CAN bus support (future expansion)
- 2x 12-bit ADC (reads TPS directly)
- 3x hardware UART (REM + Pi 4 + diagnostic TX)
- MicroPython support (user-friendly programming)
- Boots in milliseconds — transmission is under control instantly after ignition

### ESP32 Pin Assignment

| GPIO | Function | TCU Pin |
|---|---|---|
| GPIO 4 | S1 Solenoid output (via MOSFET) | C16 |
| GPIO 5 | S2 Solenoid output (via MOSFET) | C15 |
| GPIO 6 | TCC Lockup output (via MOSFET) | C14 |
| GPIO 7 | VSS input (pulse counter, interrupt) | C3 |
| GPIO 15 | TPS input (ADC, 0-5V with divider) | D2 |
| GPIO 16 | 1-2 Gear input (PRNDL) | C8 |
| GPIO 17 | D Gear input (PRNDL) | C9 |
| GPIO 18 | Brake switch input | C10 |
| UART1 TX | Diagnostic datastream output (500 baud) | C4 |
| UART2 TX/RX | Communication to Pi 4 (115200 baud) | — |
| USB | Programming / REM connection (standalone) | — |

### TPS Voltage Divider

The TPS outputs 0-5V but ESP32 ADC is 0-3.3V. Simple resistor divider:
- 10kΩ from TPS to GPIO 15
- 18kΩ from GPIO 15 to ground
- Maps 0-5V → 0-3.21V (safe for ESP32)

### Solenoid Driver Circuit (per channel)

```
GPIO ──[10kΩ]──┬── GATE ┐
               │        │ IRLZ44N
              [10kΩ]    │ N-MOSFET
               │  GND ──┘ SOURCE
               └──────── DRAIN ──── Solenoid ──── 12V
                                ┌── Solenoid ──┘
                          1N4007 (flyback diode)
```

- IRLZ44N: Logic-level gate (3.3V drive), handles 50A continuous
- 1N4007: Flyback protection against inductive kick
- 10kΩ pull-down: Ensures solenoid stays OFF when ESP32 boots/resets
- Estimated solenoid draw: 5-10A per channel

---

## Software Architecture

### MicroPython on ESP32

Using MicroPython makes user-customizable shift schedules easy — users edit a simple Python config file over USB or WiFi.

### Core Modules

```
xjshift/
  main.py              — Boot, init hardware, start main loop
  shift_engine.py      — Shift logic, schedules, safety
  hardware.py          — GPIO, ADC, UART, interrupt handlers
  config.py            — User-editable shift schedules + settings
  comms.py             — UART protocol to Pi 4 (add-on mode)
  diagnostics.py       — Replicate TCU datastream on UART1
  vss.py               — Speed calculation from reed switch pulses
```

### User-Editable Shift Schedule (config.py)

```python
# Users edit this file to customize shift points!
# Format: (upshift_mph, downshift_mph, tcc_lock_mph)

SHIFT_SCHEDULE = {
    'normal': {
        1: {'up': 15, 'down': 0},    # Upshift from 1st at 15mph
        2: {'up': 30, 'down': 10},   # Upshift from 2nd at 30, downshift at 10
        3: {'up': 45, 'down': 25},   # Upshift from 3rd at 45, downshift at 25
        4: {'up': 999, 'down': 40},  # Stay in 4th, downshift at 40
    },
    'sport': {
        1: {'up': 25, 'down': 0},
        2: {'up': 45, 'down': 15},
        3: {'up': 60, 'down': 35},
        4: {'up': 999, 'down': 50},
    },
    'tow': {
        1: {'up': 20, 'down': 0},
        2: {'up': 35, 'down': 12},
        3: {'up': 999, 'down': 28},  # No OD in tow mode
        4: {'up': 999, 'down': 999},
    },
}

# TCC lockup settings
TCC_MIN_SPEED = 40      # Don't lock below this speed
TCC_MIN_GEAR = 3        # Don't lock below this gear
TCC_MAX_TPS = 50        # Unlock above this throttle %
TCC_UNLOCK_BRAKE = True # Unlock when brake pressed

# Safety limits
MAX_RPM_DOWNSHIFT = 4500   # Won't downshift if RPM would exceed this
MIN_SPEED_1ST = 0          # Can always be in 1st
MAX_SPEED_1ST = 25         # Force upshift above this in auto
```

### Speed Calculation from Reed Switch

```python
from machine import Pin, Timer
import time

class SpeedSensor:
    """Counts pulses from the AW-4 output shaft reed switch."""

    # Calibration: pulses per mile (depends on tire size + gear ratio)
    # Stock 87-90 XJ: ~8000 pulses/mile with 225/75R15 tires
    PULSES_PER_MILE = 8000

    def __init__(self, pin_num=7):
        self._count = 0
        self._last_count = 0
        self._last_time = time.ticks_ms()
        self._mph = 0.0

        self._pin = Pin(pin_num, Pin.IN, Pin.PULL_UP)
        self._pin.irq(trigger=Pin.IRQ_FALLING, handler=self._pulse)

    def _pulse(self, pin):
        self._count += 1

    def update(self):
        """Call at regular interval (e.g., 100ms) to calculate speed."""
        now = time.ticks_ms()
        dt = time.ticks_diff(now, self._last_time) / 1000.0  # seconds
        if dt <= 0:
            return

        pulses = self._count - self._last_count
        self._last_count = self._count
        self._last_time = now

        # pulses/sec → mph
        pps = pulses / dt
        self._mph = (pps / self.PULSES_PER_MILE) * 3600

    @property
    def mph(self):
        return self._mph

    @property
    def pulse_count(self):
        return self._count
```

### Communication Protocol (Add-On Mode to Pi 4)

Simple JSON-over-UART at 115200 baud:

```json
// Pi 4 → ESP32 (commands)
{"cmd": "shift", "gear": 3}
{"cmd": "tcc", "lock": true}
{"cmd": "mode", "mode": "manual"}
{"cmd": "schedule", "name": "sport"}

// ESP32 → Pi 4 (status, 10Hz)
{"gear": 3, "s1": false, "s2": true, "tcc": true,
 "mph": 55, "mode": "auto", "rpm": 2850, "tps": 22,
 "prndl": "D", "brake": false}
```

### Diagnostic Datastream Emulation

XJShift replicates the factory TCU's 7-byte UART output on pin C4 so:
- REM diagnostic tools still work
- Any TCU datastream reader sees valid data
- Format: 500 baud, 7 bytes, 30ms interval (matching factory spec)

---

## Safety Features

1. **Boot in 4th/OD:** Solenoids de-energized at startup = 4th gear. Safe default.
2. **Power-loss failsafe:** Same — solenoids off = 4th gear at any speed.
3. **Pull-down resistors:** Hardware ensures solenoids OFF during ESP32 reset/boot.
4. **Rev-limited downshifts:** Won't allow downshift if resulting RPM > 4500.
5. **Speed-limited 1st gear:** Force upshift above 25mph in auto mode.
6. **TCC protection:** Never engage lockup in 1st/2nd, below 40mph, or with brake pressed.
7. **Watchdog timer:** ESP32 hardware watchdog resets if main loop hangs >500ms.
8. **PRNDL awareness:** Respects shifter position — no 4th gear in "1-2" range, etc.
9. **Brake-on TCC unlock:** Always unlocks torque converter when brake is pressed.

---

## Bill of Materials

| Part | Est. Price | Notes |
|---|---|---|
| ESP32-S3 DevKit | $8 | WiFi, BLE, ADC, 3 UARTs, native CAN |
| 3x IRLZ44N N-channel MOSFET | $3 | Logic-level, one per solenoid |
| 3x 1N4007 flyback diode | $1 | Solenoid protection |
| 6x 10kΩ resistor | $0.50 | Gate pull-downs + voltage divider |
| 1x 18kΩ resistor | $0.10 | TPS voltage divider |
| Small perfboard or custom PCB | $3 | Driver board |
| Buck converter 12V→5V (standalone) | $3 | Not needed in add-on mode |
| Weatherproof connector | $5 | Deutsch DT or equivalent |
| 3D-printed enclosure | $3 | ABS, under-dash or engine bay mount |
| Wire, heat shrink, misc | $3 | |
| **TOTAL (Standalone)** | **~$30** | |
| **TOTAL (Add-On to XJDash)** | **~$22** | Powered from Pi 4 USB |

Vs. Nifty Shifter JR: **$225-275** (and doesn't replace the TCU)

---

## Development Phases

### Phase 1: Bench Proof of Concept
- ESP32 + MicroPython on breadboard
- LEDs simulating solenoids
- Potentiometer simulating TPS
- Button simulating VSS pulses
- Basic auto-shift schedule working
- UART communication to Pi 4

### Phase 2: Driver Board Prototype
- Perfboard with 3x MOSFET drivers
- TPS voltage divider
- VSS input with interrupt
- Connect to real AW-4 solenoids (bench test with ohmmeter first)
- PRNDL inputs

### Phase 3: Vehicle Integration
- Install in Jeep, splice TCU pigtail to connector board
- Road test auto-shift schedule tuning
- Validate failsafe (kill power mid-drive → should coast in 4th)
- Tune TCC lockup logic
- Diagnostic datastream emulation

### Phase 4: XJDash Integration
- UART protocol between ESP32 and Pi 4
- Updated Transmission screen: manual shift buttons, mode selector
- Real-time speed/gear/TPS display from XJShift data
- Shift schedule editor in Settings screen

### Phase 5: Product Polish
- Custom PCB (KiCad, order from JLCPCB)
- Professional 3D-printed enclosure
- Breakout connector board for clean TCU pigtail splice
- Installation guide with photos
- User guide for custom shift schedules
- WiFi OTA firmware updates

---

## XJDash Transmission Screen (Updated for XJShift)

When XJShift is connected, the Transmission screen gains:

### Manual Mode Controls
- **Large gear buttons:** Tap 1, 2, 3, OD to shift directly
- **Sequential shift:** Swipe up/down or tap +/- buttons
- **TCC toggle:** Lock/unlock torque converter manually

### Mode Selector
- **NORMAL** — Default shift schedule
- **SPORT** — Higher RPM shift points, holds gears longer
- **TOW** — No overdrive, earlier downshifts for engine braking
- **MANUAL** — Full manual control from touchscreen

### Live Data
- Current gear (large indicator)
- Solenoid S1/S2/TCC states
- Vehicle speed (from VSS, not GPS)
- TPS percentage
- PRNDL position
- Shift schedule visualization

### Shift Schedule Editor (Settings)
- Visual slider for each gear's upshift/downshift points
- Save custom schedules with names
- Share schedules with other XJShift users

---

## Why This Is a Great Product

1. **Factory TCU is the weak link** — known to fail on 30+ year old XJs, NLA from Chrysler
2. **Only alternative is $225+ Nifty Shifter** — and it still needs the stock TCU for auto mode
3. **XJShift is a full replacement** at 1/10th the cost
4. **Ridiculously simple** — 2 shift solenoids + 1 TCC + lookup table
5. **XJ community is massive** — thousands of Renix XJs on the road
6. **Touchscreen shift control** (via XJDash) is a killer feature nobody else offers
7. **User-tunable shift schedules** — tow mode, sport mode, custom — via simple Python config
8. **Open source** — community can contribute, fork, and improve
9. **ESP32 platform** — cheap, reliable, boots instantly, MicroPython for easy hacking
