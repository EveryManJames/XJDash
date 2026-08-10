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
            halign='left',
            valign='center',
            size_hint_y=0.5,
        )
        self.name_label.bind(size=self.name_label.setter('text_size'))

        self.desc_label = Label(
            text=description,
            font_size='11sp',
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
        self.refresh()

    def _skin_color(self, name, alpha=1.0, default=(255, 176, 0)):
        app = App.get_running_app()
        rgb = default
        if app and hasattr(app, 'skin_manager'):
            rgb = app.skin_manager.get_color(name, default)
        return (rgb[0] / 255, rgb[1] / 255, rgb[2] / 255, alpha)

    def refresh(self):
        """Re-apply skin colors (called on selection and skin change)."""
        self.name_label.color = self._skin_color('primary')
        self.desc_label.color = self._skin_color('dim')
        self._redraw()

    def _redraw(self, *args):
        primary = self._skin_color('primary')
        inactive = self._skin_color('inactive', 0.3)
        dim = self._skin_color('dim', 0.3)

        self.canvas.before.clear()
        with self.canvas.before:
            if self.active:
                Color(primary[0], primary[1], primary[2], 0.08)
                RoundedRectangle(pos=self.pos, size=self.size, radius=[8])
                Color(*primary)
            else:
                Color(*inactive)
                RoundedRectangle(pos=self.pos, size=self.size, radius=[8])
                Color(*dim)
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
        section = self._section_label('THEME')
        self.content.add_widget(section)

        self._skin_buttons = []
        for skin_name, display_name, description in SKINS:
            btn = SkinButton(skin_name, display_name, description)
            btn.bind(on_press=self._on_skin_select)
            if skin_name == 'default_amber':
                btn.active = True
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
            halign='center',
            valign='bottom',
            size_hint_y=1,
        )
        about.bind(size=about.setter('text_size'))
        self.register_skin_label(about, 'dim', alpha=0.6)
        self.content.add_widget(about)

    def apply_skin(self):
        for btn in self._skin_buttons:
            btn.refresh()

    def _on_skin_select(self, btn):
        app = App.get_running_app()
        if app.skin_manager.load_skin(btn.skin_name):
            for b in self._skin_buttons:
                b.set_active(b.skin_name == btn.skin_name)

    def _section_label(self, text):
        lbl = Label(
            text=text,
            font_size='11sp',
            halign='left',
            valign='center',
            size_hint_y=None,
            height=30,
            padding=[12, 0],
        )
        lbl.bind(size=lbl.setter('text_size'))
        self.register_skin_label(lbl, 'dim')
        return lbl

    def _placeholder_section(self, title, message):
        box = BoxLayout(orientation='vertical', size_hint_y=None, height=60, padding=[12, 8])
        lbl = Label(
            text=title,
            font_size='11sp',
            halign='left',
            valign='center',
            size_hint_y=0.4,
        )
        lbl.bind(size=lbl.setter('text_size'))
        self.register_skin_label(lbl, 'dim')
        msg = Label(
            text=message,
            font_size='12sp',
            halign='left',
            valign='center',
            size_hint_y=0.6,
        )
        msg.bind(size=msg.setter('text_size'))
        self.register_skin_label(msg, 'dim', alpha=0.5)
        box.add_widget(lbl)
        box.add_widget(msg)
        return box
