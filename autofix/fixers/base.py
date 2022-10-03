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
    def args(cls, **kwargs):
        parser = argparse.ArgumentParser(
            **(dict(usage=f"python -m {cls.__module__}", formatter_class=argparse.RawDescriptionHelpFormatter) | kwargs)
        )
        group = parser.add_argument_group(f"{cls.__module__}")
        group.add_argument("--apply-changes", dest="force", action="store_true", help="actually apply changes?")
        return group, parser

    @classmethod
    def main(cls, argv=None):
        logging.basicConfig(level=logging.DEBUG, format="%(message)s")
        fixer = cls(options=cls.args()[-1].parse_args(args=argv))
        fixer.apply()
        fixer.check()


if __name__ == "__main__":
    raise SystemExit(Fixer.main())
