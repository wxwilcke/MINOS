#!/usr/bin/python3

import logging
from re import match, DOTALL
from rdflib import URIRef, Literal
from models.rule_base import RuleBase, IRule, Rule


logger = logging.getLogger(__name__)

def read(path="./of/latest"):
    """ Read free text rule set
    """
    mode = 'r'

    logger.info("Loading free text rule set (mode {}) from {}".format(mode, path))

    rule_set = None
    with open(path, mode) as f:
        rule_set = _read_rules(f)

    return rule_set

def _read_rules(f):
    rule_base = RuleBase()
    while True:
        raw_rule = _read_rule(f)

        match = _isRule(raw_rule)
        if match is None:
            break

        rule_base.add(_to_object(match))

    return rule_base

def _read_rule(f):
    rule = ""
    line = f.readline()
    while line != "\n" and "<EOF>" not in line:
        rule += line
        line = f.readline()

    return rule

def _to_object(match):
    ctype = match.group(1)
    antecedent = match.group(2)
    consequent = match.group(3)
    support = float(match.group(5))
    confidence = float(match.group(7))

    return IRule(Rule(URIRef(ctype),
                      _mkCondition(antecedent),
                      _mkConsequent(consequent)),
                 support,
                 confidence)

def _mkCondition(rule_part):
    pattern = "[a-z]+\.[a-z]+\.([A-Za-z]+)\('(.*)'\), [a-z]+\.[a-z]+\.([A-Za-z]+)\(('|\")(.*('|\"))\)"
    rmatch = match(pattern, rule_part)

    predicate = URIRef(rmatch.group(2))
    if rmatch.group(3) == "Literal":
        object_elements = rmatch.group(5).rsplit(", ")
        object = Literal(object_elements[0])

        if len(object_elements) > 1:
            props = object_elements[1].split("=")
            if props[0] == "lang":
                object = Literal(object, lang=props[1][1:-1])
            if props[0] == "datatype":
                object = Literal(object, datatype=props[1][1:-1])
    else:
        object = URIRef(rmatch.group(5))

    return (predicate, object)

def _mkConsequent(rule_part):
    rule_parts = rule_part.split(")\n\tAND  (")
    return [_mkCondition(consequent) for consequent in rule_parts]

def _isRule(rule):
    pattern = """\[(.*)\]\n    IF   \((.*\))\)\n    THEN \((.*(AND.*)*)\)\n    Support:    ((0|1)\.[0-9]{3})\n    Confidence: ((0|1)\.[0-9]{3})\n"""
    return match(pattern, rule, DOTALL)
