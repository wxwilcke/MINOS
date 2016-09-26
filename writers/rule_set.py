#!/usr/bin/python3

import logging


logger = logging.getLogger(__name__)

def pretty_write(output=[], path="./of/latest", overwrite=True):
    """ Pretty print a rule set

    :param output: a list of rules
    :param path: file path to write to
    :param overwrite: overwrite file at path if exists

    :returns: none
    """
    mode = 'w' if overwrite else 'x'

    logger.info("Writing rules mode {} to {}".format(mode, path))

    with open(path, mode) as f:
        for rule in output:
            f.write(_rule_to_string(rule)+"\n")

        f.write("<EOF>")

def _rule_to_string(irule):
    """ Wrap a rule into a pretty string

    :param irule: a (rule, support, confidence) tuple

    :returns: a string
    """
    consequent = """{}""".format(irule.rule.consequent[0])
    if len(irule.rule.consequent) > 1:
        consequent += """\n\tAND  """\
                    + """\n\tAND  """.join(["{}".format(irule.rule.consequent[i])\
                                            for i in range(1, len(irule.rule.consequent))])

    string = """[{}]
    IF   {}
    THEN {}
    Support:    {:.3f}
    Confidence: {:.3f}\n""".format(irule.rule.ctype,
                              irule.rule.antecedent,
                              consequent,
                              irule.support,
                              irule.confidence)

    return string
