#!/usr/bin/python3

import logging
from rdflib.term import Literal
from writers.auxiliarly import write


logger = logging.getLogger(__name__)

def pretty_write(output, path="./of/latest", overwrite=True, compress=False):
    """ Pretty print a rule set

    :param output: a list of rules
    :param path: file path to write to
    :param overwrite: overwrite file at path if exists
    :param compress: compress output as tar

    :returns: none
    """

    write(output.model, path, overwrite, compress, _rule_to_string)

def _rule_to_string(irule):
    """ Wrap a rule into a pretty string

    :param irule: a (rule, support, confidence) tuple

    :returns: a string
    """
    consequent = """{}""".format(_statement_to_string(irule.rule.consequent[0]))
    if len(irule.rule.consequent) > 1:
        consequent += """\n\tAND  """\
                    + """\n\tAND  """.join(["{}".format(_statement_to_string(irule.rule.consequent[i]))\
                                            for i in range(1, len(irule.rule.consequent))])

    string = """[{}]
    IF   {}
    THEN {}
    Support:    {:.3f}
    Confidence: {:.3f}\n""".format(irule.rule.ctype,
                              _statement_to_string(irule.rule.antecedent),
                              consequent,
                              irule.support.value,
                              irule.confidence.value)

    return string

def _statement_to_string(statement):
    left = statement[0].toPython()
    right = statement[1].toPython()

    if type(statement[1]) is Literal:
        if statement[1].language is not None:
            right += " [rdf:lang={}]".format(statement[1].language)
        elif statement[1].datatype is not None:
            right += " [rdf:datatype={}]".format(statement[1].datatype)

    return (left, right)
