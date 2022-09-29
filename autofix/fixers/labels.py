import argparse
import json
import logging
import subprocess
from collections.abc import Iterator

from .base import Fixer as Base


LABELS = {
    "bug": {
        "description": "Something isn't working correctly",
        "color": "#d73a4a",
        "alias": [],
    },
    "documentation": {
        "description": "Improvements to the documentation",
        "color": "#D4C5F9",
        "alias": [],
    },
    "enhancement": {
        "description": "New features or algorithm changes",
        "color": "#BFDADC",
        "alias": ["enhancements"],
    },
    "configs": {
        "description": "Configuration related changes",
        "color": "#2EAB76",
        "alias": [],
    },
    "testing": {
        "description": "Unit test related changes",
        "color": "#F9D0C4",
        "alias": [],
    },
    "refactoring": {
        "description": "Code changes without behavior changes",
        "color": "#BFD4F2",
        "alias": [],
    },
    "⚠️ DoNotMerge": {
        "description": "Do not merge this pull request yet!",
        "color": "#3A3D46",
        "alias": ["DoNotMerge"],
    },
    "🚧 REBUILD": {
        "description": "The docker image or environment must be rebuilt",
        "color": "#3A3D46",
        "alias": ["REBUILD"],
    },
    "dependencies": {
        "description": "Pull requests that update a dependency file",
        "color": "#1D76DB",
        "alias": [],
    },
    "GitHubAction": {
        "description": "Pull requests that update GitHub Actions CI/CD",
        "color": "#555555",
        "alias": ["github_actions"],
    },
    "Python": {
        "description": "Pull requests that update Python dependencies",
        "color": "#555555",
        "alias": ["python"],
    },
    "CI/CD": {
        "description": "Updates to continuous integration or delivery",
        "color": "#FBCA04",
        "alias": [],
    },
    "wontfix": {
        "description": "Will not fix",
        "color": "#ffffff",
        "alias": [],
    },
}


def fetch() -> dict:
    """
    Download existing labels.
    """
    stdout = subprocess.check_output(["gh", "label", "list", "--json", "name,color,description"]).decode("utf-8")
    return json.loads(stdout)


class CommandGenerator:
    """
    Generate gh commands to apply.
    """

    OPS = ("skip", "rename", "color", "description", "delete", "create")

    @classmethod
    def commands(cls, *existing: dict) -> Iterator[tuple[str, dict]]:
        """
        Examine the existing labels and generate the commands to apply.
        """
        yield from sorted(cls._generate_commands(*existing), key=lambda x: (cls.OPS.index(x[0]), x[1]["new_name"]))

    @classmethod
    def _generate_commands(cls, *existing: dict) -> Iterator[tuple[str, dict]]:
        """
        The underlying logic to generate the commands.
        """
        old_used = set()
        new_used = set()
        for old_data in existing:
            old_name = old_data["name"]

            # skip
            if old_name in LABELS:
                new_name = old_name
                old_used.add(old_name)
                new_used.add(new_name)
                yield "skip", dict(old_name=old_name, new_name=new_name)
                yield from cls._generate_label_property_commands(new_name, old_data, LABELS[old_name])

            # rename
            else:
                for new_name, new_data in LABELS.items():
                    if old_name in new_data["alias"]:
                        old_used.add(old_name)
                        new_used.add(new_name)
                        yield "rename", dict(old_name=old_name, new_name=new_name)
                        yield from cls._generate_label_property_commands(new_name, old_data, new_data)
                        break

        for old_data in existing:
            old_name = old_data["name"]
            if old_name not in old_used:
                new_name = old_name
                old_used.add(old_name)
                new_used.add(new_name)
                yield "delete", dict(old_name=old_name, new_name=new_name)

        for new_name, new_data in LABELS.items():
            if new_name not in new_used:
                old_name = new_name
                old_used.add(old_name)
                new_used.add(new_name)
                yield "create", dict(
                    old_name=old_name, new_name=new_name, new_color=new_data["color"], new_desc=new_data["description"]
                )

    @classmethod
    def _generate_label_property_commands(
        cls, new_name: str, old_data: dict, new_data: dict
    ) -> Iterator[tuple[str, dict]]:
        """
        Specifically generate commands to change label properties on already renamed labels.
        """
        if old_data["color"].lstrip("#").lower() != new_data["color"].lstrip("#").lower():
            yield "color", dict(new_name=new_name, old_color=old_data["color"], new_color=new_data["color"])

        if old_data["description"] != new_data["description"]:
            yield "description", dict(
                new_name=new_name, old_desc=old_data["description"], new_desc=new_data["description"]
            )


class Fixer(Base):
    def apply(self):
        existing = fetch()
        for kind, data in CommandGenerator.commands(*existing):
            if kind == "create":
                if self.force:
                    color, description = data["new_color"].lstrip("#"), data["new_desc"]
                    self._run_command(
                        kind, "gh", "label", "create", data["old_name"], "--description", description, "--color", color
                    )

            elif kind == "delete":
                if self.force:
                    self._run_command(kind, "gh", "label", "delete", data["old_name"], "--confirm")

            elif kind == "rename":
                self._run_command(kind, "gh", "label", "edit", data["old_name"], "--name", data["new_name"])

            elif kind == "color":
                color = data["new_color"].lstrip("#")
                self._run_command(kind, "gh", "label", "edit", data["new_name"], "--color", color)

            elif kind == "description":
                description = data["new_desc"]
                self._run_command(kind, "gh", "label", "edit", data["new_name"], "--description", description)

    def _run_command(self, kind, *command):
        logging.debug("[%-12s]: %s", kind.upper(), " ".join(command))
        if self.force:
            subprocess.check_call(command)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true")
    opts = parser.parse_args()
    fixer = Fixer(force=opts.force)
    fixer.apply()
    fixer.check()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format="%(message)s")
    raise SystemExit(main())
