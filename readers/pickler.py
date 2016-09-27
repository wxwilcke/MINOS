#!/usr/bin/python3

import logging
import pickle


logger = logging.getLogger(__name__)

def read(path="./of/latest.pickle"):
    """ Read pickle dump

    :param path: file path to read from

    :returns: unpickled construct
    """
    mode = 'rb'

    logger.info("Loading dumped pickle (mode {}) from {}".format(mode, path))

    unpickled = None
    with open(path, mode) as f:
        unpickled = pickle.load(f)

    return unpickled
