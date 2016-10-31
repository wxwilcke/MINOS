#!/usr/bin/python3

import logging
from rdflib import RDF

logger = logging.getLogger(__name__)

def check(instance_graph, model):
    logger.info("Checking {} rules".format(len(model)))
    anomalies = []
    for rule, _, _ in model:
        anomalies.extend(_test_rule(instance_graph, rule))

    logger.info("Found {} anomalies".format(len(anomalies)))
    return anomalies

def _test_rule(instance_graph, rule):
    ctype = rule[0]
    p, o = rule[1]  # antecedent

    anomalies = []
    for s in instance_graph.graph.subjects(RDF.type, ctype):
        if (s, p, o) in instance_graph.graph:
            for p_1, o_1 in rule[2]:  # consequent
                if (s, p_1, o_1) not in instance_graph.graph:
                    deviations = []
                    for o_alt in instance_graph.graph.objects(s, p_1):
                        deviations.append(o_alt)
                    anomalies.append((s, p_1, deviations))

    return anomalies
