#!/usr/bin/python3.5

from copy import deepcopy
from rdflib import URIRef
from rdflib.term import Literal
from writers.rule_set import _rule_to_string

class Rule:
    """ Rule class
    """
    ctype = None
    antecedent = None
    consequent = None

    def __init__(self, ctype=None, antecedent=None, consequent=None):
        self.ctype = ctype
        self.antecedent = antecedent
        self.consequent = consequent

    def get(self):
        return (self.ctype, self.antecedent, self.consequent)

    def __str__(self):
        return "{}".format(self.get())


class IRule:
    """ IRule class
    """
    rule = None
    support = -1.0
    confidence = -1.0

    def __init__(self, rule=None, support=-1.0, confidence=-1.0):
        if type(rule) is not Rule:
            raise TypeError("Expects instance of type Rule (was {})".format(type(rule)))
        else:
            self.rule = rule
            self.support = support
            self.confidence = confidence

    def get(self):
        return (self.rule, self.support, self.confidence)

    def pretty_print(self):
        return _rule_to_string(self)

    def __str__(self):
        return "({}, {}, {})".format(str(self.rule), self.support, self.confidence)


class RuleBase:
    """ RuleBase class
    """
    _original_model = None
    model = None
    filters = None

    def __init__(self, model=[], filters=None):
        self._original_model = deepcopy(model)
        self.model = deepcopy(self._original_model)
        self.filters = filters if filters is not None else self.Filter()

    def add(self, irule):
        if type(irule) is not IRule:
            raise TypeError("Expects instance of type IRule (was {})".format(type(irule)))
        else:
            self.model.append(irule)

    def rmv(self, irule):
        self.model.remove(irule)

    def irules(self,
               ctype=None,
               antecedent=None,
               consequent=None,
               minimal_support=0.0,
               maximal_support=1.0,
               minimal_confidence=0.0,
               maximal_confidence=1.0):
        for irule in self.model:
            if (self.filters.filters['class'] is None or irule.rule.ctype is self.filters.filters['class']) and\
               (self.filters.filters['antecedent'] is None or irule.rule.antecedent is self.filters.filters['antecedent']) and\
               (self.filters.filters['consequent'] is None or irule.rule.consequent is self.filters.filters['consequent']) and\
               irule.support >= minimal_support and\
               irule.support <= maximal_support and\
               irule.confidence >= minimal_confidence and\
               irule.confidence <= maximal_confidence:
                yield irule

    def size(self):
        return (len(self.model))

    def sort(self, by_support=False, by_confidence=False, reverse=True):
        key = None
        if by_support:
            key = lambda r: (r.support, r.confidence)
        if by_confidence:
            key = lambda r: (r.confidence, r.support)

        self.model.sort(key=key, reverse=reverse)

    def filter(self, filters):
        if len(self.filters.difference()) <= 0:
            self._original_model = deepcopy(self.model)

        diff = filters.difference(self.filters)
        for key in diff:
            if filters.filters[key] == self.Filter._default_filters[key]:
                self.model = deepcopy(self._original_model)
                diff = filters.difference()
                break

        self.filters = deepcopy(filters)
        if len(diff) > 0:
            self.update()

    def update(self):
        self.model = [irule for irule in self.irules(ctype=self.filters.filters['class'],
                                                     antecedent=self.filters.filters['antecedent'],
                                                     consequent=self.filters.filters['consequent'],
                                                     minimal_support=self.filters.filters['minimal_support'],
                                                     minimal_confidence=self.filters.filters['minimal_confidence'],
                                                     maximal_support=self.filters.filters['maximal_support'],
                                                     maximal_confidence=self.filters.filters['maximal_confidence'])]

    class Filter:
        """ Filter for RuleBase class
        """
        _default_filters = {"class": None,
                            "antecedent": None,
                            "consequent": None,
                            "minimal_support": 0,
                            "maximal_support": 1,
                            "minimal_confidence": 0,
                            "maximal_confidence": 1}
        filters = {}

        def __init__(self, filters=None):
            if filters is not None and self._check_values(filters):
                self.filters = deepcopy(filters)
            else:
                self.filters = deepcopy(self._default_filters)

        def set(self, key, value):
            if self._check_value(key, value):
                self.filters[key] = value

        def unset(self, key):
            if key not in self.filters.keys():
                raise KeyError("Unknown key: {}".format(key))
            else:
                self.filters[key] = self._default_filters[key]

        def clear(self):
            self.filters = deepcopy(self._default_filters)

        def difference(self, filters=None):
            if filters is None:
                filters = self._default_filters
            else:
                if type(filters) is not type(self):
                    raise TypeError("Filter should be of type Filter (was {})".format(type(filters)))
                    return None

                filters = filters.filters

            return [key for key in filters.keys() if
                    filters[key] != self.filters[key]]

        def _check_values(self, filters):
            for k, v in filters.items():
                signal = self._check_value(k, v)

                if signal is False:
                    return False

            return True

        def _check_value(self, key, value):
            if key not in self.filters.keys():
                raise KeyError("Unknown key: {}".format(key))
                return False
            if (key.startswith("minimal_") or key.startswith("maximal_")) and (value < 0 or value > 1):
                raise ValueError("Value should be between and including 0 and 1 (was {})".format(value))
                return False
            if key == "class" and (type(value) is not URIRef and value is not None):
                raise TypeError("Class should be of type URIRef (was {})".format(type(value)))
                return False
            if key == "antecedent" and not self._check_value_statement(value):
                raise TypeError("Antecedent should be a (URIRef, URIRef|Literal) tuple")
                return False
            if key == "consequent" and ((value is not None and type(value) is not list) or\
                    (value is not None and False in [self._check_value_statement(s) for s in value])):
                raise TypeError("Consequent should be a [(URIRef, URIRef|Literal), ...] list")
                return False

            return True

        def _check_value_statement(self, value):
            if ((value is not None and type(value) is not tuple) or
                    len(value) != 2 or
                    (value[0] is not None and type(value[0]) is not URIRef) or
                    (value[1] is not None and type(value[1]) is not URIRef and type(value[1]) is not Literal)):
                return False

            return True
