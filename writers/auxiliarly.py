#!/usr/bin/python3

import logging
import tarfile
import io
import re


logger = logging.getLogger(__name__)

def write(output=[], path="./of/latest", overwrite=True, compress=False, printer=None, abox=None, tbox=None, vocab=None):
    """ Write a list of items

    :param output: a list of items
    :param path: file path to write to
    :param overwrite: overwrite file at path if exists
    :param compress: compress output as tar

    :returns: none
    """
    buff = ""
    for item in output:
        buff += printer(item, abox, tbox, vocab) + "\n"
    buff += "<EOF>"

    mode = 'w' if overwrite else 'x'
    logger.info("Writing (mode {}, compress = {}) to {}".format(mode, compress, path))
    if compress:
        _tar_write(buff, path+".tar", mode+":bz2")
    else:
        _raw_write(buff, path, mode)

def _raw_write(buff, path, mode):
    with open(path, mode) as f:
        f.write(buff)

def _tar_write(buff, path, mode):
    info = tarfile.TarInfo(name=re.match('.*/(.*).tar', path).group(1))
    info.size = len(buff)
    info.type = tarfile.REGTYPE
    with tarfile.open(path, mode) as t:
        t.addfile(tarinfo=info, fileobj=io.BytesIO(buff.encode('utf8')))
