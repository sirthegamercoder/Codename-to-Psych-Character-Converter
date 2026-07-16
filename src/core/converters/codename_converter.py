from typing import Dict, List, Optional, Any, Tuple

from lxml import etree

from core.converters.base_converter import BaseConverter
from utils.helpers import parse_indices, hex_to_rgb


class CodenameConverter(BaseConverter):
    """Converter for Codename Engine XML character files."""

    def convert(self, content: str) -> Optional[Dict[str, Any]]:
        try:
            root = etree.fromstring(content.encode("utf-8"))

            if root.tag != "character":
                return None

            char_data = {
                "x": self._get_float_att(root, "x", 0),
                "y": self._get_float_att(root, "y", 0),
                "sprite": self._get_string_att(root, "sprite", "characters/BOYFRIEND"),
                "scale": self._get_float_att(root, "scale", 1),
                "camx": self._get_float_att(root, "camx", 0),
                "camy": self._get_float_att(root, "camy", 0),
                "icon": self._get_string_att(root, "icon", "face"),
                "holdTime": self._get_float_att(root, "holdTime", 4),
                "flipX": self._get_bool_att(root, "flipX", False),
                "animations": [],
            }

            color_hex = self._get_string_att(root, "color", "#A1A1A1")
            rgb_color = hex_to_rgb(color_hex)

            for anim_node in root.findall("anim"):
                anim_name = self._get_string_att(anim_node, "name", "")
                anim_anim = self._get_string_att(anim_node, "anim", "")
                anim_x = self._get_float_att(anim_node, "x", 0)
                anim_y = self._get_float_att(anim_node, "y", 0)
                anim_fps = int(self._get_float_att(anim_node, "fps", 24))
                anim_loop = self._get_bool_att(anim_node, "loop", False)
                indices_str = self._get_string_att(anim_node, "indices", None)

                char_data["animations"].append(
                    {
                        "name": anim_name,
                        "anim": anim_anim,
                        "x": anim_x,
                        "y": anim_y,
                        "fps": anim_fps,
                        "loop": anim_loop,
                        "indices": indices_str,
                    }
                )

            return self._convert_to_psych(char_data, rgb_color)

        except etree.XMLSyntaxError:
            return None

    def _convert_to_psych(
        self, data: Dict, rgb_color: Tuple[int, int, int]
    ) -> Dict[str, Any]:
        psych_anims = []

        for anim in data["animations"]:
            indices = []
            if anim.get("indices"):
                indices = parse_indices(anim["indices"])

            psych_anims.append(
                {
                    "anim": anim["name"],
                    "name": anim["anim"],
                    "fps": anim["fps"],
                    "loop": anim["loop"],
                    "indices": indices,
                    "offsets": [int(anim["x"]), int(anim["y"])],
                }
            )

        return {
            "animations": psych_anims,
            "image": "characters/" + data["sprite"],
            "scale": data["scale"],
            "sing_duration": data["holdTime"],
            "healthicon": data["icon"],
            "position": [data["x"], data["y"]],
            "camera_position": [data["camx"], data["camy"]],
            "flip_x": data["flipX"],
            "no_antialiasing": False,
            "healthbar_colors": list(rgb_color),
            "vocals_file": None,
        }

    def _get_float_att(self, element, name: str, default: float) -> float:
        value = element.get(name)
        if value is None:
            return default
        try:
            return float(value)
        except ValueError:
            return default

    def _get_string_att(self, element, name: str, default: str) -> str:
        return element.get(name, default)

    def _get_bool_att(self, element, name: str, default: bool) -> bool:
        value = element.get(name)
        if value is None:
            return default
        return value.lower() in ["true", "1", "yes"]
