"""
IconPicker - Scrollable grid for selecting an icon from the icon library.

Shows all icons organized by category. Tap an icon to select it.
Fires a callback with the selected icon name.
"""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.widget import Widget
from kivy.graphics import Color, RoundedRectangle, Line
from kivy.app import App

from widgets.base_widget import DashWidget
from widgets.icons import draw_icon, ICON_CATEGORIES


class IconCell(ButtonBehavior, Widget):
    """Single tappable icon cell in the picker grid."""

    def __init__(self, icon_name, on_select=None, **kwargs):
        kwargs.setdefault('size_hint', (None, None))
        kwargs.setdefault('size', (64, 64))
        super().__init__(**kwargs)

        self.icon_name = icon_name
        self._on_select = on_select
        self._selected = False
        self._app = None

        self.bind(size=self._redraw, pos=self._redraw)
        self.bind(on_press=self._handle_press)

    def _c(self, name, alpha=1.0):
        if self._app is None:
            self._app = App.get_running_app()
        rgb = self._app.skin_manager.get_color(name)
        if len(rgb) == 4:
            return (rgb[0] / 255, rgb[1] / 255, rgb[2] / 255, rgb[3] / 255)
        return (rgb[0] / 255, rgb[1] / 255, rgb[2] / 255, alpha)

    def set_selected(self, selected):
        self._selected = selected
        self._redraw()

    def _handle_press(self, *args):
        if self._on_select:
            self._on_select(self.icon_name)

    def _redraw(self, *args):
        self.canvas.clear()
        with self.canvas:
            # Background
            if self._selected:
                Color(*self._c('primary', 0.15))
                RoundedRectangle(pos=self.pos, size=self.size, radius=[8])
                Color(*self._c('primary'))
                Line(rounded_rectangle=(self.x, self.y, self.width, self.height, 8), width=1.5)
            else:
                Color(*self._c('inactive', 0.3))
                RoundedRectangle(pos=self.pos, size=self.size, radius=[6])
                Color(*self._c('dim', 0.2))
                Line(rounded_rectangle=(self.x, self.y, self.width, self.height, 6), width=1)

            # Icon
            if self._selected:
                Color(*self._c('primary'))
            else:
                Color(*self._c('primary', 0.7))

            cx = self.x + self.width / 2
            cy = self.y + self.height / 2
            draw_icon(self.icon_name, cx, cy, 28)


class IconPicker(DashWidget):
    """
    Full icon picker with categories and scrollable grid.

    Args:
        current_icon: Currently selected icon name
        on_icon_selected: Callback(icon_name) when user picks an icon
    """

    def __init__(self, current_icon='power', on_icon_selected=None, **kwargs):
        kwargs.setdefault('orientation', 'vertical')
        super().__init__(**kwargs)

        self._current_icon = current_icon
        self._on_icon_selected = on_icon_selected
        self._cells = {}

        # Header
        header = Label(
            text='SELECT ICON',
            font_size='13sp',
            bold=True,
            color=(1, 0.69, 0, 1),
            halign='center',
            valign='center',
            size_hint_y=None,
            height=36,
        )
        header.bind(size=header.setter('text_size'))
        self.add_widget(header)

        # Scrollable content
        scroll = ScrollView(do_scroll_x=False)
        content = BoxLayout(
            orientation='vertical',
            spacing=8,
            padding=[8, 4, 8, 8],
            size_hint_y=None,
        )
        content.bind(minimum_height=content.setter('height'))

        for category_name, icon_names in ICON_CATEGORIES.items():
            # Category label
            cat_label = Label(
                text=category_name.upper(),
                font_size='10sp',
                color=(0.4, 0.27, 0, 1),
                halign='left',
                valign='center',
                size_hint_y=None,
                height=22,
            )
            cat_label.bind(size=cat_label.setter('text_size'))
            content.add_widget(cat_label)

            # Icon grid (6 columns for 480px width)
            grid = GridLayout(
                cols=6,
                spacing=4,
                size_hint_y=None,
            )
            rows_needed = (len(icon_names) + 5) // 6
            grid.height = rows_needed * 68  # 64 + 4 spacing

            for icon_name in icon_names:
                cell = IconCell(
                    icon_name=icon_name,
                    on_select=self._on_cell_select,
                )
                if icon_name == current_icon:
                    cell.set_selected(True)
                self._cells[icon_name] = cell
                grid.add_widget(cell)

            content.add_widget(grid)

        scroll.add_widget(content)
        self.add_widget(scroll)

    def _on_cell_select(self, icon_name):
        # Deselect previous
        if self._current_icon in self._cells:
            self._cells[self._current_icon].set_selected(False)

        # Select new
        self._current_icon = icon_name
        if icon_name in self._cells:
            self._cells[icon_name].set_selected(True)

        # Fire callback
        if self._on_icon_selected:
            self._on_icon_selected(icon_name)

    @property
    def selected_icon(self):
        return self._current_icon
