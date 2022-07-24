import subprocess
import tempfile
from typing import List

import click
from rich.console import Console

from bq_meta import const


def _run_fzf(choices: List[str]) -> List[str]:
    # choices.sort(reverse=True)
    choices_str = "\n".join(map(str, choices))
    selection = []
    fzf_args = filter(None, ["fzf", "--ansi"])
    with tempfile.NamedTemporaryFile() as input_file:
        with tempfile.NamedTemporaryFile() as output_file:
            input_file.write(choices_str.encode("utf-8"))
            input_file.flush()
            cat = subprocess.Popen(["cat", input_file.name], stdout=subprocess.PIPE)
            subprocess.run(fzf_args, stdin=cat.stdout, stdout=output_file)
            cat.wait()
            with open(output_file.name) as f:
                selection = [line.strip("\n") for line in f.readlines()]
    return selection


def pick_one(choices: List[str], console: Console) -> str:
    result = next(iter(_run_fzf(choices)), None)
    if result:
        return result
    else:
        console.print("Aborted", style=const.error_style)
        ctx = click.get_current_context()
        ctx.exit()
