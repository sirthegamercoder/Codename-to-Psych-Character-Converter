from typing import List, Tuple


def parse_indices(indices_str: str) -> List[int]:
    result = []

    if not indices_str:
        return result

    if ".." in indices_str:
        parts = indices_str.split("..")
        if len(parts) == 2:
            try:
                start = int(parts[0].strip())
                end = int(parts[1].strip())
                result.extend(range(start, end + 1))
            except ValueError:
                pass
    elif "," in indices_str:
        parts = indices_str.split(",")
        for part in parts:
            try:
                num = int(part.strip())
                result.append(num)
            except ValueError:
                pass
    else:
        try:
            num = int(indices_str.strip())
            result.append(num)
        except ValueError:
            pass

    return result


def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    hex_color = hex_color.lstrip("#")

    if len(hex_color) == 3:
        hex_color = "".join([c * 2 for c in hex_color])

    try:
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        return (r, g, b)
    except (ValueError, IndexError):
        return (161, 161, 161)
