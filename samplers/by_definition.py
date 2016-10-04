#!/usr/bin/python3.5

import logging
import rdflib
from models.knowledge_graph import KnowledgeGraph


logger = logging.getLogger(__name__)

def sample(knowledge_graph=None, patterns=[(None, None, None)], context=[], strict_context=True):
    """ Return user-defined context of one or more instances of a non-terminal atom.

    :param knowledge_graph: a KnowledgeGraph instance to sample
    :param patterns: a list of triple patterns (None, p, o) to filter sample with
    :param context: a list of predicates (paths as tuple) to sample objects of
    :param strict_context: true is context is a strong constraint

    :returns: the sample as a KnowledgeGraph instance
    """

    if knowledge_graph is None:
        raise ValueError("Missing parameter values")

    logger.info("Sampling user-defined context")
    logger.info("Pattern:\n\t" + "\n\t".join(["{}".format(pattern) for pattern in patterns]))
    individuals = frozenset(s for pattern in patterns for s, _, _ in knowledge_graph.graph.triples(pattern))

    logger.info("Pattern matches {} individuals".format(len(individuals)))
    logger.info("Context:\n\t" + "\n\t".join(["{}".format(path) for path in context]))

    return _sample_context(knowledge_graph, individuals, context, strict_context)

def _sample_context(knowledge_graph, individuals, context, strict_context):
    kg = KnowledgeGraph(rdflib.Graph())

    for subject in individuals:
        facts = []
        for predicate in context:
            if type(predicate) is tuple:
                facts_tree = _recursive_path_walk(knowledge_graph, subject, predicate, strict_context)

                if len(facts_tree) == 0 and strict_context:
                    facts = []
                    break

                facts.extend(facts_tree)

            else:
                facts_list = list(knowledge_graph.graph.triples((subject, predicate, None)))
                if len(facts_list) == 0 and strict_context:
                    facts = []
                    break

                facts.extend(facts_list)

        for fact in facts:
            kg.graph.add(fact)

    logger.info("Sample contains {} facts".format(len(kg.graph)))
    return kg

def _recursive_path_walk(knowledge_graph, atom, context, strict_context, _facts=None):
    if len(context) == 0:
        return []
    if _facts is None:
        _facts = []

    for s, p, o in knowledge_graph.graph.triples((atom, context[0], None)):
        facts = _recursive_path_walk(knowledge_graph, o, context[1:], strict_context)
        if len(facts) == 0 and strict_context and len(context) > 1:
            return []
        _facts.append((s, p, o))
        _facts.extend(facts)

    return _facts


if __name__ == "__main__":
    print("Sample user-defined context C of all non-terminal atoms that match a given pattern")
