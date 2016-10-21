#!/usr/bin/python3

import logging
import tarfile
import io


logger = logging.getLogger(__name__)

def pretty_write(output=[], path="./of/latest", overwrite=True, compress=False):
    """ Pretty print a rule set

    :param output: a list of rules
    :param path: file path to write to
    :param overwrite: overwrite file at path if exists
    :param compress: compress output as tar

    :returns: none
    """
    buff = ""
    for rule in output:
        buff += _rule_to_string(rule) + "\n"
    buff += "<EOF>"

    mode = 'w' if overwrite else 'x'
    logger.info("Writing rules (mode {}, compress = {}) to {}".format(mode, compress, path))
    if compress:
        _tar_write(buff, path+".tar", mode+":bz2")
    else:
        _raw_write(buff, path, mode)

def _rule_to_string(irule):
    """ Wrap a rule into a pretty string

    :param irule: a (rule, support, confidence) tuple

    :returns: a string
    """
    consequent = """{}""".format(irule[0][2][0])
    if len(irule[0][2]) > 1:
        consequent += """\n\tAND  """\
                    + """\n\tAND  """.join(["{}".format(irule[0][2][i])\
                                            for i in range(1, len(irule[0][2]))])

    string = """[{}]
    IF   {}
    THEN {}
    Support:    {:.3f}
    Confidence: {:.3f}\n""".format(irule[0][0],
                              irule[0][1],
                              consequent,
                              irule[1],
                              irule[2])

    return string

def _raw_write(buff, path, mode):
    with open(path, mode) as f:
        f.write(buff)

def _tar_write(buff, path, mode):
    info = tarfile.TarInfo(name="rule_set")
    info.size = len(buff)
    info.type = tarfile.REGTYPE
    with tarfile.open(path, mode) as t:
        t.addfile(tarinfo=info, fileobj=io.BytesIO(buff.encode('utf8')))
