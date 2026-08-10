"""
TransmissionScreen - AW-4 gear indicator, solenoid status, transmission data.
"""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.clock import Clock

from screens.base_screen import BaseScreen
from widgets.gear_indicator import GearIndicator
from widgets.solenoid_row import SolenoidRow
from widgets.base_widget import DashWidget
from core.data_manager import DataManager


class DataRow(DashWidget):
    """Simple label-value row for transmission data."""

    def __init__(self, data_key, label_text, format_str='{:.0f}', unit='',
                 **kwargs):
        kwargs.setdefault('orientation', 'horizontal')
        kwargs.setdefault('size_hint_y', None)
        kwargs.setdefault('height', 32)
        kwargs.setdefault('padding', [12, 0, 12, 0])
        super().__init__(**kwargs)

        self.data_key = data_key
        self.format_str = format_str
        self.unit = unit

        self.label_widget = Label(
            text=label_text, font_size='12sp',
            halign='left', valign='center',
            size_hint_x=0.6,
        )
        self.label_widget.bind(size=self.label_widget.setter('text_size'))

        self.value_widget = Label(
            text='--', font_size='13sp', bold=True,
            halign='right', valign='center',
            size_hint_x=0.4,
        )
        self.value_widget.bind(size=self.value_widget.setter('text_size'))

        self.add_widget(self.label_widget)
        self.add_widget(self.value_widget)
        self._schedule_update(hz=5)

    def _update(self, dt):
        val = self.data_manager.get(self.data_key)
        if val is not None:
            try:
                self.value_widget.text = self.format_str.format(val) + self.unit
            except (ValueError, TypeError):
                self.value_widget.text = str(val)
        self.label_widget.color = self._c('dim')
        self.value_widget.color = self._c('primary')


class TransmissionScreen(BaseScreen):
    """AW-4 transmission monitor and control."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Gear indicator
        self.content.add_widget(GearIndicator())

        # Section: Solenoid Status
        self.content.add_widget(self._section_label('SOLENOID STATUS'))
        self.content.add_widget(SolenoidRow(channel=1, name='SOLENOID A (1-2)'))
        self.content.add_widget(SolenoidRow(channel=2, name='SOLENOID B (2-3)'))
        self.content.add_widget(SolenoidRow(channel=3, name='TCC LOCKUP'))

        # Section: Transmission Data
        self.content.add_widget(self._section_label('TRANSMISSION DATA'))
        self.content.add_widget(DataRow(data_key='RPM', label_text='ENGINE RPM', format_str='{:.0f}'))
        self.content.add_widget(DataRow(data_key='TPS', label_text='TPS', format_str='{:.0f}', unit='%'))
        self.content.add_widget(DataRow(data_key='CTS', label_text='COOLANT TEMP', format_str='{:.0f}', unit='\u00b0F'))
        self.content.add_widget(DataRow(data_key='Batt', label_text='BATTERY', format_str='{:.1f}', unit='V'))

        # Spacer
        self.content.add_widget(BoxLayout(size_hint_y=1))

    def _section_label(self, text):
        lbl = Label(
            text=text,
            font_size='11sp',
            color=(0.4, 0.27, 0, 1),
            halign='left',
            valign='center',
            size_hint_y=None,
            height=28,
            padding=[12, 0],
        )
        lbl.bind(size=lbl.setter('text_size'))
        return lbl
