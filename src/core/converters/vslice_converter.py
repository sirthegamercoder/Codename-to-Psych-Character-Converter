import json
from typing import Dict, Any, Optional

from core.converters.base_converter import BaseConverter


class VSliceConverter(BaseConverter):
    def convert(self, content: str) -> Optional[Dict[str, Any]]:
        try:
            data = json.loads(content)

            if "assetPath" not in data and (
                "animations" not in data or len(data.get("animations", [])) == 0
            ):
                return None

            return self._convert_to_psych(data)

        except json.JSONDecodeError:
            return None

    def _convert_to_psych(self, data: Dict) -> Dict[str, Any]:
        psych_char = {}

        image_path = data.get("assetPath", "")
        if image_path:
            if image_path.startswith("shared:"):
                image_path = image_path[7:]
            psych_char["image"] = image_path
        else:
            anims = data.get("animations", [])
            if anims and len(anims) > 0:
                prefix = anims[0].get("prefix", "")
                if prefix:
                    parts = prefix.split("/")
                    if len(parts) > 1:
                        psych_char["image"] = "/".join(parts[:-1]) + "/" + parts[-1]
                    else:
                        psych_char["image"] = prefix
                else:
                    psych_char["image"] = "characters/bf"
            else:
                psych_char["image"] = "characters/bf"

        psych_char["scale"] = data.get("scale", 1.0)
        psych_char["sing_duration"] = data.get(
            "singTime", data.get("sing_duration", 4.0)
        )

        health_icon = data.get("healthIcon", {})
        if isinstance(health_icon, dict):
            psych_char["healthicon"] = health_icon.get("id", "face")
        else:
            psych_char["healthicon"] = str(health_icon) if health_icon else "face"

        psych_char["position"] = data.get("offsets", data.get("position", [0, 0]))
        if len(psych_char["position"]) < 2:
            psych_char["position"] = [0, 0]

        psych_char["camera_position"] = data.get(
            "cameraOffsets", data.get("camera_position", [0, 0])
        )
        if len(psych_char["camera_position"]) < 2:
            psych_char["camera_position"] = [0, 0]

        psych_char["flip_x"] = data.get("flipX", data.get("flip_x", False))
        psych_char["no_antialiasing"] = data.get(
            "isPixel", data.get("no_antialiasing", False)
        )

        health_colors = data.get("healthbarColors", data.get("healthbar_colors", None))
        if health_colors and len(health_colors) >= 3:
            psych_char["healthbar_colors"] = health_colors[:3]
        else:
            psych_char["healthbar_colors"] = [161, 161, 161]

        psych_char["vocals_file"] = data.get(
            "vocalsFile", data.get("vocals_file", None)
        )

        psych_anims = []
        anims = data.get("animations", [])

        for anim in anims:
            anim_name = anim.get("name", "")
            if not anim_name:
                anim_name = anim.get("anim", "")

            anim_prefix = anim.get("prefix", "")
            if not anim_prefix:
                anim_prefix = anim.get("animation", "")

            fps = anim.get("frameRate", anim.get("fps", 24))
            loop = anim.get("looped", anim.get("loop", False))
            indices = anim.get("frameIndices", anim.get("indices", []))
            offsets = anim.get("offsets", [0, 0])
            if len(offsets) < 2:
                offsets = [0, 0]

            psych_anims.append(
                {
                    "anim": anim_name,
                    "name": anim_prefix,
                    "fps": fps,
                    "loop": loop,
                    "indices": indices,
                    "offsets": [int(offsets[0]), int(offsets[1])],
                }
            )

        psych_char["animations"] = psych_anims

        return psych_char
