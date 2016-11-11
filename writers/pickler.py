#!/usr/bin/python3

import logging
import pickle


logger = logging.getLogger(__name__)

def write(output, path="./of/latest.pickle", overwrite=True):
    """ Dump via pickle

    :param output: a list of rules
    :param path: file path to write to
    :param overwrite: overwrite file at path if exists

    :returns: none
    """
    mode = 'wb' if overwrite else 'xb'

    logger.info("Dumping pickle (mode {}) to {}".format(mode, path))

    with open(path, mode) as f:
        pickle.dump(output, f)
