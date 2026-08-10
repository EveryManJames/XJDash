"""
MainGaugesScreen - Primary dashboard with RPM gauge, data cells, and bar gauges.
"""

from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout

from screens.base_screen import BaseScreen
from widgets.rpm_gauge import RPMArcGauge
from widgets.data_cell import DataCell
from widgets.bar_gauge import BarGauge


class MainGaugesScreen(BaseScreen):
    """Main gauge display — RPM arc, 6 data cells, 2 bar gauges."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # RPM arc gauge (top section)
        self.rpm_gauge = RPMArcGauge()
        self.content.add_widget(self.rpm_gauge)

        # 6 data cells in a 2-column grid
        grid = GridLayout(
            cols=2,
            spacing=2,
            padding=[8, 4, 8, 4],
            size_hint_y=None,
            height=300,
        )

        grid.add_widget(DataCell(
            data_key='CTS', label_text='COOLANT', unit='\u00b0F',
            format_str='{:.0f}',
            warning_threshold=220, critical_threshold=240,
        ))
        grid.add_widget(DataCell(
            data_key='Batt', label_text='BATTERY', unit='VOLTS',
            format_str='{:.1f}',
            warning_threshold=11.5, critical_threshold=10.5,
            warn_below=True,
        ))
        grid.add_widget(DataCell(
            data_key='VAC', label_text='MAP', unit='inHg VAC',
            format_str='{:.1f}',
        ))
        grid.add_widget(DataCell(
            data_key='TPS', label_text='TPS', unit='% OPEN',
            format_str='{:.0f}',
        ))
        grid.add_widget(DataCell(
            data_key='o2', label_text='O2 SENSOR', unit='VOLTS',
            format_str='{:.2f}',
        ))
        grid.add_widget(DataCell(
            data_key='INJ_ms', label_text='INJ PULSE', unit='ms',
            format_str='{:.1f}',
        ))

        self.content.add_widget(grid)

        # Bar gauges section
        bars = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=82,
            padding=[0, 4, 0, 0],
        )
        bars.add_widget(BarGauge(
            data_key='CTS', label_text='COOLANT TEMP',
            min_val=100, max_val=260,
            warning_threshold=230,
            format_str='{:.0f}', unit='\u00b0F',
        ))
        bars.add_widget(BarGauge(
            data_key='IAT', label_text='INTAKE AIR',
            min_val=50, max_val=200,
            warning_threshold=160,
            format_str='{:.0f}', unit='\u00b0F',
        ))
        self.content.add_widget(bars)

        # Spacer to push content up
        spacer = BoxLayout(size_hint_y=1)
        self.content.add_widget(spacer)
