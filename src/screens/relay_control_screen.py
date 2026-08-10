"""
RelayControlScreen - 8-channel relay toggle grid.
"""

from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label

from screens.base_screen import BaseScreen
from widgets.relay_button import RelayButton


# Channel definitions with Canvas icon names
RELAY_CHANNELS = [
    (1, 'gear', 'SOL A (1-2)', 'AW-4 AUTO'),
    (2, 'gear', 'SOL B (2-3)', 'AW-4 AUTO'),
    (3, 'lock', 'TCC LOCKUP', 'AW-4 AUTO'),
    (4, 'fan', 'ELEC FAN LO', 'AUTO @ 210\u00b0F'),
    (5, 'fan', 'ELEC FAN HI', 'AUTO @ 225\u00b0F'),
    (6, 'lightbar', 'LIGHT BAR 1', 'MANUAL'),
    (7, 'spotlight', 'LIGHT BAR 2', 'MANUAL'),
    (8, 'plug', 'SPARE', 'MANUAL'),
]


class RelayControlScreen(BaseScreen):
    """2x4 grid of relay toggle buttons."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        grid = GridLayout(
            cols=2,
            spacing=8,
            padding=[12, 8, 12, 8],
        )

        for channel, icon_name, name, info in RELAY_CHANNELS:
            grid.add_widget(RelayButton(
                channel=channel, icon_name=icon_name, name=name, info=info,
            ))

        self.content.add_widget(grid)

        # Footer info
        footer = Label(
            text='WAVESHARE 8-CH \u2022 ADDR 01 \u2022 RS485 @ 9600',
            font_size='10sp',
            size_hint_y=None,
            height=30,
            halign='center',
            valign='center',
        )
        footer.bind(size=footer.setter('text_size'))
        self.register_skin_label(footer, 'dim')
        self.content.add_widget(footer)
