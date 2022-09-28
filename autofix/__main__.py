import argparse
import logging
from typing import Callable

from all_repos import autofix_lib
from all_repos.grep import repos_matching

from . import fixers


def line():
    logging.info("-" * 80)


def arguments():
    parser = argparse.ArgumentParser(usage="python -m autofix")
    autofix_lib.add_fixer_args(parser)

    parser.add_argument(
        "-m",
        "--message",
        dest="message",
        default="apply autofix changes",
        help="git commit message for change",
    )

    parser.add_argument(
        "-b" "--branch",
        dest="branch",
        default="update",
        help="git branch name for change",
    )

    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-g" "--grep",
        dest="grep",
        default=None,
        nargs=2,
        metavar="REGEX FILENAME",
        help="a (regex, file) to use when searching for repos to process",
    )

    parser.add_argument(
        "-f",
        "--fixer",
        dest="fixer",
        default=fixers.base.Fixer,
        choices=fixers.FIXERS.keys(),
        type=lambda v: fixers.FIXERS[v],
        help="The logic to use to fix files",
    )

    return parser.parse_args()


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
        apply_fix=args.fixer.apply,
        check_fix=args.fixer.check,
        autofix_settings=autofix_settings,
    )


if __name__ == "__main__":
    logging.basicConfig(format="%(message)s", level=logging.INFO)
    raise SystemExit(main())
