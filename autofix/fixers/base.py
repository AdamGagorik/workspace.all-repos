import dataclasses
import logging
import os


@dataclasses.dataclass()
class Fixer:
    force: bool = False

    def apply(self):
        pass

    def check(self, **kwargs):
        pass
