#!/usr/bin/python3

import logging
from rdflib import RDF

logger = logging.getLogger(__name__)

def check(instance_graph, model, show_progress=True):
    logger.info("Checking {} rules".format(model.size()))
    anomalies = []
    for irule in model.irules():
        anomalies.extend(_test_rule(instance_graph, irule.rule))

    logger.info("Found {} anomalies".format(len(anomalies)))
    return anomalies

def _test_rule(instance_graph, rule):
    anomalies = []

    p, o = rule.antecedent  # antecedent
    for s in instance_graph.graph.subjects(RDF.type, rule.ctype):
        if (s, p, o) in instance_graph.graph:
            for p_1, o_1 in rule.consequent:  # consequent
                if (s, p_1, o_1) not in instance_graph.graph:
                    deviations = []
                    for o_alt in instance_graph.graph.objects(s, p_1):
                        deviations.append(o_alt)
                    anomalies.append((s, p_1, deviations))

    return anomalies
