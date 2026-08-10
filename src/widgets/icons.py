"""
XJDash Icon Library — Self-contained Canvas-drawn icons.

Each icon is a function that draws into a Kivy Canvas at a given
position and size using the current Color. No external files needed.
Icons scale to any size and inherit the active canvas Color.

Usage:
    from widgets.icons import draw_icon, ICON_CATEGORIES

    with self.canvas:
        Color(1, 0.69, 0, 1)
        draw_icon('fan', x, y, size)
"""

import math
from kivy.graphics import Line, Ellipse, Rectangle, Triangle
from kivy.graphics import Color as KivyColor
from kivy.uix.widget import Widget


# ─── Drawing Helpers ───────────────────────────────────────────────

def _line(points, width=1.5, cap='round'):
    """Draw a line from a list of (x, y) tuples."""
    flat = []
    for p in points:
        flat.extend(p)
    Line(points=flat, width=width, cap=cap, joint='miter')


def _circle(cx, cy, r, width=1.5):
    """Draw a circle outline."""
    Line(ellipse=(cx - r, cy - r, r * 2, r * 2), width=width)


def _filled_circle(cx, cy, r):
    """Draw a filled circle."""
    Ellipse(pos=(cx - r, cy - r), size=(r * 2, r * 2))


def _arc(cx, cy, r, start_deg, end_deg, width=1.5):
    """Draw an arc."""
    Line(ellipse=(cx - r, cy - r, r * 2, r * 2, start_deg, end_deg), width=width)


def _rect(x, y, w, h, width=1.5):
    """Draw a rectangle outline."""
    Line(rectangle=(x, y, w, h), width=width)


def _filled_rect(x, y, w, h):
    """Draw a filled rectangle."""
    Rectangle(pos=(x, y), size=(w, h))


def _arrow(x1, y1, x2, y2, head_size=4, width=1.5):
    """Draw a line with an arrowhead at (x2, y2)."""
    Line(points=[x1, y1, x2, y2], width=width, cap='round')
    angle = math.atan2(y2 - y1, x2 - x1)
    a1 = angle + math.radians(150)
    a2 = angle - math.radians(150)
    Line(points=[
        x2, y2,
        x2 + head_size * math.cos(a1), y2 + head_size * math.sin(a1),
    ], width=width, cap='round')
    Line(points=[
        x2, y2,
        x2 + head_size * math.cos(a2), y2 + head_size * math.sin(a2),
    ], width=width, cap='round')


# ─── Icon Draw Functions ───────────────────────────────────────────
# Each takes (cx, cy, s) where cx/cy is center and s is half-size.

def _icon_fan(cx, cy, s):
    """Cooling fan — 4 curved blades."""
    _circle(cx, cy, s * 0.9, 1.5)
    _filled_circle(cx, cy, s * 0.15)
    for angle_deg in [0, 90, 180, 270]:
        a = math.radians(angle_deg)
        a2 = math.radians(angle_deg + 60)
        r = s * 0.65
        x1 = cx + r * 0.2 * math.cos(a)
        y1 = cy + r * 0.2 * math.sin(a)
        x2 = cx + r * math.cos(a)
        y2 = cy + r * math.sin(a)
        x3 = cx + r * 0.8 * math.cos(a2)
        y3 = cy + r * 0.8 * math.sin(a2)
        _line([(x1, y1), (x2, y2), (x3, y3)], 2)


def _icon_lightbar(cx, cy, s):
    """Light bar — rectangle with rays."""
    bw = s * 1.2
    bh = s * 0.4
    _rect(cx - bw / 2, cy - bh / 2, bw, bh, 1.5)
    # Light rays above
    for i in range(-2, 3):
        rx = cx + i * s * 0.3
        _line([(rx, cy + bh / 2 + s * 0.1), (rx, cy + bh / 2 + s * 0.45)], 1.5)


def _icon_spotlight(cx, cy, s):
    """Spotlight / flood light."""
    _arc(cx, cy, s * 0.5, 30, 150, 2)
    _line([(cx - s * 0.5, cy - s * 0.3), (cx + s * 0.5, cy - s * 0.3)], 1.5)
    _line([(cx - s * 0.3, cy - s * 0.3), (cx - s * 0.5, cy - s * 0.7)], 1.5)
    _line([(cx + s * 0.3, cy - s * 0.3), (cx + s * 0.5, cy - s * 0.7)], 1.5)
    # Rays
    for a_deg in [60, 90, 120]:
        a = math.radians(a_deg)
        x1 = cx + s * 0.55 * math.cos(a)
        y1 = cy + s * 0.55 * math.sin(a)
        x2 = cx + s * 0.85 * math.cos(a)
        y2 = cy + s * 0.85 * math.sin(a)
        _line([(x1, y1), (x2, y2)], 1.5)


def _icon_winch(cx, cy, s):
    """Winch spool with cable."""
    _circle(cx - s * 0.2, cy, s * 0.4, 2)
    _circle(cx - s * 0.2, cy, s * 0.15, 1.5)
    # Cable going right
    _line([(cx + s * 0.2, cy), (cx + s * 0.9, cy)], 2)
    # Hook
    _arc(cx + s * 0.8, cy - s * 0.25, s * 0.15, -90, 180, 2)


def _icon_difflock(cx, cy, s):
    """Differential lock — axle with locked gears."""
    # Axle line
    _line([(cx - s * 0.9, cy), (cx + s * 0.9, cy)], 2)
    # Left wheel
    _filled_rect(cx - s * 0.9, cy - s * 0.35, s * 0.2, s * 0.7)
    # Right wheel
    _filled_rect(cx + s * 0.7, cy - s * 0.35, s * 0.2, s * 0.7)
    # Diff housing
    _circle(cx, cy, s * 0.3, 2)
    # Lock symbol (X)
    _line([(cx - s * 0.15, cy - s * 0.15), (cx + s * 0.15, cy + s * 0.15)], 2)
    _line([(cx - s * 0.15, cy + s * 0.15), (cx + s * 0.15, cy - s * 0.15)], 2)


def _icon_compressor(cx, cy, s):
    """Air compressor — tank with gauge."""
    # Tank body
    bw = s * 1.4
    bh = s * 0.8
    _rect(cx - bw / 2, cy - bh / 2 - s * 0.15, bw, bh, 2)
    # Gauge circle on top
    _circle(cx, cy + s * 0.5, s * 0.25, 1.5)
    # Gauge needle
    _line([(cx, cy + s * 0.5), (cx + s * 0.15, cy + s * 0.65)], 1.5)
    # Feet
    _line([(cx - s * 0.5, cy - bh / 2 - s * 0.15), (cx - s * 0.5, cy - s * 0.7)], 2)
    _line([(cx + s * 0.5, cy - bh / 2 - s * 0.15), (cx + s * 0.5, cy - s * 0.7)], 2)


def _icon_horn(cx, cy, s):
    """Air horn / siren."""
    # Bell shape
    _line([(cx - s * 0.2, cy - s * 0.1), (cx - s * 0.7, cy - s * 0.5)], 2)
    _line([(cx - s * 0.2, cy + s * 0.1), (cx - s * 0.7, cy + s * 0.5)], 2)
    _line([(cx - s * 0.7, cy - s * 0.5), (cx - s * 0.7, cy + s * 0.5)], 2)
    _circle(cx, cy, s * 0.2, 2)
    # Sound waves
    _arc(cx + s * 0.4, cy, s * 0.25, -60, 60, 1.5)
    _arc(cx + s * 0.55, cy, s * 0.35, -60, 60, 1.5)


def _icon_hazard(cx, cy, s):
    """Hazard / warning triangle."""
    top = (cx, cy + s * 0.8)
    bl = (cx - s * 0.8, cy - s * 0.6)
    br = (cx + s * 0.8, cy - s * 0.6)
    _line([top, bl, br, top], 2)
    _line([(cx, cy + s * 0.35), (cx, cy - s * 0.1)], 2)
    _filled_circle(cx, cy - s * 0.3, s * 0.08)


def _icon_power(cx, cy, s):
    """Power symbol — circle with line."""
    _arc(cx, cy, s * 0.65, 50, 310, 2)
    _line([(cx, cy + s * 0.2), (cx, cy + s * 0.75)], 2.5)


def _icon_lightning(cx, cy, s):
    """Lightning bolt."""
    _line([
        (cx + s * 0.1, cy + s * 0.85),
        (cx - s * 0.25, cy + s * 0.1),
        (cx + s * 0.1, cy + s * 0.1),
        (cx - s * 0.1, cy - s * 0.85),
        (cx + s * 0.25, cy - s * 0.1),
        (cx - s * 0.1, cy - s * 0.1),
        (cx + s * 0.1, cy + s * 0.85),
    ], 2)


def _icon_fuel(cx, cy, s):
    """Fuel pump."""
    # Pump body
    _rect(cx - s * 0.5, cy - s * 0.6, s * 0.8, s * 1.2, 2)
    # Nozzle
    _line([(cx + s * 0.3, cy + s * 0.3), (cx + s * 0.7, cy + s * 0.3)], 2)
    _line([(cx + s * 0.7, cy + s * 0.3), (cx + s * 0.7, cy - s * 0.2)], 2)
    _line([(cx + s * 0.7, cy - s * 0.2), (cx + s * 0.5, cy - s * 0.4)], 2)
    # Gauge inside
    _rect(cx - s * 0.3, cy + s * 0.0, s * 0.4, s * 0.3, 1)


def _icon_thermometer(cx, cy, s):
    """Thermometer."""
    _line([(cx, cy + s * 0.8), (cx, cy - s * 0.3)], 2)
    _circle(cx, cy - s * 0.55, s * 0.25, 2)
    _filled_circle(cx, cy - s * 0.55, s * 0.15)
    # Tube walls
    _line([(cx - s * 0.1, cy + s * 0.7), (cx - s * 0.1, cy - s * 0.3)], 1)
    _line([(cx + s * 0.1, cy + s * 0.7), (cx + s * 0.1, cy - s * 0.3)], 1)
    # Tick marks
    for i in range(4):
        y = cy + s * 0.6 - i * s * 0.25
        _line([(cx + s * 0.1, y), (cx + s * 0.25, y)], 1)


def _icon_battery(cx, cy, s):
    """Battery."""
    _rect(cx - s * 0.6, cy - s * 0.4, s * 1.2, s * 0.8, 2)
    _filled_rect(cx + s * 0.6, cy - s * 0.15, s * 0.15, s * 0.3)
    # Plus
    _line([(cx - s * 0.35, cy), (cx - s * 0.1, cy)], 2)
    _line([(cx - s * 0.225, cy - s * 0.15), (cx - s * 0.225, cy + s * 0.15)], 2)
    # Minus
    _line([(cx + s * 0.1, cy), (cx + s * 0.35, cy)], 2)


def _icon_antenna(cx, cy, s):
    """Antenna / radio / CB."""
    _line([(cx, cy - s * 0.8), (cx, cy + s * 0.6)], 2)
    # Base
    _line([(cx - s * 0.3, cy - s * 0.8), (cx + s * 0.3, cy - s * 0.8)], 2)
    # Signal arcs
    _arc(cx, cy + s * 0.3, s * 0.3, 30, 150, 1.5)
    _arc(cx, cy + s * 0.3, s * 0.55, 40, 140, 1.5)


def _icon_gear(cx, cy, s):
    """Gear / settings."""
    _circle(cx, cy, s * 0.3, 2)
    for i in range(8):
        a = math.radians(i * 45)
        inner = s * 0.45
        outer = s * 0.7
        x1 = cx + inner * math.cos(a)
        y1 = cy + inner * math.sin(a)
        x2 = cx + outer * math.cos(a)
        y2 = cy + outer * math.sin(a)
        _line([(x1, y1), (x2, y2)], 3)


def _icon_wrench(cx, cy, s):
    """Wrench / spanner."""
    _line([(cx - s * 0.6, cy - s * 0.6), (cx + s * 0.3, cy + s * 0.3)], 2.5)
    _circle(cx + s * 0.45, cy + s * 0.45, s * 0.3, 2)
    _arc(cx + s * 0.45, cy + s * 0.45, s * 0.15, 0, 360, 1)


def _icon_headlight(cx, cy, s):
    """Headlight / driving light."""
    _arc(cx - s * 0.2, cy, s * 0.5, -90, 90, 2)
    _line([(cx - s * 0.2, cy + s * 0.5), (cx - s * 0.2, cy - s * 0.5)], 2)
    # Beams
    for i in range(-1, 2):
        y = cy + i * s * 0.25
        _line([(cx + s * 0.3, y), (cx + s * 0.8, y)], 1.5)


def _icon_siren(cx, cy, s):
    """Emergency siren / beacon."""
    # Base
    _line([(cx - s * 0.6, cy - s * 0.4), (cx + s * 0.6, cy - s * 0.4)], 2)
    # Dome
    _arc(cx, cy - s * 0.1, s * 0.4, 0, 180, 2)
    # Flash rays
    _line([(cx, cy + s * 0.3), (cx, cy + s * 0.7)], 2)
    _line([(cx - s * 0.4, cy + s * 0.15), (cx - s * 0.7, cy + s * 0.4)], 1.5)
    _line([(cx + s * 0.4, cy + s * 0.15), (cx + s * 0.7, cy + s * 0.4)], 1.5)


def _icon_lock(cx, cy, s):
    """Lock / security."""
    _rect(cx - s * 0.4, cy - s * 0.6, s * 0.8, s * 0.7, 2)
    _arc(cx, cy + s * 0.1, s * 0.3, 0, 180, 2)
    _filled_circle(cx, cy - s * 0.3, s * 0.1)


def _icon_unlock(cx, cy, s):
    """Unlock / open."""
    _rect(cx - s * 0.4, cy - s * 0.6, s * 0.8, s * 0.7, 2)
    _arc(cx + s * 0.15, cy + s * 0.1, s * 0.3, 0, 180, 2)
    _filled_circle(cx, cy - s * 0.3, s * 0.1)


def _icon_water(cx, cy, s):
    """Water / fluid — droplet."""
    # Teardrop shape using lines
    _line([
        (cx, cy + s * 0.8),
        (cx - s * 0.4, cy - s * 0.1),
    ], 2)
    _line([
        (cx, cy + s * 0.8),
        (cx + s * 0.4, cy - s * 0.1),
    ], 2)
    _arc(cx, cy - s * 0.25, s * 0.4, 180, 360, 2)


def _icon_shield(cx, cy, s):
    """Shield / protection."""
    _line([
        (cx, cy + s * 0.8),
        (cx - s * 0.6, cy + s * 0.4),
        (cx - s * 0.6, cy - s * 0.2),
        (cx, cy - s * 0.7),
        (cx + s * 0.6, cy - s * 0.2),
        (cx + s * 0.6, cy + s * 0.4),
        (cx, cy + s * 0.8),
    ], 2)


def _icon_camera(cx, cy, s):
    """Camera / dashcam."""
    _rect(cx - s * 0.6, cy - s * 0.35, s * 1.2, s * 0.7, 2)
    _circle(cx, cy, s * 0.25, 2)
    _filled_rect(cx - s * 0.4, cy + s * 0.35, s * 0.3, s * 0.2)


def _icon_speaker(cx, cy, s):
    """Speaker / audio."""
    _rect(cx - s * 0.5, cy - s * 0.25, s * 0.4, s * 0.5, 2)
    _line([
        (cx - s * 0.1, cy + s * 0.25),
        (cx + s * 0.3, cy + s * 0.55),
        (cx + s * 0.3, cy - s * 0.55),
        (cx - s * 0.1, cy - s * 0.25),
    ], 2)
    _arc(cx + s * 0.45, cy, s * 0.2, -60, 60, 1.5)
    _arc(cx + s * 0.6, cy, s * 0.3, -60, 60, 1.5)


# ─── Generic / Directional Icons ─────────────────────────────────

def _icon_arrow_up(cx, cy, s):
    _arrow(cx, cy - s * 0.7, cx, cy + s * 0.7, s * 0.25, 2)


def _icon_arrow_down(cx, cy, s):
    _arrow(cx, cy + s * 0.7, cx, cy - s * 0.7, s * 0.25, 2)


def _icon_arrow_left(cx, cy, s):
    _arrow(cx + s * 0.7, cy, cx - s * 0.7, cy, s * 0.25, 2)


def _icon_arrow_right(cx, cy, s):
    _arrow(cx - s * 0.7, cy, cx + s * 0.7, cy, s * 0.25, 2)


def _icon_arrows_updown(cx, cy, s):
    _arrow(cx, cy - s * 0.2, cx, cy + s * 0.7, s * 0.2, 2)
    _arrow(cx, cy + s * 0.2, cx, cy - s * 0.7, s * 0.2, 2)


def _icon_arrows_leftright(cx, cy, s):
    _arrow(cx - s * 0.2, cy, cx + s * 0.7, cy, s * 0.2, 2)
    _arrow(cx + s * 0.2, cy, cx - s * 0.7, cy, s * 0.2, 2)


def _icon_compass(cx, cy, s):
    """Compass."""
    _circle(cx, cy, s * 0.75, 1.5)
    # N-S needle
    _line([(cx, cy + s * 0.6), (cx, cy - s * 0.6)], 2)
    _line([(cx - s * 0.6, cy), (cx + s * 0.6, cy)], 1)
    # N arrow
    _filled_circle(cx, cy + s * 0.5, s * 0.08)
    # Center
    _filled_circle(cx, cy, s * 0.06)


def _icon_crosshair(cx, cy, s):
    """Crosshair / target."""
    _circle(cx, cy, s * 0.55, 1.5)
    _circle(cx, cy, s * 0.25, 1)
    _line([(cx, cy + s * 0.8), (cx, cy + s * 0.55)], 1.5)
    _line([(cx, cy - s * 0.8), (cx, cy - s * 0.55)], 1.5)
    _line([(cx - s * 0.8, cy), (cx - s * 0.55, cy)], 1.5)
    _line([(cx + s * 0.8, cy), (cx + s * 0.55, cy)], 1.5)


def _icon_on_off(cx, cy, s):
    """On/Off toggle circle."""
    _circle(cx, cy, s * 0.7, 2)
    _filled_circle(cx, cy, s * 0.25)


def _icon_check(cx, cy, s):
    """Checkmark."""
    _line([
        (cx - s * 0.5, cy),
        (cx - s * 0.1, cy - s * 0.45),
        (cx + s * 0.6, cy + s * 0.5),
    ], 2.5)


def _icon_x_mark(cx, cy, s):
    """X / close."""
    _line([(cx - s * 0.5, cy - s * 0.5), (cx + s * 0.5, cy + s * 0.5)], 2.5)
    _line([(cx - s * 0.5, cy + s * 0.5), (cx + s * 0.5, cy - s * 0.5)], 2.5)


def _icon_plus(cx, cy, s):
    """Plus."""
    _line([(cx, cy - s * 0.6), (cx, cy + s * 0.6)], 2.5)
    _line([(cx - s * 0.6, cy), (cx + s * 0.6, cy)], 2.5)


def _icon_minus(cx, cy, s):
    """Minus."""
    _line([(cx - s * 0.6, cy), (cx + s * 0.6, cy)], 2.5)


def _icon_star(cx, cy, s):
    """Star."""
    points = []
    for i in range(5):
        outer_a = math.radians(90 + i * 72)
        inner_a = math.radians(90 + i * 72 + 36)
        points.append((cx + s * 0.7 * math.cos(outer_a), cy + s * 0.7 * math.sin(outer_a)))
        points.append((cx + s * 0.3 * math.cos(inner_a), cy + s * 0.3 * math.sin(inner_a)))
    points.append(points[0])
    _line(points, 2)


def _icon_heart(cx, cy, s):
    """Heart."""
    _arc(cx - s * 0.3, cy + s * 0.2, s * 0.35, 0, 180, 2)
    _arc(cx + s * 0.3, cy + s * 0.2, s * 0.35, 0, 180, 2)
    _line([
        (cx - s * 0.65, cy + s * 0.2),
        (cx, cy - s * 0.65),
        (cx + s * 0.65, cy + s * 0.2),
    ], 2)


def _icon_circle(cx, cy, s):
    """Simple circle."""
    _circle(cx, cy, s * 0.65, 2)


def _icon_square(cx, cy, s):
    """Simple square."""
    _rect(cx - s * 0.55, cy - s * 0.55, s * 1.1, s * 1.1, 2)


def _icon_triangle(cx, cy, s):
    """Triangle."""
    _line([
        (cx, cy + s * 0.7),
        (cx - s * 0.65, cy - s * 0.5),
        (cx + s * 0.65, cy - s * 0.5),
        (cx, cy + s * 0.7),
    ], 2)


def _icon_diamond(cx, cy, s):
    """Diamond."""
    _line([
        (cx, cy + s * 0.7),
        (cx - s * 0.55, cy),
        (cx, cy - s * 0.7),
        (cx + s * 0.55, cy),
        (cx, cy + s * 0.7),
    ], 2)


def _icon_skull(cx, cy, s):
    """Skull / danger."""
    _arc(cx, cy + s * 0.1, s * 0.5, 0, 180, 2)
    _line([(cx - s * 0.5, cy + s * 0.1), (cx - s * 0.5, cy - s * 0.1)], 2)
    _line([(cx + s * 0.5, cy + s * 0.1), (cx + s * 0.5, cy - s * 0.1)], 2)
    _line([(cx - s * 0.5, cy - s * 0.1), (cx + s * 0.5, cy - s * 0.1)], 2)
    # Eyes
    _filled_circle(cx - s * 0.2, cy + s * 0.2, s * 0.1)
    _filled_circle(cx + s * 0.2, cy + s * 0.2, s * 0.1)
    # Teeth
    _line([(cx - s * 0.2, cy - s * 0.1), (cx - s * 0.2, cy - s * 0.3)], 1.5)
    _line([(cx, cy - s * 0.1), (cx, cy - s * 0.3)], 1.5)
    _line([(cx + s * 0.2, cy - s * 0.1), (cx + s * 0.2, cy - s * 0.3)], 1.5)


def _icon_radioactive(cx, cy, s):
    """Radioactive / nuclear."""
    _circle(cx, cy, s * 0.2, 2)
    for a_deg in [90, 210, 330]:
        a1 = math.radians(a_deg - 30)
        a2 = math.radians(a_deg + 30)
        # Wedge from inner to outer
        r1 = s * 0.3
        r2 = s * 0.7
        _line([
            (cx + r1 * math.cos(a1), cy + r1 * math.sin(a1)),
            (cx + r2 * math.cos(a1), cy + r2 * math.sin(a1)),
        ], 2)
        _line([
            (cx + r1 * math.cos(a2), cy + r1 * math.sin(a2)),
            (cx + r2 * math.cos(a2), cy + r2 * math.sin(a2)),
        ], 2)
        _arc(cx, cy, r2, a_deg - 30, a_deg + 30, 2)


def _icon_fire(cx, cy, s):
    """Fire / flame."""
    _line([
        (cx - s * 0.3, cy - s * 0.6),
        (cx - s * 0.4, cy),
        (cx - s * 0.1, cy - s * 0.1),
        (cx, cy + s * 0.7),
        (cx + s * 0.1, cy - s * 0.1),
        (cx + s * 0.4, cy),
        (cx + s * 0.3, cy - s * 0.6),
    ], 2)


def _icon_plug(cx, cy, s):
    """Electrical plug / connector."""
    _line([(cx - s * 0.2, cy + s * 0.7), (cx - s * 0.2, cy + s * 0.2)], 2)
    _line([(cx + s * 0.2, cy + s * 0.7), (cx + s * 0.2, cy + s * 0.2)], 2)
    _rect(cx - s * 0.35, cy - s * 0.1, s * 0.7, s * 0.35, 2)
    _line([(cx, cy - s * 0.1), (cx, cy - s * 0.6)], 2)


def _icon_wave(cx, cy, s):
    """Wave / signal."""
    _arc(cx, cy, s * 0.2, -60, 60, 2)
    _arc(cx, cy, s * 0.4, -60, 60, 2)
    _arc(cx, cy, s * 0.6, -60, 60, 2)
    _filled_circle(cx - s * 0.1, cy, s * 0.06)


def _icon_eye(cx, cy, s):
    """Eye / view / camera."""
    _arc(cx, cy, s * 0.6, 20, 160, 2)
    _arc(cx, cy, s * 0.6, 200, 340, 2)
    _circle(cx, cy, s * 0.2, 2)
    _filled_circle(cx, cy, s * 0.1)


def _icon_clock(cx, cy, s):
    """Clock / timer."""
    _circle(cx, cy, s * 0.65, 2)
    _line([(cx, cy), (cx, cy + s * 0.4)], 2)
    _line([(cx, cy), (cx + s * 0.3, cy)], 2)
    _filled_circle(cx, cy, s * 0.05)


def _icon_gauge(cx, cy, s):
    """Gauge / meter."""
    _arc(cx, cy, s * 0.65, 20, 160, 2)
    _line([(cx - s * 0.65, cy), (cx + s * 0.65, cy)], 1.5)
    # Needle
    _line([(cx, cy), (cx + s * 0.3, cy + s * 0.45)], 2.5)
    _filled_circle(cx, cy, s * 0.07)


def _icon_mountain(cx, cy, s):
    """Mountain / off-road / trail."""
    _line([
        (cx - s * 0.8, cy - s * 0.5),
        (cx - s * 0.2, cy + s * 0.6),
        (cx + s * 0.05, cy + s * 0.3),
        (cx + s * 0.35, cy + s * 0.65),
        (cx + s * 0.8, cy - s * 0.5),
    ], 2)


def _icon_tree(cx, cy, s):
    """Tree / nature."""
    _line([(cx, cy - s * 0.7), (cx, cy - s * 0.2)], 2)
    _line([
        (cx - s * 0.4, cy - s * 0.2),
        (cx, cy + s * 0.7),
        (cx + s * 0.4, cy - s * 0.2),
        (cx - s * 0.4, cy - s * 0.2),
    ], 2)


def _icon_sun(cx, cy, s):
    """Sun / day mode."""
    _circle(cx, cy, s * 0.3, 2)
    for i in range(8):
        a = math.radians(i * 45)
        _line([
            (cx + s * 0.45 * math.cos(a), cy + s * 0.45 * math.sin(a)),
            (cx + s * 0.7 * math.cos(a), cy + s * 0.7 * math.sin(a)),
        ], 1.5)


def _icon_moon(cx, cy, s):
    """Moon / night mode."""
    _arc(cx, cy, s * 0.55, 40, 320, 2)
    _arc(cx + s * 0.35, cy + s * 0.15, s * 0.4, 80, 280, 2)


def _icon_none(cx, cy, s):
    """Empty / no icon."""
    pass


# ─── Icon Registry ────────────────────────────────────────────────

ICONS = {
    # Automotive / Off-Road
    'fan': _icon_fan,
    'lightbar': _icon_lightbar,
    'spotlight': _icon_spotlight,
    'winch': _icon_winch,
    'difflock': _icon_difflock,
    'compressor': _icon_compressor,
    'horn': _icon_horn,
    'headlight': _icon_headlight,
    'siren': _icon_siren,
    'fuel': _icon_fuel,
    'thermometer': _icon_thermometer,
    'battery': _icon_battery,
    'antenna': _icon_antenna,
    'gear': _icon_gear,
    'wrench': _icon_wrench,
    'camera': _icon_camera,
    'speaker': _icon_speaker,
    'plug': _icon_plug,
    'gauge': _icon_gauge,

    # Safety / Status
    'hazard': _icon_hazard,
    'power': _icon_power,
    'lightning': _icon_lightning,
    'lock': _icon_lock,
    'unlock': _icon_unlock,
    'shield': _icon_shield,
    'skull': _icon_skull,
    'radioactive': _icon_radioactive,
    'fire': _icon_fire,
    'water': _icon_water,
    'eye': _icon_eye,

    # Directional
    'arrow_up': _icon_arrow_up,
    'arrow_down': _icon_arrow_down,
    'arrow_left': _icon_arrow_left,
    'arrow_right': _icon_arrow_right,
    'arrows_updown': _icon_arrows_updown,
    'arrows_leftright': _icon_arrows_leftright,
    'compass': _icon_compass,
    'crosshair': _icon_crosshair,

    # Generic
    'on_off': _icon_on_off,
    'check': _icon_check,
    'x_mark': _icon_x_mark,
    'plus': _icon_plus,
    'minus': _icon_minus,
    'star': _icon_star,
    'heart': _icon_heart,
    'circle': _icon_circle,
    'square': _icon_square,
    'triangle': _icon_triangle,
    'diamond': _icon_diamond,
    'clock': _icon_clock,
    'wave': _icon_wave,

    # Nature / Environment
    'mountain': _icon_mountain,
    'tree': _icon_tree,
    'sun': _icon_sun,
    'moon': _icon_moon,

    # Special
    'none': _icon_none,
}


# Organized by category for the icon picker UI
ICON_CATEGORIES = {
    'Automotive': [
        'fan', 'lightbar', 'spotlight', 'headlight', 'winch', 'difflock',
        'compressor', 'horn', 'siren', 'fuel', 'thermometer', 'battery',
        'antenna', 'gear', 'wrench', 'camera', 'speaker', 'plug', 'gauge',
    ],
    'Safety': [
        'hazard', 'power', 'lightning', 'lock', 'unlock', 'shield',
        'skull', 'radioactive', 'fire', 'water', 'eye',
    ],
    'Arrows': [
        'arrow_up', 'arrow_down', 'arrow_left', 'arrow_right',
        'arrows_updown', 'arrows_leftright', 'compass', 'crosshair',
    ],
    'Shapes': [
        'on_off', 'check', 'x_mark', 'plus', 'minus', 'star',
        'heart', 'circle', 'square', 'triangle', 'diamond', 'clock', 'wave',
    ],
    'Nature': [
        'mountain', 'tree', 'sun', 'moon',
    ],
}


def draw_icon(name, cx, cy, size):
    """
    Draw a named icon at center (cx, cy) with given size.

    Must be called inside a canvas context with Color already set.
    Size is the full width/height — the icon draws within ±size/2.

    Usage:
        with self.canvas:
            Color(1, 0.69, 0, 1)
            draw_icon('fan', 100, 200, 32)
    """
    half = size / 2
    func = ICONS.get(name, _icon_none)
    func(cx, cy, half)


def get_icon_names():
    """Return sorted list of all available icon names."""
    return sorted(ICONS.keys())


class IconWidget(Widget):
    """Widget that draws a Canvas icon at its center.

    Set color with set_color() — a Kivy-normalized RGBA tuple.
    """

    def __init__(self, icon_name='power', scale=0.7, **kwargs):
        super().__init__(**kwargs)
        self.icon_name = icon_name
        self.scale = scale
        self._color = (1, 0.69, 0, 1)
        self.bind(size=self._redraw, pos=self._redraw)

    def set_icon(self, name):
        self.icon_name = name
        self._redraw()

    def set_color(self, color):
        self._color = color
        self._redraw()

    def _redraw(self, *args):
        self.canvas.clear()
        with self.canvas:
            KivyColor(*self._color)
            cx = self.x + self.width / 2
            cy = self.y + self.height / 2
            icon_size = min(self.width, self.height) * self.scale
            draw_icon(self.icon_name, cx, cy, icon_size)


def get_icon_count():
    """Return total number of available icons."""
    return len(ICONS)
