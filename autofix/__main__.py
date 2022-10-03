import argparse
import logging
from typing import Callable

from all_repos import autofix_lib
from all_repos.grep import repos_matching

import autofix.fixers.base
import autofix.fixers.labels
import autofix.fixers.syncfile


# noinspection SpellCheckingInspection
FIXERS = {
    "base": autofix.fixers.base.Fixer,
    "labels": autofix.fixers.labels.Fixer,
    "syncfile": autofix.fixers.syncfile.Fixer,
}


def line():
    logging.info("-" * 80)


def arguments():
    parser = argparse.ArgumentParser(
        usage="python -m autofix",
        add_help=False,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    autofix_lib.add_fixer_args(parser)

    autofix_group = parser.add_argument_group("autofix")
    autofix_group.add_argument(
        "-m",
        "--message",
        dest="message",
        default="apply autofix changes",
        help="git commit message for change",
    )

    autofix_group.add_argument(
        "-b",
        "--branch",
        dest="branch",
        default="update",
        help="git branch name for change",
    )

    discover_group = autofix_group.add_mutually_exclusive_group()
    discover_group.add_argument(
        "-g",
        "--grep",
        dest="grep",
        default=None,
        nargs=2,
        metavar="REGEX FILENAME",
        help="a (regex, file) to use when searching for repos to process",
    )

    autofix_group.add_argument(
        "-f",
        "--fixer",
        dest="fixer",
        default="base",
        choices=FIXERS.keys(),
        help="The logic to use to fix files",
    )

    args, remaining = parser.parse_known_args()
    args = FIXERS[args.fixer].args(parents=[parser], usage=parser.usage)[-1].parse_args()

    return args


class Find:
    @staticmethod
    def matching(pattern="", obj=".pre-commit-config.yaml") -> Callable:
        return lambda config: repos_matching(config, (pattern, "--", obj))


def main():
    # Get Arguments
    args = arguments()

    # Create finder
    if args.grep:
        find_repos = Find.matching(*args.grep)
    else:
        find_repos = Find.matching()

    # Setup configuration
    repos, config, commit, autofix_settings = autofix_lib.from_cli(
        args,
        find_repos=find_repos,
        msg=args.message,
        branch_name=args.branch,
    )

    # Debug configuration
    line()
    for repo in repos:
        logging.info("found repo: %s", repo)

    line()
    logging.info("git author: %s", commit.author)
    logging.info("git branch: %s", commit.branch_name)
    logging.info("commit msg: %s", commit.msg)
    line()

    if input("Continue? [y/n]: ").lower() not in {"y", "yes"}:
        logging.warning("aborting...")
        return

    # Apply fixes
    autofix_lib.fix(
        repos,
        config=config,
        commit=commit,
        apply_fix=FIXERS[args.fixer](options=args).apply,
        check_fix=FIXERS[args.fixer](options=args).check,
        autofix_settings=autofix_settings,
    )


if __name__ == "__main__":
    logging.basicConfig(format="%(message)s", level=logging.INFO)
    raise SystemExit(main())
