#!/usr/bin/python3

import logging
from rdflib.term import Literal
from writers.auxiliarly import get_label


logger = logging.getLogger(__name__)

LANG = "nl"
FALLBACK_TO_DEFAULT = True

def transcribe(irule, abox=None, tbox=None, vocab=None):
    """ Transcribe a rule in natural language (Dutch)

    :param irule: a (rule, support, confidence) tuple
    :param abox: assertional data used during transcribing
    :param tbox: schema data used during transcribing
    :param vocab: controlled vocabulary used during transcribing

    :returns: a string
    """
    string = "Voor ieder(e) {} geldt: als {} ".format(
        get_label(irule.rule.ctype, [tbox], LANG, FALLBACK_TO_DEFAULT),
        get_label(irule.rule.antecedent[0], [tbox], LANG, FALLBACK_TO_DEFAULT))
    if type(irule.rule.antecedent[1]) is Literal:
        string += "'{}', ".format(irule.rule.antecedent[1].toPython())
    else:
        string += "{}, ".format(get_label(irule.rule.antecedent[1], [abox, vocab], LANG, FALLBACK_TO_DEFAULT))

    string += "dan {} ".format(
        get_label(irule.rule.consequent[0][0], [tbox], LANG, FALLBACK_TO_DEFAULT))
    if type(irule.rule.consequent[0][1]) is Literal:
        string += "'{}'".format(irule.rule.consequent[0][1].toPython())
    else:
        string += "{}".format(get_label(irule.rule.consequent[0][1], [abox, vocab], LANG, FALLBACK_TO_DEFAULT))

    for i in range(1, len(irule.rule.consequent)):
        string += ", en {} ".format(
            get_label(irule.rule.consequent[i][0], [tbox], LANG, FALLBACK_TO_DEFAULT))
        if type(irule.rule.consequent[i][1]) is Literal:
            string += "'{}'".format(irule.rule.consequent[i][1].toPython())
        else:
            string += "{}".format(get_label(irule.rule.consequent[i][1], [abox, vocab], LANG, FALLBACK_TO_DEFAULT))

    return string + "."
