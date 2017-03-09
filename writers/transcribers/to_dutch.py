#!/usr/bin/python3

import logging
from writers.transcribers.auxiliarly import get_label


logger = logging.getLogger(__name__)

LANG = "nl"

def transcribe(irule, abox=None, tbox=None, vocab=None):
    """ Transcribe a rule in natural language (Dutch)

    :param irule: a (rule, support, confidence) tuple
    :param abox: assertional data used during transcribing
    :param tbox: schema data used during transcribing
    :param vocab: controlled vocabulary used during transcribing

    :returns: a string
    """
    string = "Voor ieder(e) {} geldt dat, als het {} {}, dan het {} {}".format(
        get_label(irule.rule.ctype, [tbox], LANG),
        get_label(irule.rule.antecedent[0], [tbox], LANG),
        get_label(irule.rule.antecedent[1], [abox, vocab], LANG),
        get_label(irule.rule.consequent[0][0], [tbox], LANG),
        get_label(irule.rule.consequent[0][1], [abox, vocab]), LANG)

    for i in range(1, len(irule.rule.consequent)):
        string += ", en {} {}".format(
            get_label(irule.rule.consequent[i][0], [tbox], LANG),
            get_label(irule.rule.consequent[i][1], [abox, vocab]), LANG)

    return string + "."