import locale
from typing import Optional

locale.setlocale(locale.LC_ALL, "")


def bytes_fmt(bytes_opt: Optional[int]) -> str:
    bytes = bytes_opt if bytes_opt else 0
    for unit in ["B", "KiB", "MiB", "GiB", "TiB", "PiB"]:
        if abs(bytes) < 1024:
            size = round(bytes, 2)
            return f"{size} {unit}"
        else:
            bytes /= 1024


def num_fmt(num_opt: Optional[int]) -> str:
    num = num_opt if num_opt else 0
    return f"{num:,}"
