import logging
import os.path
import pathlib
import shutil
import subprocess

from .base import Fixer as Base


class Fixer(Base):
    def apply(self):
        assert len(self.options.src) == len(self.options.dst), "inputs not in pairs"

        for inp_path, out_path in zip(self.options.src, self.options.dst):
            inp_path = inp_path.absolute()
            out_path = out_path.absolute()

            if not os.path.exists(inp_path):
                raise FileNotFoundError(inp_path)

            if not os.path.exists(out_path) and not self.options.allow_missing:
                logging.error("[SKIP]: out path does not exist! use --create : %s", out_path)
                continue

            if self.options.force:
                logging.info("cp %s %s", inp_path, out_path)
                shutil.copy(inp_path, out_path)
                subprocess.check_call(["git", "add", out_path])
            else:
                logging.error("skipping logic! use --force : cp %s %s", inp_path, out_path)

    @classmethod
    def args(cls, **kwargs):
        group, parser = super().args(**kwargs)
        group.add_argument("--allow-missing", action="store_true", help="create file if missing?")
        group.add_argument("--src", nargs="*", metavar="SRC", type=lambda p: pathlib.Path(p).absolute(), help="input")
        group.add_argument("--dst", nargs="*", metavar="DST", type=pathlib.Path, help="output")
        return group, parser


if __name__ == "__main__":
    raise SystemExit(Fixer.main())
