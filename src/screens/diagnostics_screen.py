"""
DiagnosticsScreen - Connection status, sensor health, fault codes, system stats.

Values are read live from the running app's managers via value_fn callables
— nothing here is hardcoded to look healthy when it isn't.
"""

import os
import platform

from kivy.app import App
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout

from screens.base_screen import BaseScreen
from widgets.status_card import StatusCard
from core.data_manager import DataManager, STALE_AFTER


def _app():
    return App.get_running_app()


def _rem_status():
    app = _app()
    sm = getattr(app, 'serial_manager', None)
    if not sm or not sm.connected:
        return ('DISCONNECTED', 'err')
    # Same liveness rule as the header: a connected port that stopped
    # producing data is NO DATA, not CONNECTED.
    age = DataManager().age('RPM')
    if age is None or age > STALE_AFTER:
        return ('NO DATA', 'err')
    if sm.use_mock:
        return ('MOCK DATA', 'warn')
    return ('CONNECTED', 'good')


def _rem_port():
    sm = getattr(_app(), 'serial_manager', None)
    return sm.port if sm else '--'


def _rem_baud():
    sm = getattr(_app(), 'serial_manager', None)
    return str(sm.baud) if sm else '--'


def _relay_status():
    rc = getattr(_app(), 'relay_controller', None)
    if not rc or not rc.connected:
        return ('OFFLINE', 'err')
    if rc.is_mock:
        return ('MOCK', 'warn')
    return ('ONLINE', 'good')


def _relay_addr():
    rc = getattr(_app(), 'relay_controller', None)
    if rc:
        return f"0x{rc.config['slave_address']:02X}"
    return '--'


def _data_rate():
    dm = DataManager()
    hz = dm.get('_rem_hz')
    age = dm.age('_rem_hz')
    # The rate is only republished while lines arrive — an old value
    # means traffic stopped, so show placeholder instead of a stale Hz.
    if hz is None or age is None or age > STALE_AFTER:
        return '--'
    return f'{hz:.1f} Hz'


def _platform_name():
    # Pi exposes its model string; everything else gets the generic name
    model_path = '/proc/device-tree/model'
    if os.path.exists(model_path):
        try:
            with open(model_path) as f:
                return f.read().strip('\x00').strip()
        except OSError:
            pass
    return f'{platform.system()} {platform.machine()}'


def _cpu_temp():
    temp_path = '/sys/class/thermal/thermal_zone0/temp'
    if os.path.exists(temp_path):
        try:
            with open(temp_path) as f:
                millideg = int(f.read().strip())
            return f'{millideg / 1000:.0f}°C'
        except (OSError, ValueError):
            pass
    return '--'


def _memory_gb():
    try:
        total = os.sysconf('SC_PHYS_PAGES') * os.sysconf('SC_PAGE_SIZE')
        return f'{total / (1024 ** 3):.0f} GB'
    except (ValueError, OSError):
        return '--'


class DiagnosticsScreen(BaseScreen):
    """System diagnostics and sensor health monitor."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        scroll = ScrollView(do_scroll_x=False)
        cards = BoxLayout(
            orientation='vertical',
            spacing=8,
            padding=[8, 8, 8, 8],
            size_hint_y=None,
        )
        cards.bind(minimum_height=cards.setter('height'))

        # Connection Status
        cards.add_widget(StatusCard(
            title='CONNECTION STATUS',
            rows=[
                {'label': 'REM Serial', 'value_fn': _rem_status},
                {'label': 'REM Port', 'value_fn': _rem_port},
                {'label': 'Baud Rate', 'value_fn': _rem_baud},
                {'label': 'Relay Module', 'value_fn': _relay_status},
                {'label': 'RS485 Addr', 'value_fn': _relay_addr},
                {'label': 'Data Rate', 'value_fn': _data_rate},
            ],
        ))

        # Sensor Health
        cards.add_widget(StatusCard(
            title='SENSOR HEALTH',
            rows=[
                {'label': 'Coolant Temp', 'data_key': 'CTS', 'format': '{:.0f}°F'},
                {'label': 'Intake Air', 'data_key': 'IAT', 'format': '{:.0f}°F'},
                {'label': 'O2 Sensor', 'data_key': 'o2', 'format': '{:.2f}V'},
                {'label': 'MAP Sensor', 'data_key': 'VAC', 'format': '{:.1f} inHg'},
                {'label': 'TPS', 'data_key': 'TPS', 'format': '{:.0f}%'},
                {'label': 'Battery', 'data_key': 'Batt', 'format': '{:.1f}V'},
                {'label': 'Knock Count', 'data_key': 'Knock', 'format': '{:.0f}'},
            ],
        ))

        # Fault Codes (REM does not stream fault codes yet)
        cards.add_widget(StatusCard(
            title='FAULT CODES',
            rows=[
                {'label': '', 'value': 'NOT MONITORED', 'color': 'default'},
            ],
        ))

        # System
        cards.add_widget(StatusCard(
            title='SYSTEM',
            rows=[
                {'label': 'Platform', 'value': _platform_name()},
                {'label': 'CPU Temp', 'value_fn': _cpu_temp},
                {'label': 'Memory', 'value': _memory_gb()},
                {'label': 'XJDash Version', 'value': '0.1.0'},
            ],
        ))

        scroll.add_widget(cards)
        self.content.add_widget(scroll)
