import subprocess
import tempfile
from rich.live import Live
from typing import List, Optional


def _run_fzf(choices: List[str], live: Optional[Live]) -> List[str]:
    choices.reverse()  # reverse order when searching - from bottom to top
    choices_str = "\n".join(choices)
    selection = []
    if live:
        live.stop()
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
    if live:
        live.start()
    return selection


def pick_one(choices: List[str], live: Optional[Live]) -> Optional[str]:
    result = next(iter(_run_fzf(choices, live)), None)
    return result
