# Renix Engine Monitor Digital Dashboard - Quick Start Guide

**Hardware:** Raspberry Pi 4 + 4.3" Touchscreen (Portrait Mode)  
**Connection:** Direct USB from REM to Pi  
**Power:** 12V vehicle power with buck converter  

---

## 🚀 30-Minute Proof of Concept

**Goal:** Get REM data displaying on your computer screen to verify everything works before vehicle installation.

### Materials Needed
- Renix Engine Monitor (installed in your Jeep)
- Computer with Python installed
- USB cable (USB-A to Micro-USB for REM connection)

### Step 1: Configure REM for Serial Output (5 min)

1. Turn on your Jeep (ignition to ON)
2. On REM display, navigate: **Options → More → Settings → Advanced Menu → USB Output**
3. Select: **Normal** (easier to read than Raw for testing)
4. Power cycle REM (turn ignition off/on) to apply setting

### Step 2: Connect and Test (10 min)

**On Windows:**
```bash
# Install Python serial library
pip install pyserial

# Find COM port (Device Manager → Ports)
# Usually COM3, COM4, etc.
```

**On Mac/Linux:**
```bash
# Install serial library
pip3 install pyserial

# Find device
ls /dev/tty.* | grep -i usb
# Usually /dev/ttyACM0 or /dev/tty.usbmodem*
```

### Step 3: Run Test Script (5 min)

Create `test_rem.py`:

```python
import serial
import time

# CHANGE THIS to your port
PORT = '/dev/ttyACM0'  # Linux/Mac
# PORT = 'COM4'        # Windows

ser = serial.Serial(PORT, 115200, timeout=1)
print("Connected to REM! Reading data...\n")

try:
    while True:
        if ser.in_waiting:
            line = ser.readline().decode('utf-8').strip()
            print(line)
            time.sleep(0.1)
except KeyboardInterrupt:
    print("\nStopped")
    ser.close()
```

Run it:
```bash
python3 test_rem.py
```

**Expected Output:**
```
12450 14.5 15.4 195 98 750 13.8 2.5 RICH 13.2 CLSD OFF 18 PART 15 0 4.2 3.1 + 128 142 OFF NO 0.8 14.5
12700 14.3 15.6 195 98 780 13.8 2.7 LEAN 13.2 CLSD OFF 19 PART 15 0 4.3 3.2 + 129 142 OFF NO 0.9 15.2
```

✅ **Success!** You're now receiving real-time data from your Jeep's ECU.

### Step 4: Understanding the Data (10 min)

The output is space-delimited values in this order:
```
timestamp MAP VAC CTS IAT RPM Batt o2 exhaust o2_Heater Loop EGR TPS TPS_mode IGN Knock INJ_ms INJ_DC Sync STFT LTFT AC_SW AC_REQ GPH AFR
```

**Key Values:**
- **Position 5 (RPM):** Engine speed
- **Position 4 (CTS):** Coolant temperature (°F)
- **Position 3 (MAP):** Manifold pressure (inHg)
- **Position 12 (TPS):** Throttle position (%)

Try revving the engine and watch RPM value change!

---

## 📦 Hardware Shopping List

### Essential Components

| Item | Specs | Where to Buy | Price |
|------|-------|--------------|-------|
| **Raspberry Pi 4** | 2GB RAM minimum | Adafruit, Amazon | $45 |
| **4.3" DSI Touchscreen** | 800x480 IPS, capacitive | Waveshare (SKU: 13872) | $55 |
| **MicroSD Card** | 32GB, Class 10, A1-rated | Amazon, Best Buy | $10 |
| **DC-DC Converter** | 12V→5V, 5A output | Pololu D36V28F5 | $18 |
| **USB Cable (REM→Pi)** | USB-A to Micro-USB, 3ft | Monoprice, Amazon | $5 |
| **Power Cable (12V)** | 16AWG, red/black pair, 6ft | Auto parts store | $8 |
| **Inline Fuse Holder** | Blade-type, 5A fuse | Auto parts store | $3 |
| **Pi Case** | Ventilated or open frame | Amazon | $12 |

**Subtotal:** ~$156

### Optional but Recommended

| Item | Purpose | Price |
|------|---------|-------|
| USB GPS Module (U-blox VK-172) | GPS tracking, accurate timestamps | $20 |
| USB Flash Drive (32GB) | More reliable than SD for logging | $12 |
| Heatsinks for Pi | Better heat management | $5 |
| USB Hub (powered) | If adding multiple USB devices | $15 |

**Grand Total with Optionals:** ~$208

---

## 🔧 Hardware Assembly Guide

### Step 1: Flash Raspberry Pi OS (30 min)

1. **Download Raspberry Pi Imager:** https://www.raspberrypi.com/software/
2. **Insert SD card** into your computer
3. **Select OS:** Raspberry Pi OS (64-bit) with Desktop
4. **Configure:** 
   - Set hostname: `jeep-dashboard`
   - Enable SSH (optional but useful)
   - Set WiFi credentials
5. **Write** to SD card (takes ~10 minutes)

### Step 2: Initial Pi Setup (15 min)

1. Insert SD card into Pi
2. Connect display via DSI ribbon cable
3. Connect keyboard + mouse (USB)
4. Power on (using USB-C power adapter for now)
5. Complete setup wizard (language, timezone, password)
6. Update system:
```bash
sudo apt update && sudo apt upgrade -y
```

### Step 3: Configure Display Rotation (5 min)

For **portrait mode** (display rotated 90° left):

```bash
sudo nano /boot/config.txt
```

Add this line:
```
display_rotate=3
```

Save (Ctrl+X, Y, Enter) and reboot:
```bash
sudo reboot
```

Display should now be in portrait orientation.

### Step 4: Install Python Dependencies (10 min)

```bash
# Install Python packages
pip3 install pyserial

# For GUI development (choose ONE framework):
# Option A: Kivy (Python-native)
pip3 install kivy

# Option B: Electron (if using web tech)
sudo apt install nodejs npm
npm install -g electron

# For datalogging
pip3 install pynmea2  # GPS parsing (if using GPS module)
```

### Step 5: Test REM Connection on Pi (10 min)

1. Connect REM to Pi via USB cable
2. Power on Jeep (REM should boot)
3. Run the test script from earlier:
```bash
python3 test_rem.py
```

✅ Verify data is flowing correctly.

---

## 💻 Dashboard Software Development

### Architecture Overview

```
┌─────────────────────────────────────┐
│     Backend (Python)                │
│  - Serial reader (reads REM USB)    │
│  - Data parser                      │
│  - SQLite logger                    │
│  - GPS reader (optional)            │
│  - WebSocket server (for UI)        │
└─────────────┬───────────────────────┘
              │ WebSocket or IPC
┌─────────────▼───────────────────────┐
│     Frontend (UI)                   │
│  - Electron + React (web-based)     │
│  - OR Kivy (Python-native)          │
│  - Displays gauges, logs, GPS       │
│  - Touchscreen interaction          │
└─────────────────────────────────────┘
```

### Starter Code: Complete Serial Reader with Logging

Save as `rem_reader.py`:

```python
#!/usr/bin/env python3
"""
REM Serial Reader with SQLite Logging
Reads REM data and stores to database
"""

import serial
import sqlite3
import time
from datetime import datetime

# Configuration
SERIAL_PORT = '/dev/ttyACM0'
BAUD_RATE = 115200
DB_PATH = '/home/pi/jeep_logs'

# Data field names (REM Normal mode output)
FIELDS = [
    'timestamp', 'MAP', 'VAC', 'CTS', 'IAT', 'RPM', 'Batt', 'o2',
    'exhaust', 'o2_Heater', 'Loop', 'EGR', 'TPS', 'TPS_mode',
    'IGN', 'Knock', 'INJ_ms', 'INJ_DC', 'Sync', 'STFT', 'LTFT',
    'AC_SW', 'AC_REQ', 'GPH', 'AFR'
]

class REMLogger:
    def __init__(self):
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.db_conn = self.create_database()
        self.serial_conn = None
        
    def create_database(self):
        """Create SQLite database for this session"""
        db_file = f"{DB_PATH}/{self.session_id}.db"
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        # Create table with all REM fields
        cursor.execute(f'''
            CREATE TABLE datalog (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                datetime TEXT,
                {", ".join([f"{field} REAL" if field != 'timestamp' else f"{field} INTEGER" 
                           for field in FIELDS if field not in ['exhaust', 'Loop', 'EGR', 'TPS_mode', 'AC_SW', 'AC_REQ', 'Sync']])},
                exhaust TEXT,
                Loop TEXT,
                EGR TEXT,
                TPS_mode TEXT,
                AC_SW TEXT,
                AC_REQ TEXT,
                Sync TEXT
            )
        ''')
        
        conn.commit()
        print(f"✓ Created session: {self.session_id}")
        return conn
    
    def connect_serial(self):
        """Connect to REM serial port"""
        try:
            self.serial_conn = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
            print(f"✓ Connected to REM on {SERIAL_PORT}")
            return True
        except Exception as e:
            print(f"✗ Serial connection failed: {e}")
            return False
    
    def parse_line(self, line):
        """Parse REM data line into dictionary"""
        values = line.strip().split()
        if len(values) != len(FIELDS):
            return None
        
        data = {}
        for i, field in enumerate(FIELDS):
            if field in ['exhaust', 'Loop', 'EGR', 'TPS_mode', 'AC_SW', 'AC_REQ', 'Sync']:
                data[field] = values[i]  # String fields
            else:
                try:
                    data[field] = float(values[i])
                except:
                    data[field] = 0
        
        return data
    
    def log_data(self, data):
        """Insert datapoint into database"""
        cursor = self.db_conn.cursor()
        
        cursor.execute(f'''
            INSERT INTO datalog (
                datetime, {", ".join(FIELDS)}
            ) VALUES (?, {", ".join(["?" for _ in FIELDS])})
        ''', (
            datetime.now().isoformat(),
            *[data[field] for field in FIELDS]
        ))
        
        self.db_conn.commit()
    
    def run(self):
        """Main reading loop"""
        if not self.connect_serial():
            return
        
        print("Reading data... (Ctrl+C to stop)")
        print("-" * 80)
        
        try:
            while True:
                if self.serial_conn.in_waiting:
                    line = self.serial_conn.readline().decode('utf-8', errors='ignore')
                    data = self.parse_line(line)
                    
                    if data:
                        # Log to database
                        self.log_data(data)
                        
                        # Print summary
                        print(f"RPM: {data['RPM']:5.0f} | "
                              f"Temp: {data['CTS']:3.0f}°F | "
                              f"MAP: {data['MAP']:4.1f}\" | "
                              f"TPS: {data['TPS']:3.0f}% | "
                              f"Logged ✓")
                
                time.sleep(0.01)
        
        except KeyboardInterrupt:
            print("\n\nStopping...")
        finally:
            self.serial_conn.close()
            self.db_conn.close()
            print(f"✓ Session saved: {self.session_id}.db")

if __name__ == '__main__':
    logger = REMLogger()
    logger.run()
```

**Run it:**
```bash
mkdir -p /home/pi/jeep_logs
python3 rem_reader.py
```

Your data is now being logged to SQLite! Files saved in `/home/pi/jeep_logs/`.

---

## 🎨 Building the Dashboard UI

### Option A: Simple Python GUI (Kivy)

Create `dashboard_simple.py`:

```python
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.clock import Clock
import serial

class DashboardLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        
        # Create labels for key gauges
        self.rpm_label = Label(text='RPM: ---', font_size='48sp', size_hint=(1, 0.3))
        self.temp_label = Label(text='Temp: ---°F', font_size='32sp')
        self.map_label = Label(text='MAP: ---"', font_size='32sp')
        self.tps_label = Label(text='TPS: ---%', font_size='32sp')
        
        self.add_widget(self.rpm_label)
        self.add_widget(self.temp_label)
        self.add_widget(self.map_label)
        self.add_widget(self.tps_label)
        
        # Connect to REM
        try:
            self.serial = serial.Serial('/dev/ttyACM0', 115200, timeout=0.1)
            Clock.schedule_interval(self.update_gauges, 0.1)
        except Exception as e:
            self.rpm_label.text = f"Error: {e}"
    
    def update_gauges(self, dt):
        """Read serial and update display"""
        if self.serial.in_waiting:
            line = self.serial.readline().decode('utf-8').strip()
            values = line.split()
            
            if len(values) >= 25:
                rpm = float(values[5])
                cts = float(values[3])
                map_val = float(values[1])
                tps = float(values[12])
                
                self.rpm_label.text = f'RPM: {rpm:.0f}'
                self.temp_label.text = f'Temp: {cts:.0f}°F'
                self.map_label.text = f'MAP: {map_val:.1f}"'
                self.tps_label.text = f'TPS: {tps:.0f}%'
                
                # Color-code warnings
                if cts > 230:
                    self.temp_label.color = (1, 0, 0, 1)  # Red
                else:
                    self.temp_label.color = (1, 1, 1, 1)  # White

class DashboardApp(App):
    def build(self):
        return DashboardLayout()

if __name__ == '__main__':
    DashboardApp().run()
```

**Run it:**
```bash
python3 dashboard_simple.py
```

### Option B: Web-Based Dashboard (Electron + React)

**Benefits:**
- Modern web technologies (HTML/CSS/JavaScript)
- Easy to style with CSS frameworks
- Responsive design
- Better graphics libraries (Chart.js, D3.js)

**Structure:**
```
dashboard-app/
├── main.js           # Electron main process
├── preload.js        # IPC bridge
├── renderer.js       # Serial reader (Node.js)
└── public/
    ├── index.html    # UI layout
    ├── style.css     # Styling
    └── app.js        # React components
```

**Quick Start:**
```bash
npm init -y
npm install electron serialport ws
```

*(Full Electron tutorial available in detailed documentation)*

---

## 🔌 Vehicle Power Integration

### DC-DC Buck Converter Wiring

**Components:**
- Pololu D36V28F5 (12V input, 5V 5A output)
- 16AWG wire (red/black)
- 5A blade fuse + inline holder
- USB-C breakout cable (for Pi power)

**Wiring Diagram:**
```
Battery 12V (Fuse Panel)
    │
    ├─[5A Fuse]───┬──> Buck Converter (+IN)
    │             │
    │             └──> Buck Converter (-IN)
    │
    └─[Ground]────────> Buck Converter GND


Buck Converter Output:
    5V (+OUT) ──> USB-C Red Wire (VBUS)
    GND       ──> USB-C Black Wire (GND)
```

**Installation Steps:**

1. **Find ignition-switched 12V source:**
   - Option A: Accessory circuit from fuse panel
   - Option B: Radio harness ACC wire (yellow, 12V when ignition ON)

2. **Tap into power:**
   - Use wire tap connectors OR solder + heat shrink
   - Install inline fuse holder close to power source

3. **Mount buck converter:**
   - Behind dashboard, secured with zip ties
   - Ensure ventilation (converter generates heat)

4. **Connect to Pi:**
   - USB-C breakout: Red→5V, Black→GND
   - Pi 4 requires USB-C connector for power

5. **Test before final install:**
   - Ignition ON: Pi should boot
   - Ignition OFF: Pi should shut down (after implementing shutdown script)

### Auto-Shutdown & Power Latch

**Purpose:** Gracefully shut down Pi when ignition turns off, then cut 12V to the
buck converter so there is zero parasitic draw.

This is now built into XJDash itself via `src/core/ignition_monitor.py` and
`src/core/power_latch.py`. No separate script is needed — the app handles
ignition detection, cleanup, and power-off automatically.

**Ignition sense voltage divider (GPIO17):**
```
Switched 12V ──[10kΩ]──┬── GPIO17 (pin 11)
                        │
                     [4.7kΩ] + [100nF cap]
                        │
                       GND
```
Produces ~3.1V at the GPIO pin (safe for 3.3V logic).

**Power latch relay (GPIO27):**
A standard 12V automotive relay holds the buck converter on after the Pi boots.
When shutdown completes, GPIO27 releases and the relay drops — zero draw.

See `Documentation/Wiring_Schematic.md` for the full circuit diagram,
pin assignments, and parts list.

---

## 📊 Data Analysis

### Exporting Logs for Excel

**Python script to convert SQLite → CSV:**

```python
import sqlite3
import csv

session = '20241226_143022'  # Your session ID
db_file = f'/home/pi/jeep_logs/{session}.db'
csv_file = f'/home/pi/jeep_logs/{session}.csv'

conn = sqlite3.connect(db_file)
cursor = conn.cursor()

# Export all data
cursor.execute('SELECT * FROM datalog')
rows = cursor.fetchall()

# Get column names
column_names = [description[0] for description in cursor.description]

# Write CSV
with open(csv_file, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(column_names)
    writer.writerows(rows)

print(f"Exported {len(rows)} rows to {csv_file}")
```

**Import to Excel:**
1. File → Open → Select CSV
2. Text Import Wizard → Delimited → Comma
3. Create graphs using Insert → Chart

### WiFi Upload to Cloud

**Using Dropbox API:**

```bash
pip3 install dropbox
```

```python
import dropbox

def upload_log(local_file, dropbox_path):
    token = 'YOUR_DROPBOX_ACCESS_TOKEN'
    dbx = dropbox.Dropbox(token)
    
    with open(local_file, 'rb') as f:
        dbx.files_upload(f.read(), dropbox_path, mode=dropbox.files.WriteMode.overwrite)
    
    print(f"Uploaded {local_file} to Dropbox")

# After each session
upload_log(f'/home/pi/jeep_logs/{session_id}.db', f'/Jeep_Logs/{session_id}.db')
```

---

## 🛠️ Troubleshooting

### Issue: Pi won't boot
- **Check:** SD card properly inserted?
- **Check:** Power supply adequate (5V 3A minimum)?
- **Try:** Re-flash SD card with Raspberry Pi Imager

### Issue: Display not working
- **Check:** DSI ribbon cable fully seated on both ends
- **Check:** Display rotation configured in `/boot/config.txt`
- **Try:** HDMI output first to verify Pi is booting

### Issue: REM not detected
- **Check:** USB cable good? (try different cable)
- **Check:** REM powered on? (Jeep ignition ON)
- **Check:** Correct serial port? (`ls /dev/ttyACM*`)
- **Try:** Different USB port on Pi

### Issue: No serial data
- **Check:** REM USB Output enabled? (Options → Settings)
- **Check:** Correct baud rate? (115200)
- **Check:** Using correct serial device?
- **Try:** `sudo dmesg | grep tty` to see device detection logs

### Issue: Dashboard crashes
- **Check:** Sufficient power? (voltage sag under load?)
- **Check:** Overheating? (add heatsinks/fan)
- **Check:** SD card not corrupted? (try fresh card)

### Issue: Data logging stops
- **Check:** Disk space full? (`df -h`)
- **Check:** File permissions? (`ls -l /home/pi/jeep_logs/`)
- **Try:** Clear old logs, restart logging script

---

## 📋 Final Checklist

Before installing in vehicle:

- [ ] Pi boots reliably from power-on
- [ ] Touchscreen displays correctly in portrait mode
- [ ] Serial data from REM reads correctly
- [ ] Dashboard UI shows live gauges
- [ ] Datalogging creates files successfully
- [ ] Auto-shutdown script tested (GPIO trigger works)
- [ ] Power circuit protected with proper fuse
- [ ] All wiring neat and secure (no loose connections)
- [ ] Pi case provides adequate cooling
- [ ] Mounting bracket fits properly

After installation:

- [ ] Test during short drive (5-10 minutes)
- [ ] Verify no electrical interference with REM or Jeep systems
- [ ] Check power-up/shutdown cycle 3+ times
- [ ] Review first datalog file for completeness
- [ ] Verify touchscreen responsive while driving (vibration test)

---

## 🎯 Next Steps After MVP

Once basic dashboard is working:

1. **GPS Integration** - Add location tracking to logs
2. **WiFi Sync** - Auto-upload logs when parked at home
3. **Advanced Gauges** - Add boost gauge, wideband O2, custom inputs
4. **Multi-Screen UI** - Swipe between gauge screens
5. **Diagnostic Codes** - Display fault code descriptions
6. **Performance Tracking** - 0-60 timer, quarter-mile runs
7. **Maintenance Reminders** - Oil change countdowns

---

## 📞 Support Resources

- **REM Support:** https://nickintimedesign.com/support/
- **Raspberry Pi Forums:** https://forums.raspberrypi.com/
- **Jeep XJ Tech:** https://www.jeepforum.com/
- **Python Help:** https://stackoverflow.com/

**Have questions?** Consult the full knowledge base document for detailed technical info.

---

**Document Version:** 2.0  
**Last Updated:** December 26, 2024  
**Estimated Time to Working Dashboard:** 2-3 weekends
