#!/usr/bin/python3.5

import logging
import rdflib
from models.knowledge_graph import KnowledgeGraph
from samplers.auxiliary import depth_first_sampler


logger = logging.getLogger(__name__)

def sample(knowledge_graph=None, patterns=[(None, None, None)], depth=1):
    """ Return neighbourhood context of one or more instances of a non-terminal atom.

    :param knowledge_graph: a KnowledgeGraph instance to sample
    :param patterns: a list of triple patterns (None, p, o) to filter sample with
    :param depth: the maximum distance from an atom to sample

    :returns: the sample as a KnowledgeGraph instance
    """

    kg = KnowledgeGraph(rdflib.Graph())
    if knowledge_graph is not None:
        logger.info("Sampling neighbourhood up to depth {}".format(depth))
        logger.info("Pattern:\n\t" + "\n\t".join(["{}".format(pattern) for pattern in patterns]))
        for pattern in patterns:
            for subject, _, _ in knowledge_graph.graph.triples(pattern):
                facts = depth_first_sampler(knowledge_graph,
                                            subject,
                                            depth=depth)
                type_present = False
                for s, p, o in facts:
                    kg.graph.add((s, p, o))

                    if p == rdflib.RDF.type and s == subject:
                        type_present = True

                # type is required
                if not type_present:
                    for ctype in knowledge_graph.graph.objects(subject, rdflib.RDF.type):
                        kg.graph.add((subject, rdflib.RDF.type, ctype))

    logger.info("Sample contains {} facts".format(len(kg.graph)))
    return kg

if __name__ == "__main__":
    print("Sample context C up till depth d of all non-terminal atoms that match a given pattern")
