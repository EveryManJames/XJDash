# Renix Engine Monitor Digital Dashboard - Complete Technical Documentation

## Project Overview

**Goal:** Build a digital dashboard add-on for the Renix Engine Monitor (REM) that provides:
- Modern touchscreen gauge display
- Real-time data visualization
- Advanced datalogging with WiFi capability
- GPS integration for location-based data
- Superior UI/UX compared to the REM's small OLED screen

**Architecture:** The REM handles all diagnostic communication with the Jeep's ECU, TCU, and ABS modules. Your dashboard receives processed data from the REM via USB serial connection and displays it with a modern interface.

**Hardware Selection:**
- **Main Computer:** Raspberry Pi 4 (2GB RAM minimum)
- **Display:** 4.3" IPS touchscreen (portrait orientation)
- **Mounting:** Custom 3D-printed bracket (already designed) - mounts left of factory gauges
- **Data Connection:** USB cable from REM to Raspberry Pi
- **Power:** 12V vehicle power with step-down to 5V USB-C for Pi

---

## Hardware Architecture

### System Component Overview

```
┌─────────────────────────────────────────────────────┐
│  1990 Jeep Cherokee XJ (Renix System)              │
│                                                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │ 4.0L ECU │  │  AW-4    │  │ Bendix 9 │        │
│  │ (Bendix) │  │   TCU    │  │   ABS    │        │
│  └─────┬────┘  └─────┬────┘  └─────┬────┘        │
│        │             │              │              │
│        └─────────────┴──────────────┘              │
│                      │                              │
│                      │ (Diagnostic Port)            │
│                      ▼                              │
│         ┌────────────────────────┐                 │
│         │  Renix Engine Monitor  │                 │
│         │  (Teensy-based)        │                 │
│         │  - Processes datastream│                 │
│         │  - OLED display        │                 │
│         │  - USB serial output   │                 │
│         └───────────┬────────────┘                 │
│                     │ USB Serial                   │
│                     │ (115200 baud)                │
└─────────────────────┼──────────────────────────────┘
                      │
                      ▼
         ┌────────────────────────┐
         │   Raspberry Pi 4       │
         │   - Python/Node.js app │
         │   - Serial data reader │
         │   - Dashboard renderer │
         │   - Data logger        │
         │   - WiFi sync          │
         └───────────┬────────────┘
                     │ DSI/HDMI
                     ▼
         ┌────────────────────────┐
         │  4.3" IPS Touchscreen  │
         │  (Portrait Mode)       │
         │  - Live gauges         │
         │  - Diagnostic codes    │
         │  - Datalogging UI      │
         │  - Settings menu       │
         └────────────────────────┘
```

### Data Flow

1. **Jeep Systems → REM:** REM communicates with ECU/TCU/ABS via diagnostic port (proprietary Bendix protocols)
2. **REM → Raspberry Pi:** REM streams processed data via USB serial (115200 baud, configurable output format)
3. **Pi → Display:** Raspberry Pi renders dashboard interface and displays on touchscreen
4. **Pi → Storage:** All data logged locally to Pi's storage (SD card or USB drive)
5. **Pi → Cloud (Optional):** WiFi sync uploads logs for remote viewing/analysis

---

## Recommended 4.3" Touchscreen Options

For portrait-mounted dashboard next to factory gauges:

### Option 1: Waveshare 4.3" DSI Touchscreen
- **Resolution:** 800x480 IPS
- **Interface:** DSI (Direct Serial Interface) - faster than HDMI
- **Touch:** Capacitive multi-touch
- **Pros:** Native Pi integration, low latency, excellent viewing angles
- **Mounting:** 4.3" in portrait = 2.6" wide × 3.8" tall (compact fit)

### Option 2: Elecrow 5" HDMI Touchscreen (Alternative)
- **Resolution:** 800x480 IPS
- **Interface:** HDMI + USB touch
- **Touch:** Capacitive
- **Note:** Slightly larger but may fit depending on bracket design

**Recommendation:** Waveshare 4.3" DSI for direct Pi integration and lower power consumption.

---

## REM Datalogging Capabilities (KEY DISCOVERY)

### Current REM Serial Output Modes

The REM already has built-in datalogging via USB serial output. Configure in: **Options > More > Settings > Advanced Menu > USB Output**

**Available Modes:**

1. **Disabled:** No USB output

2. **Normal Mode:** Human-readable calculated values
   - Output: `Time, MAP, VAC, CTS, IAT, RPM, Batt, o2, exhaust, o2_Heater, Loop, EGR, TPS, TPS_mode, IGN, Knock, INJ_ms, INJ_DC, Sync, STFT, LTFT, AC_SW, AC_REQ, GPH, AFR`
   - Best for: Easy parsing, immediate use
   - Format: CSV-like, space-delimited

3. **Raw Mode:** Uncalculated 8-bit datastream
   - All bytes from ECU/TCU/ABS modules
   - Requires applying math formulas from datastream documentation
   - Best for: Deep analysis, custom calculations
   - See: [Datastream documentation](https://nickintimedesign.com/reverse-engineering/)

4. **Passthrough Mode:** Unmodified 62,500 baud ECU stream
   - For compatibility with other Renix loggers
   - Direct ECU communication passthrough

### Serial Communication Settings

- **Baud Rate:** 115200 (default for Normal/Raw modes)
- **Data Bits:** 8
- **Parity:** None
- **Stop Bits:** 1
- **Flow Control:** None
- **Port:** `/dev/ttyACM0` (typical on Raspberry Pi)

### Timing Information

- **Update Interval:** ~4 frames per second (250ms between frames)
- **Frame marker:** Timestamp in milliseconds (since REM power-on)
- **Note:** Update rate varies with engine RPM (more processing = slower updates)

---

## Implementation Strategy

### Phase 1: Serial Data Capture (Foundation)

**Objective:** Establish reliable communication between REM and Raspberry Pi

**Tasks:**
1. **Physical Connection**
   - USB cable from REM to Pi (USB-A to Micro-USB)
   - Verify Pi recognizes REM as serial device (`ls /dev/ttyACM*`)

2. **Serial Reader Development**
   - Python script using `pyserial` library
   - Parse incoming data stream (Normal mode recommended for MVP)
   - Handle reconnection if REM power cycles

3. **Data Structure**
   ```python
   {
     "timestamp": 12345,  # Milliseconds since REM startup
     "MAP": 14.5,         # Manifold Absolute Pressure (inHg)
     "VAC": 15.4,         # Manifold Vacuum (inHg)
     "CTS": 195,          # Coolant Temp (°F)
     "IAT": 102,          # Intake Air Temp (°F)
     "RPM": 2500,
     "Batt": 14.2,        # Battery voltage
     "o2": 2.5,           # O2 sensor voltage
     # ... (25 total parameters)
   }
   ```

**Sample Python Code:**
```python
import serial
import time

ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1)

while True:
    if ser.in_waiting:
        line = ser.readline().decode('utf-8').strip()
        values = line.split()
        
        # Parse into structured data
        data = {
            'timestamp': int(values[0]),
            'MAP': float(values[1]),
            'VAC': float(values[2]),
            # ... etc
        }
        
        print(f"RPM: {data.get('RPM', 0)}, Temp: {data.get('CTS', 0)}°F")
```

### Phase 2: Dashboard UI (Core Functionality)

**Objective:** Display live data with clean, readable gauges

**Framework Options:**
- **Electron + Web Tech:** Familiar HTML/CSS/JS, easy styling
- **Kivy (Python):** Native Python, good for embedded displays
- **Qt/PyQt:** Professional-looking, excellent graphics
- **React Native:** If you want mobile-first design patterns

**UI Layout (Portrait 4.3" - 480x800 pixels)**

```
┌──────────────────────┐
│   [Header Bar]       │ ← Vehicle name, time, warning icons
├──────────────────────┤
│                      │
│   ┌──────────────┐   │ ← Large primary gauge (RPM)
│   │              │   │   Circular dial, animated needle
│   │     2500     │   │
│   │              │   │
│   └──────────────┘   │
│                      │
├──────────────────────┤
│  Temp: 195°F  ▲      │ ← Secondary readouts (scrollable)
│  MAP:  14.5"  ▼      │
│  TPS:  45%           │
│  o2:   Rich          │
├──────────────────────┤
│  [Codes] [Log] [GPS] │ ← Bottom navigation
└──────────────────────┘
```

**Key Gauges to Display:**
- **Primary:** RPM (large circular dial)
- **Secondary:** Coolant temp, MAP/VAC, TPS, Battery voltage
- **Status indicators:** Loop status (open/closed), EGR, A/C status
- **Warnings:** Auto-highlight out-of-range values (red text, flash)

### Phase 3: Datalogging System (Enhanced)

**Objective:** Superior datalogging compared to REM's incomplete SD card feature

**Local Storage:**
- **Format:** SQLite database OR CSV files (one per session)
- **Location:** `/home/pi/jeep_logs/` or external USB drive
- **Rotation:** Auto-archive old logs after 30 days
- **Size management:** Compress logs older than 7 days

**Session Management:**
```python
import sqlite3
from datetime import datetime

# Start new session when REM connects
session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
db = sqlite3.connect(f'/home/pi/jeep_logs/{session_id}.db')

# Log every datapoint
cursor.execute('''
    INSERT INTO datalog 
    (timestamp, rpm, cts, iat, map, tps, battery, o2, ...) 
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ...)
''', (data['timestamp'], data['RPM'], ...))
```

**WiFi Sync (Optional but Recommended):**
- Upload completed sessions to cloud storage (Dropbox, Google Drive, custom server)
- Web-based log viewer accessible from phone/computer
- Email alerts for diagnostic codes or critical events
- Remote monitoring while vehicle is parked

**Example:**
```python
def upload_log_to_cloud(session_file):
    # Compress log
    import gzip
    with open(session_file, 'rb') as f_in:
        with gzip.open(f'{session_file}.gz', 'wb') as f_out:
            f_out.writelines(f_in)
    
    # Upload via SFTP, AWS S3, Dropbox API, etc.
    # ...
```

### Phase 4: GPS Integration

**Hardware:** USB GPS module (e.g., U-blox VK-172)
- **Interface:** USB, appears as `/dev/ttyUSB0`
- **Protocol:** NMEA sentences (standard GPS format)
- **Power:** 5V from Pi USB port

**Data to Capture:**
- **Location:** Latitude, longitude, altitude
- **Speed:** GPS speed (compare to trans output shaft speed for slip detection)
- **Time:** Accurate timestamp (alternative to REM millis counter)
- **Distance:** Track mileage per session

**Use Cases:**
- Tag logs with GPS location (know where issues occurred)
- Speed/distance calculations for MPG verification
- Export to Google Maps for visual track overlay
- Alert if vehicle moves while parked (anti-theft notification)

**Python GPS Reading:**
```python
import pynmea2

gps = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)

while True:
    line = gps.readline().decode('utf-8')
    if line.startswith('$GPGGA'):  # GPS fix data
        msg = pynmea2.parse(line)
        print(f"Lat: {msg.latitude}, Lon: {msg.longitude}")
```

### Phase 5: Advanced Features

**Diagnostic Code Display:**
- Parse fault codes from REM data stream
- Display human-readable descriptions (from REM Codes Description page)
- Code history log with timestamps

**Customizable Gauge Screens:**
- Multi-page layout (swipe to switch)
- User-configurable gauge selection
- Night mode (red/dim colors for nighttime driving)

**Performance Tracking:**
- 0-60 timer (using GPS speed)
- Quarter-mile timer
- Peak RPM/speed tracking per session

**Maintenance Reminders:**
- Oil change countdown (based on logged mileage)
- Service interval warnings
- Custom maintenance schedule input

---

## REM Datastream Technical Details

### Bendix 4.0L ECU Datastream (Primary Source)

**Protocol:**
- **UART:** Inverted logic, 62,500 baud
- **Frame Length:** 33 bytes
- **Update Rate:** Variable (depends on engine speed)
- **TX Pin:** ECU Pin C12 → Diagnostic Port D2-1

**Key Data Bytes:**

| Byte | Parameter | Formula | Description |
|------|-----------|---------|-------------|
| 0 | Program Version | HEX | 0xB0=old, 0xB1=new |
| 1 | Vehicle Cal | Bit 2,7 | Auto/manual trans flag |
| 3 | MAP Sensor | #/9.13+3.1 | Manifold pressure (inHg) |
| 4 | CTS | #*1.125-40 | Coolant temp (°F) |
| 5 | IAT | #*1.125-40 | Intake air temp (°F) |
| 6 | Battery | #/16.24 | Battery voltage (V) |
| 7 | O2 Sensor | #/51.2 | O2 voltage (0-5V) |
| 8-9 | RPM | 20,000,000/# | Engine RPM |
| 12 | TPS | #/2.55 | Throttle position (%) |
| 13 | Spark Advance | DEC | Degrees BTDC |
| 16 | Barometric | #/9.13+3.1 | Baro pressure (inHg) |
| 19 | Injector Pulse | #*0.128 | Pulse width (ms) |
| 24 | Short Term FT | DEC | Fuel trim offset |
| 26 | Long Term FT | DEC | Fuel trim gain |
| 29 | Input Flags | Bits | A/C, NSS, starter signals |
| 30 | Output Flags | Bits | Relay faults |

**Loop Status (Byte 18):**
- Bit 1,6: Decel/Closed loop indicators
- Bit 3: EGR status (ON/OFF)
- Bit 7: Exhaust mixture (Lean/Rich)

**Full documentation:** https://nickintimedesign.com/renix-4l-ecu-datastream/

### AW-4 Transmission Datastream (Secondary Source)

**Protocol:**
- **UART:** Standard logic, 500 baud (very slow!)
- **Frame Length:** 7 bytes
- **Update Rate:** 4 frames/second (250ms)
- **TX Pin:** TCU Pin C4 → Diagnostic Port D2-15

**Key Data Bytes:**

| Byte | Parameter | Formula | Description |
|------|-----------|---------|-------------|
| 0 | Module ID | DEC | 1=4.0L, 2=2.5L |
| 1 | TPS Steps | DEC | Trans TPS (0-7) |
| 2 | Output RPM | #*34 | Trans output shaft RPM |
| 3 | Brake/PRNDL | Bits | Brake switch, shifter position |
| 4 | Solenoids/Gear | Bits | Current gear, solenoid states |
| 5 | Solenoid Faults | Bits | Current/stored fault codes |
| 6 | TPS Fault | Bit 0 | Throttle position sensor fault |

**Current Gear Decoding (Byte 4, Bits 5-7):**
- Bits 5,6: 00=2nd, 01=3rd, 10=1st, 11=4th
- "L" indicator when torque converter locked

**Note:** TCU baud rate is so slow that Teensy-based systems need special clock configuration or Serial3 port.

**Full documentation:** https://nickintimedesign.com/aw-4-tcu-datastream/

### Bendix 9 ABS Module (Tertiary Source - Optional)

**Protocol:**
- **UART:** Inverted logic, 62,500 baud
- **Frame Length:** 16 bytes
- **TX Pin:** ABM Pin C4 → Diagnostic Port D2-5

**Available Data:**
- Wheel speeds (all four corners, MPH)
- ABS solenoid states (build/decay/isolation)
- Fault codes (809-818 series)
- Brake switch, G-switch, pressure switches

**Note:** Only present on 1989-1990 XJs with factory ABS option (rare).

**Full documentation:** https://nickintimedesign.com/bendix-9-abs-module-datastream/

---

## REM Gauge Definitions (For Dashboard Display)

These are the calculations and meanings behind each gauge value. Use these for tooltip help text or gauge labels.

### Engine Sensors

**MAP (Manifold Absolute Pressure):**
- **Range:** 3.1-31" Hg
- **Normal Idle:** <15" Hg (high vacuum)
- **WOT:** 15-30" Hg (low vacuum)
- **Formula:** Byte3 / 9.13 + 3.1
- **Note:** Absolute pressure, not relative vacuum

**VAC (Manifold Vacuum):**
- **Range:** 0-25" Hg
- **Normal Idle:** >15" Hg
- **Formula:** Baro - MAP
- **Use:** Traditional vacuum gauge reading (relative to atmosphere)

**CTS (Coolant Temperature):**
- **Range:** -40 to 247°F
- **Normal Operating:** 180-220°F (210°F ideal)
- **Warning:** >230°F (overheating)
- **Formula:** Byte4 * 1.125 - 40

**IAT (Intake Air Temperature):**
- **Range:** -40 to 247°F
- **Expected:** Ambient + 20-50°F (engine bay heating)
- **Formula:** Byte5 * 1.125 - 40

**RPM (Engine Speed):**
- **Range:** 300-5000 RPM (300 minimum for sensor detection)
- **Idle:** 600-900 RPM (750 target)
- **Redline:** 5000 RPM (ECU fuel cutoff)
- **Formula:** 20,000,000 / (Byte9 * 256 + Byte8)
- **Note:** Actually spark timing gap in microseconds

**Battery Voltage:**
- **Range:** 0-15.7V
- **Key Off:** 12.4-12.8V (healthy battery)
- **Running:** 13.5-14.5V (alternator charging)
- **Formula:** Byte6 / 16.24
- **Note:** Reads from fuel pump relay circuit (shows 0V key-off)

### Fuel System

**O2 Sensor Voltage:**
- **4.0L Range:** 0-5V
- **2.5L Range:** 0-1000mV
- **Formula:** Byte7 / 51.2 (4.0L) or Byte7 / 51.2 * 1000 (2.5L)
- **Rich:** <2.5V (4.0L) or <500mV (2.5L)
- **Lean:** >2.5V (4.0L) or >500mV (2.5L)
- **Note:** Should constantly swing in closed loop

**A/F (Air/Fuel Ratio - Estimated):**
- **Range:** 13-16:1
- **Stoichiometric:** 14.7:1
- **Rich:** 13-14:1 (more power, less economy)
- **Lean:** 15-16:1 (less power, more economy)
- **Note:** REM estimate only, not accurate for tuning

**Loop Status:**
- **OPEN:** Cold engine, ignores O2 sensor
- **CLSD:** Warm engine, using O2 feedback
- **DECEL:** Fuel cut-off mode (>1200 RPM, closed throttle)

**EGR (Exhaust Gas Recirculation):**
- **ON:** EGR valve open (closed loop, cruise)
- **OFF:** EGR valve closed (startup, idle, WOT, decel)

**TPS (Throttle Position Sensor):**
- **Range:** 17-94%
- **Closed Throttle:** 14-18% (adjust to 17%)
- **Wide Open:** ~94% (never reaches 100%)
- **Formula:** Byte12 / 2.55

**Throttle Mode:**
- **CLSD:** ECU sees throttle fully closed
- **PART:** Throttle partially open (normal operation)
- **WOT:** Wide open throttle (open loop mode)

**Injector Pulse Width:**
- **4.0L Range:** 0-32.6ms
- **4.0L Idle:** 4-8ms (closed loop)
- **2.5L Idle:** 1-2ms (single TB injector)
- **Formula:** Byte19 * 0.128

**Injector Duty Cycle:**
- **Idle:** 2-10%
- **Max Safe:** <80%
- **Formula:** (Pulse Width * RPM) / 1200

**STFT (Short Term Fuel Trim):**
- **Range:** 0-255 (128 = base)
- **<128:** ECU reducing fuel
- **>128:** ECU adding fuel
- **Note:** Only updates in closed loop

**LTFT (Long Term Fuel Trim):**
- **Range:** 0-255 (128 = base)
- **Stable value** after ECU adapts to average fueling needs
- **Interpretation:** Same as STFT but long-term average

### Ignition System

**Spark Advance (Timing):**
- **Range:** 0-40° BTDC
- **Idle:** 10-20°
- **Cruise/WOT:** 30-40°
- **Formula:** Byte13 (decimal)

**Knock Sensor (4.0L only):**
- **Idle:** ~0
- **2500 RPM:** 10-100 (normal increase with RPM)
- **High knock:** Spark advance will retard

**Knock Retard:**
- **REM-calculated:** Base timing - current timing
- **Shows how much timing is being pulled due to knock**

### Transmission (Auto Only)

**Trans Output RPM:**
- **Formula:** Byte2 * 34
- **Min detection:** 300 RPM

**MPH (Vehicle Speed):**
- **Calculated from:** Output RPM × tire size ÷ final drive ratio
- **Requires configuration:** Tire diameter, axle gears, transfer case
- **Note:** Cannot account for 4-Lo range

**Current Gear:**
- **1st, 2nd, 3rd, 4th**
- **"L" indicator:** Torque converter locked

**Trans TPS Steps:**
- **Range:** 0-7 steps
- **Use:** TCU shift point modification based on driving style

### Auxiliary Systems

**A/C Select:**
- **ON:** A/C mode switch active AND low pressure switch closed
- **OFF:** A/C not requested

**A/C Request:**
- **YES:** Evaporator temp acceptable for compressor operation
- **NO:** Temp out of range OR A/C select off

**Starter Signal:**
- **ON:** Starter relay active
- **OFF:** Not cranking
- **Note:** May be blocked by NSS reading

**NSS (Neutral Safety Switch):**
- **YES:** Shifter in Park or Neutral
- **NO:** Shifter in Drive gear

---

## Implementation Code Examples

### Complete Serial Reader (Python)

```python
#!/usr/bin/env python3
"""
Renix Engine Monitor Serial Data Reader
Reads REM "Normal" mode output via USB serial
"""

import serial
import time
import json
from datetime import datetime

# Serial port configuration
SERIAL_PORT = '/dev/ttyACM0'
BAUD_RATE = 115200

# Normal mode field order (from REM documentation)
FIELD_NAMES = [
    'timestamp', 'MAP', 'VAC', 'CTS', 'IAT', 'RPM', 'Batt', 'o2',
    'exhaust', 'o2_Heater', 'Loop', 'EGR', 'TPS', 'TPS_mode',
    'IGN', 'Knock', 'INJ_ms', 'INJ_DC', 'Sync', 'STFT', 'LTFT',
    'AC_SW', 'AC_REQ', 'GPH', 'AFR'
]

def connect_rem():
    """Establish serial connection to REM"""
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        print(f"Connected to REM on {SERIAL_PORT}")
        return ser
    except serial.SerialException as e:
        print(f"Error: {e}")
        return None

def parse_line(line):
    """Parse space-delimited data line into dictionary"""
    try:
        values = line.strip().split()
        if len(values) != len(FIELD_NAMES):
            return None
        
        data = {}
        for i, field in enumerate(FIELD_NAMES):
            # Convert numeric fields to appropriate types
            if field in ['Loop', 'EGR', 'TPS_mode', 'exhaust', 'AC_SW', 'AC_REQ']:
                data[field] = values[i]  # Keep as string (ON/OFF, OPEN/CLSD, etc.)
            else:
                try:
                    data[field] = float(values[i])
                except ValueError:
                    data[field] = values[i]
        
        return data
    except Exception as e:
        print(f"Parse error: {e}")
        return None

def main():
    """Main reading loop"""
    ser = connect_rem()
    if not ser:
        return
    
    print("Reading data... (Ctrl+C to stop)")
    print("-" * 60)
    
    try:
        while True:
            if ser.in_waiting:
                line = ser.readline().decode('utf-8', errors='ignore')
                data = parse_line(line)
                
                if data:
                    # Print key values
                    print(f"RPM: {data['RPM']:5.0f} | "
                          f"Temp: {data['CTS']:3.0f}°F | "
                          f"MAP: {data['MAP']:4.1f}\" | "
                          f"TPS: {data['TPS']:3.0f}% | "
                          f"Loop: {data['Loop']}")
                    
                    # Optional: Save to file or database
                    # save_to_database(data)
            
            time.sleep(0.01)  # Small delay to prevent CPU thrashing
    
    except KeyboardInterrupt:
        print("\nStopped by user")
    finally:
        ser.close()

if __name__ == '__main__':
    main()
```

### Dashboard UI (Electron + React Example)

**Main Dashboard Component:**

```javascript
// dashboard.jsx
import React, { useState, useEffect } from 'react';
import GaugeCircular from './GaugeCircular';
import StatusBar from './StatusBar';

const Dashboard = () => {
  const [data, setData] = useState({});
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    // Connect to backend serial reader (via WebSocket or IPC)
    const ws = new WebSocket('ws://localhost:8080');
    
    ws.onopen = () => {
      console.log('Connected to REM');
      setConnected(true);
    };

    ws.onmessage = (event) => {
      const remData = JSON.parse(event.data);
      setData(remData);
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      setConnected(false);
    };

    return () => ws.close();
  }, []);

  // Warning logic
  const isCoolantHot = data.CTS > 230;
  const isBatteryLow = data.Batt < 12.5 && data.RPM === 0;
  const isBatteryHigh = data.Batt > 15;

  return (
    <div className="dashboard" style={{ 
      width: '480px', 
      height: '800px', 
      backgroundColor: '#1a1a1a',
      color: '#fff',
      fontFamily: 'Arial, sans-serif'
    }}>
      
      {/* Header */}
      <StatusBar 
        connected={connected}
        warnings={[
          isCoolantHot && 'OVERHEAT',
          isBatteryLow && 'BATT LOW',
          isBatteryHigh && 'VOLTAGE HIGH'
        ].filter(Boolean)}
      />

      {/* Main Gauge - RPM */}
      <div style={{ padding: '20px', textAlign: 'center' }}>
        <GaugeCircular
          value={data.RPM || 0}
          max={6000}
          label="RPM"
          size={280}
          redline={5000}
        />
      </div>

      {/* Secondary Readouts */}
      <div style={{ padding: '10px 20px' }}>
        <DataRow label="Coolant" value={`${data.CTS || 0}°F`} warn={isCoolantHot} />
        <DataRow label="Intake Temp" value={`${data.IAT || 0}°F`} />
        <DataRow label="MAP" value={`${data.MAP || 0}"`} />
        <DataRow label="Vacuum" value={`${data.VAC || 0}"`} />
        <DataRow label="TPS" value={`${data.TPS || 0}%`} />
        <DataRow label="Battery" value={`${data.Batt || 0}V`} warn={isBatteryLow || isBatteryHigh} />
        <DataRow label="O2" value={data.exhaust || '-'} />
        <DataRow label="Loop" value={data.Loop || '-'} />
      </div>

      {/* Bottom Nav */}
      <div style={{ 
        position: 'absolute', 
        bottom: 0, 
        width: '100%',
        display: 'flex',
        justifyContent: 'space-around',
        padding: '10px',
        backgroundColor: '#0a0a0a'
      }}>
        <button>Codes</button>
        <button>Datalog</button>
        <button>GPS</button>
      </div>
    </div>
  );
};

const DataRow = ({ label, value, warn }) => (
  <div style={{ 
    display: 'flex', 
    justifyContent: 'space-between',
    padding: '8px 0',
    borderBottom: '1px solid #333',
    color: warn ? '#ff4444' : '#fff'
  }}>
    <span>{label}</span>
    <span style={{ fontWeight: 'bold' }}>{value}</span>
  </div>
);

export default Dashboard;
```

### SQLite Datalogging

```python
import sqlite3
from datetime import datetime

class DataLogger:
    def __init__(self, db_path='/home/pi/jeep_logs'):
        self.db_path = db_path
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.conn = None
        self.init_database()
    
    def init_database(self):
        """Create database and table schema"""
        db_file = f"{self.db_path}/{self.session_id}.db"
        self.conn = sqlite3.connect(db_file)
        cursor = self.conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS datalog (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp INTEGER,
                datetime TEXT,
                MAP REAL,
                VAC REAL,
                CTS REAL,
                IAT REAL,
                RPM REAL,
                Batt REAL,
                o2 REAL,
                exhaust TEXT,
                o2_Heater REAL,
                Loop TEXT,
                EGR TEXT,
                TPS REAL,
                TPS_mode TEXT,
                IGN REAL,
                Knock REAL,
                INJ_ms REAL,
                INJ_DC REAL,
                Sync TEXT,
                STFT REAL,
                LTFT REAL,
                AC_SW TEXT,
                AC_REQ TEXT,
                GPH REAL,
                AFR REAL,
                gps_lat REAL,
                gps_lon REAL,
                gps_speed REAL
            )
        ''')
        
        self.conn.commit()
        print(f"Created session: {self.session_id}")
    
    def log_datapoint(self, data, gps_data=None):
        """Insert single datapoint into database"""
        cursor = self.conn.cursor()
        
        cursor.execute('''
            INSERT INTO datalog (
                timestamp, datetime, MAP, VAC, CTS, IAT, RPM, Batt, o2,
                exhaust, o2_Heater, Loop, EGR, TPS, TPS_mode, IGN, Knock,
                INJ_ms, INJ_DC, Sync, STFT, LTFT, AC_SW, AC_REQ, GPH, AFR,
                gps_lat, gps_lon, gps_speed
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data.get('timestamp'),
            datetime.now().isoformat(),
            data.get('MAP'),
            data.get('VAC'),
            data.get('CTS'),
            data.get('IAT'),
            data.get('RPM'),
            data.get('Batt'),
            data.get('o2'),
            data.get('exhaust'),
            data.get('o2_Heater'),
            data.get('Loop'),
            data.get('EGR'),
            data.get('TPS'),
            data.get('TPS_mode'),
            data.get('IGN'),
            data.get('Knock'),
            data.get('INJ_ms'),
            data.get('INJ_DC'),
            data.get('Sync'),
            data.get('STFT'),
            data.get('LTFT'),
            data.get('AC_SW'),
            data.get('AC_REQ'),
            data.get('GPH'),
            data.get('AFR'),
            gps_data.get('lat') if gps_data else None,
            gps_data.get('lon') if gps_data else None,
            gps_data.get('speed') if gps_data else None
        ))
        
        self.conn.commit()
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            print(f"Session {self.session_id} saved")

# Usage
logger = DataLogger()

while True:
    rem_data = read_serial_data()  # Your serial reader
    gps_data = read_gps_data()     # Your GPS reader
    
    logger.log_datapoint(rem_data, gps_data)
```

---

## Power Management

### Raspberry Pi Power Requirements

- **Pi 4 2GB:** 3A @ 5V (15W) recommended minimum
- **Peak draw:** Can spike to 5A during boot or USB device enumeration
- **Display:** ~0.5-1A additional
- **Total:** 4A @ 5V (20W) for safety margin

### 12V to 5V Conversion Options

**Option 1: Automotive USB Charger (Quick & Easy)**
- AUKEY/Anker dual-port car charger with USB-C PD
- **Pros:** Plug-and-play, cheap ($15-25)
- **Cons:** Cigarette lighter socket required, less clean install

**Option 2: DC-DC Buck Converter (Professional)**
- Pololu D36V28F5 (5V 5A buck regulator)
- Wired directly to vehicle ignition-switched 12V source
- **Pros:** Clean install, reliable, ignition-controlled power
- **Cons:** Requires soldering, proper gauge wire

**Option 3: Official Jeep Headunit Power (If Replacing Stereo)**
- Tap into factory radio harness 12V ACC and GND
- Inline buck converter before Pi
- **Pros:** OEM integration, proper fusing already present
- **Cons:** Limited space behind dash

### Recommended: Ignition-Switched Power with Clean Shutdown

**Circuit Design:**
```
Battery 12V
    │
    ├─[Fuse 5A]─┬──> Buck Converter (5V 5A) ──> Pi USB-C
    │           │
    │           └──> GPIO Pin (3.3V signal) ──┐
    │                                         │
    └─[Ignition Switch]───────────────────────┘
```

**Shutdown Logic:**
1. Ignition OFF detected on GPIO pin
2. Pi begins graceful shutdown (saves logs, closes files)
3. After 30 seconds, buck converter cuts power completely

**Python Shutdown Script:**
```python
import RPi.GPIO as GPIO
import subprocess
import time

IGNITION_PIN = 17  # GPIO pin connected to ignition signal

GPIO.setmode(GPIO.BCM)
GPIO.setup(IGNITION_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

def check_ignition():
    while True:
        if GPIO.input(IGNITION_PIN) == GPIO.LOW:
            print("Ignition OFF - shutting down in 10 seconds...")
            time.sleep(10)
            
            # Verify still off (debounce)
            if GPIO.input(IGNITION_PIN) == GPIO.LOW:
                subprocess.call(['sudo', 'shutdown', '-h', 'now'])
        
        time.sleep(1)

if __name__ == '__main__':
    check_ignition()
```

---

## Hardware Shopping List

### Core Components

| Item | Spec | Estimated Cost | Notes |
|------|------|---------------|-------|
| Raspberry Pi 4 | 2GB RAM | $35-45 | 4GB if running additional services |
| 4.3" Touchscreen | 800x480 IPS, DSI | $40-60 | Waveshare recommended |
| MicroSD Card | 32GB Class 10 | $10 | Or USB boot drive for reliability |
| USB GPS Module | U-blox VK-172 | $15-25 | Optional but recommended |
| DC-DC Buck Converter | 5V 5A output | $15-20 | Pololu D36V28F5 or equiv. |
| USB Cable | USB-A to Micro-USB, 3ft | $5 | REM to Pi connection |
| Case for Pi | Ventilated enclosure | $10-15 | Heat dissipation important |

**Subtotal:** ~$130-200

### Wiring & Mounting

| Item | Purpose | Est. Cost |
|------|---------|-----------|
| 16AWG wire | Power distribution | $5 |
| Inline fuse holder | 5A fuse for Pi circuit | $3 |
| Heat shrink tubing | Wire connections | $5 |
| Velcro strips | Secure Pi case behind dash | $5 |

**Subtotal:** ~$20

**Grand Total:** $150-220

---

## Next Steps / Implementation Plan

### Phase 1: Proof of Concept (Week 1)
- [ ] Order Raspberry Pi 4 and 4.3" touchscreen
- [ ] Connect REM to Pi via USB on bench (not in vehicle)
- [ ] Verify serial data reception using Python script
- [ ] Parse "Normal" mode output into structured data
- [ ] Display raw data on terminal to confirm values match REM OLED

### Phase 2: Basic Dashboard (Week 2-3)
- [ ] Set up touchscreen on Pi (DSI connection, configure display rotation)
- [ ] Install dashboard framework (Electron/React or Kivy)
- [ ] Build basic UI with 3-4 primary gauges
- [ ] Test UI responsiveness and update rate
- [ ] Implement night mode color scheme

### Phase 3: Vehicle Integration (Week 4)
- [ ] Finalize power solution (buck converter, wiring)
- [ ] Install dashboard in vehicle using 3D printed mount
- [ ] Route USB cable from REM to Pi cleanly
- [ ] Test in-vehicle operation (startup, shutdown, vibration)
- [ ] Verify all gauges display correct real-time data

### Phase 4: Datalogging (Week 5)
- [ ] Implement SQLite logging backend
- [ ] Add "Start/Stop Log" button in UI
- [ ] Test log file creation and storage management
- [ ] Export logs to CSV for analysis in Excel
- [ ] Configure automatic log rotation/archiving

### Phase 5: GPS & WiFi (Week 6-7)
- [ ] Connect USB GPS module
- [ ] Integrate GPS data with REM logs
- [ ] Test GPS accuracy and update rate
- [ ] Implement WiFi upload to cloud storage (Dropbox/Google Drive)
- [ ] Build web-based log viewer for remote access

### Phase 6: Advanced Features (Ongoing)
- [ ] Diagnostic code display with descriptions
- [ ] Multi-page layouts (swipe between screens)
- [ ] Performance tracking (0-60, quarter-mile)
- [ ] Maintenance reminders (oil change, service intervals)
- [ ] Custom gauge configurations (user-selectable)

---

## Resources & Documentation

### Official REM Site
- **Main Site:** https://nickintimedesign.com
- **Datastream Docs:** https://nickintimedesign.com/reverse-engineering/
- **Datalogging Guide:** https://nickintimedesign.com/rem-datalogging/
- **Gauge Definitions:** https://nickintimedesign.com/rem-gauge-readouts/
- **Downloads:** https://nickintimedesign.com/downloads/

### Raspberry Pi Resources
- **Official Docs:** https://www.raspberrypi.org/documentation/
- **GPIO Pinout:** https://pinout.xyz
- **Touchscreen Setup:** https://www.waveshare.com/wiki/4.3inch_DSI_LCD

### Development Tools
- **Python Serial:** https://pyserial.readthedocs.io/
- **Electron:** https://www.electronjs.org/
- **React:** https://reactjs.org/
- **Kivy (Python UI):** https://kivy.org/

### Jeep/Renix Communities
- **Cruiser54's Renix Tips:** http://cruiser54.com/
- **Jeep Forum XJ Section:** https://www.jeepforum.com/forum/f11/
- **NICOclub XJ Tech:** https://www.nicoclub.com/

---

## FAQ

**Q: Can I use this with a 2.5L 4-cylinder Jeep?**
A: Yes! The REM supports both 4.0L and 2.5L Renix engines. Some gauge values will differ (injector pulse width, O2 voltage scale), but all core functionality works.

**Q: Will this work on 1991+ Jeeps?**
A: No. The REM only supports Renix systems (1987-1990 Jeep Cherokee/Comanche). Later Jeeps use OBD-I or OBD-II which have different protocols.

**Q: Do I need to modify my REM?**
A: No modifications required! The REM already has USB serial output built-in. Just enable it in the settings menu.

**Q: Can I run this without the REM?**
A: No. The REM handles all the specialized Bendix communication protocols. Building that from scratch would require reverse-engineering all the ECU/TCU/ABS communication yourself.

**Q: What if my REM loses power while logging?**
A: The current serial monitor approach loses data if the REM disconnects. However, with your Pi-based solution, you can implement auto-reconnection and continuous logging that survives brief REM power interruptions.

**Q: Can I display this on my phone instead?**
A: Potentially! You could build a mobile app that connects to the Pi via WiFi hotspot. But the touchscreen next to the gauges is more practical for in-vehicle use.

**Q: How much data storage do I need?**
A: At 4 frames/second with ~25 parameters per frame, a 1-hour drive = ~14,400 datapoints = ~2-5MB depending on format. A 32GB SD card can store thousands of hours of logs.

**Q: Will the Pi overheat in summer heat?**
A: Pi 4 can get hot. Use a case with ventilation/heatsinks and mount in a location with airflow (not sealed behind the dash). The Pi will throttle performance if it hits 85°C but won't damage itself.

**Q: Can I power the Pi from USB on the REM?**
A: No. The REM's USB port is data-only and cannot provide enough current to power a Pi. You need a separate 5V power source.

---

## Project Status & Future Enhancements

### Completed (Per This Documentation)
- ✅ Hardware architecture defined
- ✅ REM datastream protocols documented
- ✅ Serial communication strategy outlined
- ✅ Power management solution designed
- ✅ Basic dashboard UI concepts
- ✅ Datalogging implementation plan

### In Progress
- 🔄 3D printed mounting bracket (user has designed)
- 🔄 Hardware procurement

### Future Expansion Ideas
- 📋 **Stereo Integration:** Add Bluetooth audio, backup camera input
- 📋 **OBD-II Adapter:** Add OBD-II reader for newer vehicles (dual-protocol)
- 📋 **CAN Bus Expansion:** Read additional vehicle systems via CAN
- 📋 **Remote Diagnostics:** Send alerts/codes via SMS or push notifications
- 📋 **Cloud Analytics:** Upload all logs to central server for fleet management
- 📋 **AI-Powered Diagnostics:** Machine learning to predict failures before they occur

---

## Conclusion

This digital dashboard project builds on the excellent foundation of Nick's Renix Engine Monitor while adding modern conveniences:

1. **Better Display:** 4.3" touchscreen vs. small OLED
2. **Enhanced Logging:** Local storage + WiFi upload vs. incomplete SD card implementation
3. **GPS Integration:** Location-tagged data for troubleshooting
4. **Expandability:** Open platform for future features (stereo, backup cam, etc.)

The REM has already solved the hardest problem: communicating with obscure 1990s Bendix protocols. Your role is to take that clean data stream and present it beautifully on a modern interface.

**Key Success Factors:**
- Use the REM's existing USB serial output (don't reinvent the wheel)
- Start simple (basic gauges) before adding advanced features
- Test thoroughly in the vehicle (vibration, temperature, power cycling)
- Build incrementally (MVP → logging → GPS → advanced)

This is a highly achievable project with massive practical value for your XJ. The documentation is thorough, the hardware is affordable, and the software stack is flexible. Time to turn your Jeep's dash into a modern command center!

---

**Document Version:** 2.0  
**Last Updated:** December 26, 2024  
**Author:** Claude (Documentation compiled from nickintimedesign.com)  
**Project Owner:** James Martin
