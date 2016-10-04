#!/usr/bin/python3.5

import logging
import rdflib
from models.knowledge_graph import KnowledgeGraph
from samplers.auxiliary import breadth_first_sampler


logger = logging.getLogger(__name__)

def sample(knowledge_graph=None, patterns=[(None, None, None)], size=1, strict_size=False):
    """ Return spiral context up to size s of one or more instances of a non-terminal atom.

    :param knowledge_graph: a KnowledgeGraph instance to sample
    :param patterns: a list of triple patterns (None, p, o) to filter sample with
    :param size: the size of a context (number of facts)
    :param strict_size: true if size is a strong constraint

    :returns: the sample as a KnowledgeGraph instance
    """
    kg = KnowledgeGraph(rdflib.Graph())
    if knowledge_graph is not None:
        logger.info("Sampling spiral neighbourhood up to size {}".format(size))
        logger.info("Pattern:\n\t" + "\n\t".join(["{}".format(pattern) for pattern in patterns]))
        for pattern in patterns:
            for subject, _, _ in knowledge_graph.graph.triples(pattern):
                facts = breadth_first_sampler(knowledge_graph,
                                              subject,
                                              size=size,
                                              strict_size=strict_size)
                for fact in facts:
                    kg.graph.add(fact)

    logger.info("Sample contains {} facts".format(len(kg.graph)))
    return kg

if __name__ == "__main__":
    print("Sample spiral context C up till size s of all non-terminal atoms that match a given pattern")
