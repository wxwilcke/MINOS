#!/usr/bin/python3

import logging
from rdflib.term import Literal
from writers.auxiliarly import write, get_label
from writers.transcribers import transcriber
from writers.transcribers.language import dutch, english


logger = logging.getLogger(__name__)

def pretty_write(output, path="./of/latest", overwrite=True, compress=False, *args):
    """ Pretty print a rule set

    :param output: a list of rules
    :param path: file path to write to
    :param overwrite: overwrite file at path if exists
    :param compress: compress output as tar

    :returns: none
    """

    write(output.model, path, overwrite, compress, _rule_to_string)

def pretty_label_write(output, path="./of/latest", overwrite=True, compress=False, abox=None, tbox=None, vocab=None,
                       lang="en"):
    """ Pretty print a rule set using labels

    :param output: a list of rules
    :param path: file path to write to
    :param overwrite: overwrite file at path if exists
    :param compress: compress output as tar
    :param abox: assertional data used for label retrieval
    :param tbox: schema data used for label retrieval
    :param vocab: controlled vocabulary used for label retrieval

    :returns: none
    """

    write(output.model, path, overwrite, compress, _rule_to_label_string, abox, tbox, vocab, lang)

def natural_write(output, path="./of/latest", overwrite=True, compress=False, abox=None, tbox=None, vocab=None,
                  lang="en"):
    """ Pretty print a rule set in natural text

    :param output: a list of rules
    :param path: file path to write to
    :param overwrite: overwrite file at path if exists
    :param compress: compress output as tar
    :param abox: assertional data used during transcribing
    :param tbox: schema data used during transcribing
    :param vocab: controlled vocabulary used during transcribing

    :returns: none
    """

    write(output.model, path, overwrite, compress, _rule_to_natural_text, abox, tbox, vocab, lang)

def _rule_to_natural_text(irule, abox=None, tbox=None, vocab=None, lang="en"):
    """ Wrap a rule into a transcribed string

    :param irule: a (rule, support, confidence) tuple
    :param abox: assertional data used during transcribing
    :param tbox: schema data used during transcribing
    :param vocab: controlled vocabulary used during transcribing
    :param lang: specify language for transcriptions

    :returns: a string
    """

    if lang == "nl":
        language_module = dutch
    else:
        language_module = english

    return transcriber.transcribe(irule, language_module, abox, tbox, vocab)

def _rule_to_label_string(irule, abox=None, tbox=None, vocab=None, lang="en"):
    """ Wrap a rule into a labelled string

    :param irule: a (rule, support, confidence) tuple

    :returns: a string
    """
    consequent = """{}""".format(_statement_to_label_string(irule.rule.consequent[0],
                                                           abox,
                                                           tbox,
                                                           vocab,
                                                           lang))
    if len(irule.rule.consequent) > 1:
        consequent += """\n\tAND  """\
                    + """\n\tAND  """.join(["{}".format(_statement_to_label_string(
                                                irule.rule.consequent[i],
                                                abox,
                                                tbox,
                                                vocab,
                                                lang))\
                                            for i in range(1, len(irule.rule.consequent))])

    string = """[{}]
    IF   {}
    THEN {}
    Support:    {:.3f}
    Confidence: {:.3f}\n""".format(get_label(irule.rule.ctype, [tbox], lang),
                              _statement_to_label_string(irule.rule.antecedent,
                                                        abox,
                                                        tbox,
                                                        vocab,
                                                        lang),
                              consequent,
                              irule.support.value,
                              irule.confidence.value)

    return string

def _rule_to_string(irule, *args):
    """ Wrap a rule into a string

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

def _statement_to_label_string(statement, abox, tbox, vocab, lang):
    left = get_label(statement[0], [tbox], lang)

    if type(statement[1]) is Literal:
        right = "'{}'".format(statement[1].toPython())
    else:
        right = get_label(statement[1], [abox, vocab], lang)

    return (left, right)

def _statement_to_string(statement):
    left = statement[0].toPython()
    right = statement[1].toPython()

    if type(statement[1]) is Literal:
        if statement[1].language is not None:
            right += " [rdf:lang={}]".format(statement[1].language)
        elif statement[1].datatype is not None:
            right += " [rdf:datatype={}]".format(statement[1].datatype)

    return (left, right)
