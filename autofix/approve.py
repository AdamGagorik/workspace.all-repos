import argparse
import json
import os
import pathlib
import subprocess
from collections.abc import Iterator
from functools import partial
from itertools import chain, repeat
from typing import Any, Callable


def ask(
    prompt: str,
    error: str = "error! answer y or n",
    valid: Callable[[str], bool] = lambda s: s in {"y", "n"},
    always: str | None = None,
) -> str:
    prompt = f"{prompt.strip()} "

    if always is not None:
        print(f"{prompt}{always}")
        if not valid(always):
            raise ValueError("{always} is not a valid answer")
        return always

    answers = map(input, chain([prompt], repeat("\n".join([error, prompt]))))
    return next(filter(valid, answers))


def run(*cmd: str, default: Any = False, output: bool = False):
    try:
        return subprocess.run([str(c) for c in cmd], check=True, capture_output=output)
    except subprocess.CalledProcessError as e:
        print(e.stderr)
        return default


def args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-y", "--yes", action="store_true")
    parser.add_argument("--search", default="Bump OR automatic")
    return parser.parse_args()


def get_pr_status(pull: dict) -> Iterator[tuple[str, str]]:
    for i, check in enumerate(pull["statusCheckRollup"]):
        name = check.get("name", check.get("context", f"check-{i}"))
        try:
            status = check.get("state", check.get("conclusion"))
            yield name, status in {"SUCCESS"}
        except KeyError:
            yield name, False


def main(opts: argparse.Namespace):
    work = pathlib.Path.cwd()
    asker = partial(ask, always="y" if opts.yes else None)
    repos = [p for p in work.joinpath("repos", "syapse").glob("*") if p.is_dir()]
    for REPO in repos:
        os.chdir(work)
        os.chdir(REPO)

        pulls = run(
            "gh",
            "pr",
            "list",
            "--search",
            opts.search,
            "--json",
            "number,title,statusCheckRollup",
            default=[],
            output=True,
        )
        pulls = json.loads(pulls.stdout.decode("utf-8").strip())

        for i, pull in enumerate(pulls):
            if i == 0:
                print(f" {REPO.name} ".center(120 - 2, "*"))
            else:
                print("-" * 120)

            number, title = pull["number"], pull["title"]
            status = dict(get_pr_status(pull))
            for check, state in status.items():
                print(f">>> [{int(state)}] {check}")

            print(f">>> {title}")
            if not all(status.values()):
                print(">>> missing status checks!")
                match asker("... open PR?"):
                    case "y":
                        run("gh", "pr", "view", "--web", number)
                continue

            match asker("... PR OK?"):
                case "y":
                    if run("gh", "pr", "review", "--approve", number).returncode == 0:
                        match asker("... merge?"):
                            case "y":
                                run("gh", "pr", "merge", "--squash", "--auto", "--delete-branch", number)

        os.chdir(work)


if __name__ == "__main__":
    main(opts=args())
