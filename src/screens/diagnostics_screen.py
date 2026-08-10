"""
DiagnosticsScreen - Connection status, sensor health, fault codes, system stats.
"""

from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label

from screens.base_screen import BaseScreen
from widgets.status_card import StatusCard


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
                {'label': 'REM Serial', 'value': 'CONNECTED', 'color': 'good'},
                {'label': 'REM Port', 'value': '/dev/ttyACM0'},
                {'label': 'Baud Rate', 'value': '115200'},
                {'label': 'Relay Module', 'value': 'ONLINE', 'color': 'good'},
                {'label': 'RS485 Addr', 'value': '0x01'},
                {'label': 'Data Rate', 'value': '~24 Hz'},
            ],
        ))

        # Sensor Health
        cards.add_widget(StatusCard(
            title='SENSOR HEALTH',
            rows=[
                {'label': 'Coolant Temp', 'data_key': 'CTS', 'format': 'OK \u2022 {:.0f}\u00b0F', 'color': 'good'},
                {'label': 'Intake Air', 'data_key': 'IAT', 'format': 'OK \u2022 {:.0f}\u00b0F', 'color': 'good'},
                {'label': 'O2 Sensor', 'data_key': 'o2', 'format': 'OK \u2022 {:.2f}V', 'color': 'good'},
                {'label': 'MAP Sensor', 'data_key': 'VAC', 'format': 'OK \u2022 {:.1f} inHg', 'color': 'good'},
                {'label': 'TPS', 'data_key': 'TPS', 'format': 'OK \u2022 {:.0f}%', 'color': 'good'},
                {'label': 'Battery', 'data_key': 'Batt', 'format': 'OK \u2022 {:.1f}V', 'color': 'good'},
                {'label': 'Knock Sensor', 'value': 'NO KNOCK', 'color': 'good'},
            ],
        ))

        # Fault Codes
        cards.add_widget(StatusCard(
            title='FAULT CODES',
            rows=[
                {'label': '', 'value': '\u2713 NO ACTIVE FAULT CODES', 'color': 'good'},
            ],
        ))

        # System
        cards.add_widget(StatusCard(
            title='SYSTEM',
            rows=[
                {'label': 'Platform', 'value': 'Raspberry Pi 4'},
                {'label': 'CPU Temp', 'value': '--'},
                {'label': 'Memory', 'value': '4 GB'},
                {'label': 'XJDash Version', 'value': '0.1.0'},
            ],
        ))

        scroll.add_widget(cards)
        self.content.add_widget(scroll)
