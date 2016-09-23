#!/usr/bin/python3.5

import logging
import rdflib
from models.knowledge_graph import KnowledgeGraph
from samplers.auxiliary import depth_first_sampler


def sample(knowledge_graph=None, pattern=(None, None, None), depth=1):
    """ Return neighbourhood context of one or more instances of a non-terminal atom.

    :param knowledge_graph: a KnowledgeGraph instance to sample
    :param pattern: a triple pattern (None, p, o) to filter sample with
    :param depth: the maximum distance from an atom to sample

    :returns: the sample as a KnowledgeGraph instance
    """

    kg = KnowledgeGraph(rdflib.Graph())
    if knowledge_graph is not None and pattern is not None:
        logging.info("Sampling neighbourhood up to depth {}".format(depth))
        for subject, _, _ in knowledge_graph.graph.triples(pattern):
            facts = depth_first_sampler(knowledge_graph,
                                        subject,
                                        depth=depth)
            for fact in facts:
                kg.graph.add(fact)

    return kg

if __name__ == "__main__":
    print("Sample context C up till depth d of all non-terminal atoms that match a given pattern")
