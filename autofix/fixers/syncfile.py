import argparse
import logging
import os.path
import shutil

from .base import Fixer as Base


class Fixer(Base):
    def apply(self):
        for inp_path, out_path in map(lambda v: v.split(":"), self.options.sync):
            if not os.path.exists(inp_path):
                raise FileNotFoundError(inp_path)

            if not os.path.exists(out_path) and not self.options.create:
                logging.error("[SKIP]: out path does not exist! use --create : %s", out_path)
                continue

            if self.options.force:
                logging.info("cp %s %s", inp_path, out_path)
                shutil.copy(inp_path, out_path)
            else:
                logging.error("skipping logic! use --force : cp %s %s", inp_path, out_path)

    @classmethod
    def args(cls) -> argparse.ArgumentParser:
        parser = super().args()
        parser.add_argument("--create", action="store_true", help="create file is missing?")
        parser.add_argument("--sync", nargs="*", required=True, help="the file to sync")
        return parser


if __name__ == "__main__":
    raise SystemExit(Fixer.main())
