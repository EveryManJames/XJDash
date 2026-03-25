"""
Skin Manager - Loads and applies visual themes
"""

import json
import os
from typing import Dict, Any, Optional


class SkinManager:
    """
    Manages loading and applying skins (.xjskin files)
    """

    def __init__(self, skins_dir: str = 'skins'):
        """
        Initialize skin manager

        Args:
            skins_dir: Directory containing .xjskin files
        """
        self.skins_dir = skins_dir
        self.current_skin = None
        self.current_skin_data = {}

    def load_skin(self, skin_name: str) -> bool:
        """
        Load a skin by name

        Args:
            skin_name: Skin filename without extension (e.g., 'default_amber')

        Returns:
            True if loaded successfully
        """
        skin_path = os.path.join(self.skins_dir, f"{skin_name}.xjskin")

        if not os.path.exists(skin_path):
            print(f"❌ Skin not found: {skin_path}")
            return False

        try:
            with open(skin_path, 'r') as f:
                self.current_skin_data = json.load(f)

            self.current_skin = skin_name
            print(f"✅ Loaded skin: {self.current_skin_data.get('name', skin_name)}")
            return True

        except Exception as e:
            print(f"❌ Error loading skin: {e}")
            return False

    def get_color(self, color_name: str, default: tuple = (255, 255, 255)) -> tuple:
        """
        Get a color from current skin

        Args:
            color_name: Color key (e.g., 'primary', 'warning')
            default: Default color if not found

        Returns:
            RGB(A) tuple
        """
        colors = self.current_skin_data.get('colors', {})
        color = colors.get(color_name, default)

        # Ensure it's a tuple
        if isinstance(color, list):
            return tuple(color)
        return color

    def get_font(self, font_type: str) -> Dict[str, Any]:
        """
        Get font configuration

        Args:
            font_type: Font key (e.g., 'gauge_numbers', 'labels')

        Returns:
            Font configuration dict with 'family' and 'size'
        """
        fonts = self.current_skin_data.get('fonts', {})
        return fonts.get(font_type, {'family': 'lcd_mono.ttf', 'size': 18})

    def get_background(self) -> Dict[str, Any]:
        """
        Get background configuration

        Returns:
            Background config dict
        """
        return self.current_skin_data.get('background', {'type': 'solid', 'color': [0, 0, 0]})

    def get_gauge_config(self, gauge_name: str) -> Dict[str, Any]:
        """
        Get gauge-specific configuration

        Args:
            gauge_name: Gauge identifier (e.g., 'rpm_gauge', 'temp_gauge')

        Returns:
            Gauge configuration dict
        """
        gauges = self.current_skin_data.get('gauges', {})
        return gauges.get(gauge_name, {})

    def get_effects(self) -> Dict[str, bool]:
        """
        Get visual effects settings

        Returns:
            Effects configuration dict
        """
        return self.current_skin_data.get('effects', {})

    def list_available_skins(self) -> list:
        """
        List all available skins

        Returns:
            List of skin names (without .xjskin extension)
        """
        if not os.path.exists(self.skins_dir):
            return []

        skins = []
        for filename in os.listdir(self.skins_dir):
            if filename.endswith('.xjskin'):
                skins.append(filename[:-7])  # Remove .xjskin extension

        return sorted(skins)

    def get_skin_info(self, skin_name: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata about a skin without loading it

        Args:
            skin_name: Skin filename without extension

        Returns:
            Dict with name, author, version, description
        """
        skin_path = os.path.join(self.skins_dir, f"{skin_name}.xjskin")

        if not os.path.exists(skin_path):
            return None

        try:
            with open(skin_path, 'r') as f:
                data = json.load(f)

            return {
                'name': data.get('name', skin_name),
                'author': data.get('author', 'Unknown'),
                'version': data.get('version', '1.0.0'),
                'description': data.get('description', '')
            }

        except Exception as e:
            print(f"⚠️  Error reading skin info: {e}")
            return None
