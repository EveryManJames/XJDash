"""
Mock Serial Data - Simulates REM output for development
"""

import random
import time
import math


class MockREMSerial:
    """
    Simulates Renix Engine Monitor serial output
    Generates realistic data for development without hardware
    """

    def __init__(self):
        # Initialize with realistic idle values
        self.timestamp = 0
        self.rpm = 750
        self.cts = 195  # Coolant temp
        self.iat = 105  # Intake air temp
        self.map = 14.5
        self.vac = 15.4
        self.tps = 17
        self.batt = 13.8
        self.o2 = 2.5
        self.ign = 15
        self.inj_ms = 4.5
        self.stft = 128
        self.ltft = 142

        # Simulation state
        self.engine_running = True
        self.sim_time = 0

    def read_line(self) -> str:
        """
        Generate a line of mock REM data

        Returns:
            Space-delimited string matching REM Normal mode output
        """
        # Block like a real serial readline would — without this the
        # reader thread busy-spins at 100% of a core.
        time.sleep(0.25)
        self.sim_time += 0.25  # 250ms between frames
        self.timestamp += 250

        # Simulate realistic engine behavior
        self._simulate_engine_dynamics()

        # Format as REM Normal mode output
        return self._format_normal_mode()

    def _simulate_engine_dynamics(self):
        """Simulate realistic engine parameter changes"""

        # RPM variation (idle hunting)
        if self.engine_running:
            self.rpm += random.uniform(-20, 20)
            self.rpm = max(600, min(900, self.rpm))  # Keep in idle range

            # Occasionally rev engine (simulate user input)
            if random.random() < 0.01:  # 1% chance each frame
                self.rpm += random.uniform(500, 1500)
        else:
            self.rpm = 0

        # Temperature slowly changes
        self.cts += random.uniform(-0.1, 0.1)
        self.cts = max(180, min(220, self.cts))

        self.iat += random.uniform(-0.2, 0.2)
        self.iat = max(90, min(130, self.iat))

        # MAP/VAC correlated with RPM
        base_map = 14.5
        self.map = base_map + (self.rpm - 750) / 100
        self.vac = 29.92 - self.map  # Atmospheric - MAP

        # TPS (mostly idle, occasional movement)
        if random.random() < 0.05:
            self.tps = random.uniform(17, 95)
        else:
            self.tps = 17 + random.uniform(-1, 1)

        # Battery voltage
        self.batt = 13.8 + random.uniform(-0.1, 0.1)

        # O2 sensor swings in closed loop
        if self.cts > 180:  # Warm engine
            self.o2 += random.uniform(-0.3, 0.3)
            self.o2 = max(0.5, min(4.5, self.o2))
        else:
            self.o2 = 2.5  # Fixed in open loop

        # Ignition timing
        self.ign = 15 + (self.rpm - 750) / 50
        self.ign = max(10, min(40, self.ign))

        # Injector pulse width correlated with RPM
        self.inj_ms = 4.5 + (self.rpm - 750) / 200
        self.inj_ms = max(3, min(20, self.inj_ms))

        # Fuel trims slowly drift
        self.stft += random.uniform(-1, 1)
        self.stft = max(118, min(138, self.stft))

        self.ltft += random.uniform(-0.1, 0.1)
        self.ltft = max(135, min(150, self.ltft))

    def _format_normal_mode(self) -> str:
        """
        Format data as REM Normal mode output

        Returns:
            Space-delimited string with all parameters
        """
        # Calculate derived values
        vac = 29.92 - self.map
        exhaust = "RICH" if self.o2 < 2.5 else "LEAN"
        o2_heater = 13.2 if self.engine_running else 0
        loop = "CLSD" if self.cts > 180 else "OPEN"
        egr = "OFF"  # Usually off at idle
        tps_mode = "CLSD" if self.tps < 20 else "PART"
        knock = int(self.rpm / 50)  # Scales with RPM
        inj_dc = (self.inj_ms * self.rpm) / 1200
        sync = "+"
        ac_sw = "OFF"
        ac_req = "NO"
        gph = (self.inj_ms * self.rpm * 4) / 120000  # Rough estimate
        afr = 14.7 + (self.stft - 128) / 20

        return (
            f"{int(self.timestamp)} "
            f"{self.map:.1f} {vac:.1f} "
            f"{self.cts:.0f} {self.iat:.0f} "
            f"{self.rpm:.0f} {self.batt:.1f} "
            f"{self.o2:.1f} {exhaust} {o2_heater:.1f} "
            f"{loop} {egr} "
            f"{self.tps:.0f} {tps_mode} "
            f"{self.ign:.0f} {knock} "
            f"{self.inj_ms:.1f} {inj_dc:.1f} "
            f"{sync} {self.stft:.0f} {self.ltft:.0f} "
            f"{ac_sw} {ac_req} "
            f"{gph:.2f} {afr:.1f}"
        )
