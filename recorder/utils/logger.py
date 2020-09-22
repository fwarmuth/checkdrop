#!/usr/bin/env python
"""logger.py: function to create a file base logger."""
import logging


def create_logger(name: str, level = logging.INFO):
    # setup
    log = logging.getLogger(name)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_logging_handler = logging.StreamHandler()
    console_logging_handler.setFormatter(formatter)
    log.addHandler(console_logging_handler)
    log.setLevel(level)

    # return it
    return log
