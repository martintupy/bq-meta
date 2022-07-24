import locale

locale.setlocale(locale.LC_ALL, "")


def bytes_fmt(bytes: int) -> str:
    for unit in ["B", "KiB", "MiB", "GiB", "TiB", "PiB"]:
        if abs(bytes) < 1024:
            size = round(bytes, 1)
            return f"{size} {unit}"
        else:
            bytes /= 1024


def num_fmt(num: int) -> str:
    return f"{num:,}"
