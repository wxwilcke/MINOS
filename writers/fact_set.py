#!/usr/bin/python3

import logging
from writers.auxiliarly import write


logger = logging.getLogger(__name__)

def pretty_write(output=[], path="./of/latest", overwrite=True, compress=False):
    """ Pretty print a fact set

    :param output: a list of facts
    :param path: file path to write to
    :param overwrite: overwrite file at path if exists
    :param compress: compress output as tar

    :returns: none
    """

    write(output, path, overwrite, compress, _fact_to_string)

def _fact_to_string(fact):
    """ Wrap a fact into a pretty string

    :param fact: a (subject, predicate, [object(s)]) tuple

    :returns: a string
    """
    n = len(fact[2])
    objs = "NULL"

    if n > 0:
        objs = """{}""".format(fact[2][0])
        if len(fact[2]) > 1:
            objs += """\n\t   """\
                 + """\n\t   """.join(["{}".format(fact[2][i])\
                                      for i in range(1, n)])

    string = """[S]  {}
[P]  {}
[O]  {}\n""".format(fact[0],
                    fact[1],
                    objs)

    return string
