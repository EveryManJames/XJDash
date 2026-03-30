# XJDash Wiring Schematic & Pin Assignment

**Vehicle:** 1990 Jeep Cherokee XJ
**Computer:** Raspberry Pi 4 (4GB)
**Display:** Freenove 4.3" DSI Touchscreen (800x480, portrait)
**Last Updated:** March 30, 2026

---

## Pin Assignment Summary

### Raspberry Pi 4 GPIO Header (40-pin)

```
                    +-----+-----+
              3.3V  | 1   | 2   |  5V
  I2C SDA [GPIO2]  | 3   | 4   |  5V
  I2C SCL [GPIO3]  | 5   | 6   |  GND
              ----  | 7   | 8   |  ----
               GND  | 9   | 10  |  ----
  IGN Sense [GPIO17]| 11  | 12  |  ----
  PWR Latch [GPIO27]| 13  | 14  |  GND
              ----  | 15  | 16  |  ----
              3.3V  | 17  | 18  |  ----
              ----  | 19  | 20  |  GND
              ----  | 21  | 22  |  ----
              ----  | 23  | 24  |  ----
               GND  | 25  | 26  |  ----
              ----  | 27  | 28  |  ----
              ----  | 29  | 30  |  GND
              ----  | 31  | 32  |  ----
              ----  | 33  | 34  |  GND
              ----  | 35  | 36  |  ----
              ----  | 37  | 38  |  ----
               GND  | 39  | 40  |  ----
                    +-----+-----+
```

| BCM Pin | Phys Pin | Direction | Function              | Connected To                       |
|---------|----------|-----------|-----------------------|------------------------------------|
| GPIO2   | 3        | I2C SDA   | BNO055 data           | BNO055 SDA pin                     |
| GPIO3   | 5        | I2C SCL   | BNO055 clock          | BNO055 SCL pin                     |
| GPIO17  | 11       | INPUT     | Ignition sense         | Voltage divider from switched 12V  |
| GPIO27  | 13       | OUTPUT    | Power latch keep-alive | 1kΩ → 2N2222 base                 |

**All other GPIO pins are unused and available for future expansion.**

### Raspberry Pi 4 Ports

| Port       | Device                          | Linux Device     | Baud/Protocol |
|------------|---------------------------------|------------------|---------------|
| USB-A #1   | Renix Engine Monitor (REM v4+)  | `/dev/ttyACM0`   | 115200 8N1    |
| USB-A #2   | USB-to-RS485 Adapter            | `/dev/ttyUSB0`   | 9600 8N1      |
| USB-A #3   | (available)                     | —                | —             |
| USB-A #4   | (available)                     | —                | —             |
| DSI        | Freenove 4.3" Touchscreen       | —                | —             |
| USB-C      | 5V Power from buck converter    | —                | —             |

---

## Complete System Wiring Diagram

```
═══════════════════════════════════════════════════════════════════════════════
                         JEEP CHEROKEE XJ - POWER SOURCES
═══════════════════════════════════════════════════════════════════════════════

    Battery 12V (Constant)                    Ignition 12V (Switched)
         │                                          │
         │                                          │
    [5A Blade Fuse]                                 │
         │                                          │
         ├──────────────────────────┐               │
         │                          │               │
═════════╪══════════════════════════╪═══════════════╪═════════════════════════
         │  POWER LATCH CIRCUIT     │               │
═════════╪══════════════════════════╪═══════════════╪═════════════════════════
         │                          │               │
         │              Relay Pin 86 (coil +)       │
         │                    │                     │
         │                    │    ┌── 1N4007 ──────┘
         │                    │    │   (anode toward IGN,
         │               [1N4007]  │    cathode toward pin 85)
         │               (flyback, │
         │                band     │
         │              toward 86) │
         │                    │    │
         │              Relay Pin 85 (coil −)
         │                    │    │
         │                    └────┤
         │                         │
         │                   2N2222 Collector
         │                         │
         │                   2N2222 Emitter ──── GND
         │                         │
         │                   2N2222 Base
         │                         │
         │                      [1kΩ]
         │                         │
         │                      GPIO27 (Pi pin 13)
         │
         │
    Relay Pin 30 (common)
         │
    Relay Pin 87 (NO) ─────── Buck Converter VIN (+)
                                   │
    Relay Pin 87a (NC)             │
         │                    Buck Converter GND (−) ──── GND (shared)
      (unused)                     │
                              Buck Converter VOUT (+5V)
                                   │
                              Pi USB-C Power Input


    Relay: Standard 12V automotive relay (Bosch-style 5-pin SPDT)
           e.g., Hella 007793041, SPST also acceptable (no 87a needed)

    Power Sequence:
      Key ON  → IGN diode energizes coil → relay closes → buck powers Pi
      Pi boot → GPIO27 HIGH → transistor holds coil → self-latched
      Key OFF → IGN drops, GPIO27 still holds → Pi detects via GPIO17
      Cleanup → GPIO27 LOW → relay opens → buck loses 12V → zero draw
      Failsafe: software timer forces GPIO27 LOW after 45s if Pi hangs


═══════════════════════════════════════════════════════════════════════════════
                      IGNITION SENSE CIRCUIT
═══════════════════════════════════════════════════════════════════════════════

    Ignition 12V (Switched)
         │
      [10kΩ]
         │
         ├──────── GPIO17 (Pi pin 11, INPUT, PUD_DOWN)
         │
      [4.7kΩ]
         │
        GND

    Optional: 100nF ceramic capacitor across the 4.7kΩ to filter
              ignition noise from starter motor / alternator.

    Voltage at GPIO17:  12V × 4.7k / (10k + 4.7k) = ~3.1V (HIGH)
                        Safe for Pi 3.3V GPIO with margin.
                        0V when ignition off (LOW).

    NOTE: Quick_Start_Dashboard_Implementation_v2.md references an
    older 8.2kΩ/3.3kΩ divider design. This 10kΩ/4.7kΩ divider is
    the current standard — it produces a cleaner ~3.1V with less
    current draw (~0.8mA vs ~1.0mA).


═══════════════════════════════════════════════════════════════════════════════
                      BNO055 IMU (GYROSCOPE / PITCH / ROLL)
═══════════════════════════════════════════════════════════════════════════════

    Adafruit BNO055 Breakout (Product #2472)

    Pi Header                BNO055 Breakout
    ─────────                ───────────────
    Pin 1  (3.3V)  ──────── VIN
    Pin 6  (GND)   ──────── GND
    Pin 3  (GPIO2) ──────── SDA
    Pin 5  (GPIO3) ──────── SCL

    I2C Address: 0x28 (default, ADR pin LOW/unconnected)
                 0x29 (ADR pin tied HIGH — use if 0x28 conflicts)

    I2C Bus: /dev/i2c-1 (Pi 4 default)
    Sample Rate: 20 Hz (configurable in gyro_manager.py)

    Mounting: Secure firmly to vehicle chassis or Pi enclosure.
              Orientation matters — X-axis forward, Y-axis left, Z-axis up.
              Use calibrate() after mounting to set zero reference.


═══════════════════════════════════════════════════════════════════════════════
                      REM (RENIX ENGINE MONITOR) CONNECTION
═══════════════════════════════════════════════════════════════════════════════

    REM v4+ (NickInTimeDesign)          Raspberry Pi 4
    ──────────────────────              ──────────────
    USB Micro-B port  ════ USB cable ════  USB-A port #1

    Serial: 115200 baud, 8N1
    Linux Device: /dev/ttyACM0 (CDC ACM USB serial)
    Data: 25 space-delimited fields at ~4 Hz (250ms intervals)

    Fields: timestamp MAP VAC CTS IAT RPM Batt o2 exhaust o2_Heater
            Loop EGR TPS TPS_mode IGN Knock INJ_ms INJ_DC Sync
            STFT LTFT AC_SW AC_REQ GPH AFR

    No external power needed — REM is powered by the vehicle's ECU harness.


═══════════════════════════════════════════════════════════════════════════════
                      WAVESHARE MODBUS RTU 8-CH RELAY MODULE (B)
═══════════════════════════════════════════════════════════════════════════════

    Raspberry Pi 4                USB-to-RS485           Relay Module
    ──────────────               ─────────────          ────────────
    USB-A port #2 ═══ USB ═══ Adapter ═══ 2-wire ═══ RS485 A/B terminals
                                twisted pair

    RS485 Wiring (2-wire half-duplex):
        Adapter Terminal A (+) ──── twisted pair ──── Module Terminal A (+)
        Adapter Terminal B (−) ──── twisted pair ──── Module Terminal B (−)

    Relay Module Power:
        Vehicle 12V (constant) ──[fuse]──── Module VIN (7-36V DC input)
        Vehicle GND ─────────────────────── Module GND

    Protocol: Modbus RTU, 9600 baud 8N1
    Linux Device: /dev/ttyUSB0
    Slave Address: 0x01 (configurable via module DIP switches, range 1-255)
    Coil Addresses: 0x00 through 0x07 (channels 1-8)

    Channel Assignments:
    ┌─────────┬────────┬─────────────────────┬──────────────────────────┐
    │ Channel │ Coil   │ Assignment          │ Notes                    │
    ├─────────┼────────┼─────────────────────┼──────────────────────────┤
    │ 1       │ 0x00   │ AW-4 Solenoid 1     │ Shift solenoid           │
    │ 2       │ 0x01   │ AW-4 Solenoid 2     │ Shift solenoid           │
    │ 3       │ 0x02   │ AW-4 Solenoid 3     │ Shift solenoid           │
    │ 4       │ 0x03   │ Electric Fan Low     │ Auto: ON 210F, OFF 195F │
    │ 5       │ 0x04   │ Electric Fan High    │ Auto: ON 225F, OFF 210F │
    │ 6       │ 0x05   │ Light Bar 1          │ Manual control           │
    │ 7       │ 0x06   │ Light Bar 2          │ Manual control           │
    │ 8       │ 0x07   │ Spare                │ User-configurable        │
    └─────────┴────────┴─────────────────────┴──────────────────────────┘

    Per-channel rating: 10A @ 250VAC / 30VDC
    Min cycle time: 1.0 second per channel (software-enforced)
    Safety: All relays OFF on disconnect / app shutdown


═══════════════════════════════════════════════════════════════════════════════
                      DSI TOUCHSCREEN
═══════════════════════════════════════════════════════════════════════════════

    Freenove 4.3" IPS Capacitive Touchscreen
    ─────────────────────────────────────────
    Connection: 15-pin DSI ribbon cable → Pi DSI connector
    Resolution: 800 x 480 (mounted portrait = 480 x 800)
    Rotation: display_rotate=3 in /boot/config.txt
    Touch: Capacitive (I2C on dedicated DSI pins, not GPIO I2C bus)
    Power: Supplied via DSI ribbon cable (no separate power)


═══════════════════════════════════════════════════════════════════════════════
                      FULL SYSTEM OVERVIEW
═══════════════════════════════════════════════════════════════════════════════

                         Vehicle Battery 12V
                              │
                         [5A Fuse]
                              │
            ┌─────────────────┼──────────────────────────┐
            │                 │                           │
      Power Latch        Waveshare Relay             (future
      Relay Coil +       Module VIN                   expansion)
            │            (7-36V input)
      ┌─[flyback]─┐          │
      │  diode     │     Relay Module GND ── GND
      │            │
      Pin 85 ──┬── Pin 86
               │
          ┌────┤
          │    └── [1N4007] ── Ignition 12V (switched)
          │
     2N2222 (C)
          │
     2N2222 (E) ── GND
          │
     2N2222 (B) ── [1kΩ] ── GPIO27 (pin 13)

      Pin 30 ── Constant 12V
      Pin 87 (NO) ── Buck Converter VIN
                          │
                     Buck Conv VOUT (5V)
                          │
                     Pi USB-C Power
                          │
                    ┌─────┴──────┐
                    │  Pi 4 (4GB) │
                    │             │
                    │  GPIO Header│
                    │   Pin 1  ───┼── 3.3V ──── BNO055 VIN
                    │   Pin 3  ───┼── SDA  ──── BNO055 SDA  (I2C addr 0x28)
                    │   Pin 5  ───┼── SCL  ──── BNO055 SCL
                    │   Pin 6  ───┼── GND  ──── BNO055 GND
                    │   Pin 11 ───┼── GPIO17 ── [10kΩ] ── Ign 12V (switched)
                    │          ───┼────────┤
                    │             │     [4.7kΩ]+[100nF cap]
                    │             │        │
                    │   Pin 14 ───┼── GND ─┘
                    │   Pin 13 ───┼── GPIO27 ── [1kΩ] ── 2N2222 Base
                    │             │
                    │  USB Ports  │
                    │   USB #1 ───┼── USB cable ── REM v4+
                    │   USB #2 ───┼── USB-to-RS485 Adapter ── twisted pair
                    │   USB #3 ───┼── (available)      │
                    │   USB #4 ───┼── (available)      │
                    │             │              Waveshare 8-Ch
                    │  DSI Port   │              Relay Module
                    │   DSI   ────┼── ribbon ── 4.3" Touchscreen
                    │             │
                    └─────────────┘


═══════════════════════════════════════════════════════════════════════════════
                      PARTS LIST (ACTIVE COMPONENTS)
═══════════════════════════════════════════════════════════════════════════════

    COMPUTING & DISPLAY
    ────────────────────
    [ ] Raspberry Pi 4 (4GB)                          ~$55
    [ ] Freenove 4.3" DSI IPS Touchscreen             ~$40
    [ ] 32GB MicroSD (Class 10, A1)                   ~$10

    SENSORS
    ────────
    [ ] Adafruit BNO055 9-DOF IMU (Product #2472)     ~$35

    COMMUNICATION
    ──────────────
    [ ] Renix Engine Monitor v4+ (already installed)    —
    [ ] USB-A to Micro-B cable (3ft, for REM)          ~$5
    [ ] USB-to-RS485 adapter                           ~$12
    [ ] 2-wire twisted pair (RS485, through firewall)  ~$5

    RELAY CONTROL
    ──────────────
    [ ] Waveshare Modbus RTU 8-Ch Relay Module (B)     ~$30

    POWER CIRCUIT
    ──────────────
    [ ] DC-DC Buck Converter 12V→5V (5A output)       ~$18
        (Pololu D36V28F5 or similar)
    [ ] 12V automotive relay (Bosch-style 5-pin SPDT)  ~$3
    [ ] 2N2222 NPN transistor                          ~$0.50
    [ ] 1N4007 rectifier diode (qty 2)                 ~$0.20
    [ ] 1kΩ resistor (1/4W)                            ~$0.05
    [ ] 10kΩ resistor (1/4W)                           ~$0.05
    [ ] 4.7kΩ resistor (1/4W)                          ~$0.05
    [ ] 100nF ceramic capacitor                        ~$0.10
    [ ] 5A blade fuse + inline holder                  ~$3
    [ ] 16AWG wire red/black (6ft)                     ~$5
    [ ] USB-C breakout cable (for Pi power)            ~$5

    ESTIMATED TOTAL (excluding REM): ~$227


═══════════════════════════════════════════════════════════════════════════════
                      GROUND REFERENCE
═══════════════════════════════════════════════════════════════════════════════

    All grounds are common (vehicle chassis ground):
      - Pi GND (any GND pin: 6, 9, 14, 20, 25, 30, 34, 39)
      - Buck converter GND
      - 2N2222 emitter
      - BNO055 GND
      - Ignition sense voltage divider bottom
      - Power latch relay coil (via transistor to GND)
      - Waveshare relay module GND
      - RS485 adapter GND (if applicable — some are USB-powered only)

    IMPORTANT: Use a single, solid ground point on the vehicle chassis
    near the Pi mounting location. Star-ground from that point to avoid
    ground loops that cause noise on I2C and serial lines.


═══════════════════════════════════════════════════════════════════════════════
                      SOFTWARE → HARDWARE MAPPING
═══════════════════════════════════════════════════════════════════════════════

    Source File                         Hardware            Pin/Port
    ───────────────────────────────     ──────────────      ─────────────
    src/core/power_latch.py             Power relay         GPIO27 (out)
    src/core/ignition_monitor.py        Ign sense divider   GPIO17 (in)
    src/core/gyro_manager.py            BNO055 IMU          GPIO2/3 (I2C)
    src/core/serial_manager.py          REM v4+             /dev/ttyACM0
    src/relay/relay_controller.py       Waveshare relay     /dev/ttyUSB0
    main.py                             (orchestrates all of the above)


═══════════════════════════════════════════════════════════════════════════════
                      PIN CONFLICT AUDIT
═══════════════════════════════════════════════════════════════════════════════

    GPIO2  — I2C SDA (BNO055 only)          ✅ No conflict
    GPIO3  — I2C SCL (BNO055 only)          ✅ No conflict
    GPIO17 — Ignition sense INPUT            ✅ No conflict
    GPIO27 — Power latch OUTPUT              ✅ No conflict

    DSI touchscreen uses dedicated DSI I2C lines (not GPIO2/3).  ✅

    USB-A ports: 2 of 4 used, 2 available for GPS module,
    keyboard, or other future peripherals.                      ✅

    I2C bus: BNO055 at 0x28. DSI touch controller is on a
    separate I2C bus. No address conflicts.                     ✅

    VERDICT: No pin conflicts. No address conflicts.
             No shared bus contention.
```
