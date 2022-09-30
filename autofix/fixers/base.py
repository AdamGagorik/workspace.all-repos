import argparse
import dataclasses
import logging


@dataclasses.dataclass()
class Fixer:
    options: argparse.Namespace

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
        fixer = cls(options=cls.args().parse_args(args=argv))
        fixer.apply()
        fixer.check()


if __name__ == "__main__":
    raise SystemExit(Fixer.main())
