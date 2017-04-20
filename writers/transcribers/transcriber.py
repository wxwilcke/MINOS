#!/usr/bin/python3

import logging

logger = logging.getLogger(__name__)


def transcribe(irule, lang, abox=None, tbox=None, vocab=None):
    """ Transcribe a rule in natural language

    :param irule: a (rule, support, confidence) tuple
    :param lang: transcription language
    :param abox: assertional data used during transcribing
    :param tbox: schema data used during transcribing
    :param vocab: controlled vocabulary used during transcribing

    :returns: a string
    """

    return lang.transcribe(irule, abox, tbox, vocab)
