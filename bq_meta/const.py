from pathlib import Path
import os
import yaml
from rich.style import Style
from rich.theme import Theme

DEFAULT_BQ_META_HOME = f"{Path.home()}/.config/bq-meta"

BQ_META_HOME = os.getenv("BQ_META_HOME", DEFAULT_BQ_META_HOME)
BQ_META_CONFIG = f"{BQ_META_HOME}/config.yaml"
BQ_META_PROJECTS = f"{BQ_META_HOME}/projects"

BQ_META_DISABLE_COLORS = os.getenv("BQ_META_DISABLE_COLORS", "False").lower() in ("true", "1", "t")
BQ_META_SKIN = os.getenv("BQ_META_SKIN")

default_skin = {
    "request": "gold3",
    "info": "green4",
    "error": "red",
    "border": "grey27",
    "time": "yellow",
    "darker": "grey46",
    "alternate": "grey50",
    "link": "light_sky_blue1",
    "keyword": "dodger_blue1",
}

skin = default_skin

if BQ_META_SKIN and os.path.isfile(BQ_META_SKIN):
    BQ_META_skin = yaml.safe_load(open(BQ_META_SKIN, "r"))
    skin = {**skin, **BQ_META_skin}

request_style = Style(color=skin["request"])
info_style = Style(color=skin["info"])
error_style = Style(color=skin["error"])
border_style = Style(color=skin["border"])
time_style = Style(color=skin["time"])
darker_style = Style(color=skin["darker"])
alternate_style = Style(color=skin["alternate"])
link_style = Style(color=skin["link"])
keyword_style = Style(color=skin["keyword"])

theme = Theme(
    {
        "progress.elapsed": darker_style,
        "prompt.default": darker_style,
        "prompt.choices": "default",
        "rule.line": border_style,
        "repr.path": darker_style,
        "repr.filename": darker_style,
        "status.spinner": "none",
        "progress.spinner": "none",
        "repr.number": "none",
        "tree.line": border_style,
    }
)

FZF_SEPARATOR = " ~ "
