#!/usr/bin/python3

import logging
import re


logger = logging.getLogger(__name__)
LANG_DEFAULT = "en"

def get_label(node, knowledge_graphs=[], lang=LANG_DEFAULT, fallback=True):
    """ Retrieve label in preferred language

    :param node: a resource
    :param knowledge_graphs: a list of KnowledgeGraph instances

    :returns: a string
    """
    labels = []
    if len(knowledge_graphs) >= 0:
        for knowledge_graph in knowledge_graphs:
            if knowledge_graphs is not None:
                labels.extend(knowledge_graph.graph.preferredLabel(node, lang))

        if len(labels) <= 0 and lang != LANG_DEFAULT and fallback:
            for knowledge_graph in knowledge_graphs:
                if knowledge_graphs is not None:
                    labels.extend(knowledge_graph.graph.preferredLabel(node, LANG_DEFAULT))

    label = node.toPython()
    if len(labels) <= 0:
        match = re.match('.*[/|#](.*)', label)
        if match is not None:
            label = match.group(1)
    else:
        label = labels[0][1].toPython()

    return label
