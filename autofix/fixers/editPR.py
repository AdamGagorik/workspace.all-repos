import functools
import json
import logging
import subprocess

from autofix import CONFIG

from .base import Fixer as Base


@functools.lru_cache(maxsize=1)
def get_label_lut() -> dict:
    def _():
        with CONFIG.joinpath("labels.json").open("r") as stream:
            for key, values in json.load(stream).items():
                yield key, key
                for alias in values["alias"]:
                    yield alias, key

    return dict(_())


class Fixer(Base):
    def apply(self):
        try:
            # fmt: off
            url = (
                self._run_command(
                    "GITHUB PR LIST",
                    "gh", "pr", "list",
                    "--head", f"{self.options.branch}",
                    "--json", "url", "--limit", "1",
                    "--jq", ".[0].url",
                    force=True,
                )
                .decode("utf-8")
                .strip()
            )
            # fmt: on
        except subprocess.CalledProcessError:
            logging.error("can not find PR with branch for repo")
            return

        if not url.strip():
            logging.error("can not find PR with branch for repo")
            return

        # fmt: off
        self._run_command(
            "GITHUB PR EDIT",
            "gh", "pr", "edit", url,
            *self._prepend("--add-label", *(get_label_lut()[label] for label in self.options.labels)),
            *self._prepend("--add-assignee", *self.options.assignees),
            *self._prepend("--add-reviewer", *self.options.reviewers),
            force=self.options.force,
        )
        # fmt: on

    @staticmethod
    def _prepend(key: str, *values: str):
        for value in values:
            yield key
            yield value

    @staticmethod
    def _run_command(kind, *command, force: bool = False):
        logging.debug("[%-12s]: %s", kind.upper(), " ".join(command))
        if force:
            return subprocess.check_output(command)

    @classmethod
    def args(cls, **kwargs):
        group, parser = super().args(**kwargs)

        group.add_argument(
            "--add-label",
            dest="labels",
            action="append",
            default=[],
            choices=tuple(get_label_lut().keys()),
            metavar="str",
            help="see gh pr edit --help",
        )

        group.add_argument(
            "--add-assignee", dest="assignees", action="append", default=[], metavar="str", help="see gh pr edit --help"
        )

        group.add_argument(
            "--add-reviewer", dest="reviewers", action="append", default=[], metavar="str", help="see gh pr edit --help"
        )

        return group, parser


if __name__ == "__main__":
    raise SystemExit(Fixer.main())
