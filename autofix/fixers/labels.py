import json
import logging
import subprocess

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
        "alias": [],
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
        "alias": [],
    },
    "🚧 REBUILD": {
        "description": "The docker image or environment must be rebuilt",
        "color": "#3A3D46",
        "alias": [],
    },
    "dependencies": {
        "description": "Pull requests that update a dependency file",
        "color": "#1D76DB",
        "alias": [],
    },
    "GitHubAction": {
        "description": "Pull requests that update GitHub Actions CI/CD",
        "color": "#555555",
        "alias": [],
    },
    "Python": {
        "description": "Pull requests that update Python dependencies",
        "color": "#555555",
        "alias": [],
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
    stdout = subprocess.check_output(["gh", "label", "list", "--json", "name,color,description"]).decode("utf-8")
    return json.loads(stdout)


def remap(existing, **candidates):
    for old_data in existing:
        old_name = old_data["name"]
        for new_name, new_data in candidates.items():
            packet = dict(old_name=old_name, new_name=new_name)

            if old_name == new_name:
                yield "skip", packet | {}
                candidates.pop(new_name)
            elif old_name in new_data["alias"] or old_name.lower() == new_name.lower():
                yield "rename", packet | {}
                candidates.pop(new_name)
            else:
                yield "delete", packet | {}
                continue

            if old_data["color"] not in new_data["color"]:
                yield "color", packet | dict(old_color=old_data["color"], new_color=new_data["color"])

            if old_data["description"] != new_data["description"]:
                yield "description", packet | dict(old_desc=old_data["description"], new_desc=new_data["description"])

            break
        else:
            raise RuntimeError(f"can not map {old_name}")


OPS = ("skip", "delete", "rename", "color", "description")


class Fixer(Base):
    @staticmethod
    def apply():
        existing = fetch()
        for command, data in sorted(remap(existing, **LABELS), key=lambda x: (OPS.index(x[0]), x[1]["new_name"])):
            logging.info("%s %s", command, data)

            if command == "delete":
                raise NotImplementedError

            elif command == "rename":
                name = data["new_name"]
                subprocess.check_call(["gh", "label", "edit", data["new_name"], "--name", f"{name}"])

            elif command == "color":
                color = data["new_color"].lstrip("#")
                subprocess.check_call(["gh", "label", "edit", data["new_name"], "--color", f"{color}"])

            elif command == "description":
                description = data["new_desc"]
                subprocess.check_call(["gh", "label", "edit", data["new_name"], "--description", f"{description}"])


def main():
    Fixer.apply()
    Fixer.check()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    raise SystemExit(main())
