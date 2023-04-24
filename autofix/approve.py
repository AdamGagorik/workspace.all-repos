import json
import os
import pathlib
import subprocess
from itertools import chain, repeat
from typing import Any, Callable


def ask(
    prompt: str, error: str = "error! answer y or n", valid: Callable[[str], bool] = lambda s: s in {"y", "n"}
) -> str:
    prompt = f"{prompt.strip()} "
    answers = map(input, chain([prompt], repeat("\n".join([error, prompt]))))
    return next(filter(valid, answers))


def run(*cmd: str, default: Any = False, output: bool = False):
    try:
        return subprocess.run([str(c) for c in cmd], check=True, capture_output=output)
    except subprocess.CalledProcessError as e:
        print(e.stderr)
        return default


WORK = pathlib.Path.cwd()
REPOS = [p for p in WORK.joinpath("repos", "syapse").glob("*") if p.is_dir()]
for REPO in REPOS:
    os.chdir(WORK)
    os.chdir(REPO)

    PULLS = run("gh", "pr", "list", "--search", "Bump OR automatic", "--json", "number,title", default=[], output=True)
    PULLS = json.loads(PULLS.stdout.decode("utf-8").strip())

    for i, PULL in enumerate(PULLS):
        if i == 0:
            print(f" {REPO.name} ".center(120 - 2, "*"))
        else:
            print("-" * 120)

        N, T = PULL["number"], PULL["title"]

        print(f">>> {T}")
        match ask("PR OK?"):
            case "y":
                if run("gh", "pr", "review", "--approve", N).returncode == 0:
                    match ask("merge?"):
                        case "y":
                            run("gh", "pr", "merge", "--squash", "--auto", "--delete-branch", N)

    os.chdir(WORK)
