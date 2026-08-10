"""
SettingsScreen - Skin selector, relay config, serial port config.
"""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.behaviors import ButtonBehavior
from kivy.graphics import Color, RoundedRectangle, Line
from kivy.app import App

from screens.base_screen import BaseScreen


class SkinButton(ButtonBehavior, BoxLayout):
    """Button to select a skin."""

    def __init__(self, skin_name, display_name, description, **kwargs):
        kwargs.setdefault('orientation', 'vertical')
        kwargs.setdefault('size_hint_y', None)
        kwargs.setdefault('height', 60)
        kwargs.setdefault('padding', [16, 8, 16, 8])
        kwargs.setdefault('spacing', 2)
        super().__init__(**kwargs)

        self.skin_name = skin_name
        self.active = False

        self.name_label = Label(
            text=display_name,
            font_size='14sp',
            bold=True,
            color=(1, 0.69, 0, 1),
            halign='left',
            valign='center',
            size_hint_y=0.5,
        )
        self.name_label.bind(size=self.name_label.setter('text_size'))

        self.desc_label = Label(
            text=description,
            font_size='11sp',
            color=(0.4, 0.27, 0, 1),
            halign='left',
            valign='center',
            size_hint_y=0.5,
        )
        self.desc_label.bind(size=self.desc_label.setter('text_size'))

        self.add_widget(self.name_label)
        self.add_widget(self.desc_label)
        self.bind(size=self._redraw, pos=self._redraw)

    def set_active(self, active):
        self.active = active
        self._redraw()

    def _redraw(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            if self.active:
                Color(1, 0.69, 0, 0.08)
                RoundedRectangle(pos=self.pos, size=self.size, radius=[8])
                Color(1, 0.69, 0, 1)
            else:
                Color(0.04, 0.03, 0, 0.3)
                RoundedRectangle(pos=self.pos, size=self.size, radius=[8])
                Color(0.15, 0.1, 0, 0.3)
            Line(rounded_rectangle=(self.x, self.y, self.width, self.height, 8), width=1)


SKINS = [
    ('default_amber', '1990 Amber LCD', 'Classic amber backlit LCD display'),
    ('green_vfd', 'Green VFD Display', 'Retro green vacuum fluorescent'),
    ('girlfriend', 'Photo Background', 'Modern with custom photo'),
]


class SettingsScreen(BaseScreen):
    """App settings and configuration."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Section: Skin Selector
        section = Label(
            text='THEME',
            font_size='11sp',
            color=(0.4, 0.27, 0, 1),
            halign='left',
            valign='center',
            size_hint_y=None,
            height=30,
            padding=[12, 0],
        )
        section.bind(size=section.setter('text_size'))
        self.content.add_widget(section)

        self._skin_buttons = []
        for skin_name, display_name, description in SKINS:
            btn = SkinButton(skin_name, display_name, description)
            btn.bind(on_press=self._on_skin_select)
            if skin_name == 'default_amber':
                btn.set_active(True)
            self._skin_buttons.append(btn)
            self.content.add_widget(btn)

        # Section: Relay Config (placeholder)
        self.content.add_widget(self._placeholder_section('RELAY CONFIG', 'Coming soon'))

        # Section: Serial Config (placeholder)
        self.content.add_widget(self._placeholder_section('SERIAL PORT', 'Coming soon'))

        # Section: About
        about = Label(
            text='XJDash v0.1.0\nBy James Martin\nMIT License',
            font_size='11sp',
            color=(0.4, 0.27, 0, 0.6),
            halign='center',
            valign='bottom',
            size_hint_y=1,
        )
        about.bind(size=about.setter('text_size'))
        self.content.add_widget(about)

    def _on_skin_select(self, btn):
        app = App.get_running_app()
        if app.skin_manager.load_skin(btn.skin_name):
            for b in self._skin_buttons:
                b.set_active(b.skin_name == btn.skin_name)

    def _placeholder_section(self, title, message):
        box = BoxLayout(orientation='vertical', size_hint_y=None, height=60, padding=[12, 8])
        lbl = Label(
            text=title,
            font_size='11sp',
            color=(0.4, 0.27, 0, 1),
            halign='left',
            valign='center',
            size_hint_y=0.4,
        )
        lbl.bind(size=lbl.setter('text_size'))
        msg = Label(
            text=message,
            font_size='12sp',
            color=(0.25, 0.17, 0, 0.5),
            halign='left',
            valign='center',
            size_hint_y=0.6,
        )
        msg.bind(size=msg.setter('text_size'))
        box.add_widget(lbl)
        box.add_widget(msg)
        return box
