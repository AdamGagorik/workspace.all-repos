import argparse
import dataclasses
import logging


@dataclasses.dataclass()
class Fixer:
    force: bool = False

    def apply(self):
        ...

    def check(self, **kwargs):
        ...

    @classmethod
    def args(cls) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(description=cls.__doc__)
        parser.add_argument("--force", action="store_true")
        return parser

    @classmethod
    def main(cls, argv=None):
        logging.basicConfig(level=logging.DEBUG, format="%(message)s")
        opts = cls.args().parse_args(args=argv)
        fixer = cls(force=opts.force)
        fixer.apply()
        fixer.check()


if __name__ == "__main__":
    raise SystemExit(Fixer.main())
