import logging
import os


class Fixer:
    @staticmethod
    def apply():
        logging.info("apply fix for %s", os.getcwd())

    @staticmethod
    def check(**kwargs):
        logging.info("check fix for %s", os.getcwd())
