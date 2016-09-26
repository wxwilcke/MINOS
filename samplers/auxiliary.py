#!/usr/bin/python3.5

from collections import deque
import logging


logger = logging.getLogger(__name__)

def depth_first_sampler(knowledge_graph=None, atom=None, depth=0, allow_loops=False, _last_atom=None,  _facts=None):
    """ recursive depth-first approach to built up graph around atom

    :param knowledge_graph: a KnowledgeGraph instance to sample
    :param atom: the individual to start from
    :param depth: the maximum number of steps from atom to sample
    :param allow_loops: true if loops are allowed

    :returns: a set of facts
    """
    if _facts is None:
        _facts = set()
    if depth <= 0:
        return _facts

    for s, p, o in knowledge_graph.graph.triples((atom, None, None)):
        if not allow_loops and o == _last_atom:
            continue

        _facts = _facts.union(depth_first_sampler(knowledge_graph, o, depth-1, allow_loops, s))
        _facts.add((s, p, o))

    return _facts

def breadth_first_sampler(knowledge_graph=None, atom=None, size=0, strict_size=False, allow_loops=False,
                          search_iteration_limit=100):
    """ breadth-first approach to built up graph around atom

    :param knowledge_graph: a KnowledgeGraph instance to sample
    :param atom: the individual to start from
    :param size: the maximum size of the sample
    :param strict_size: if true, size is a strong constraint
    :param search_iteration_limit: maximum number of subsequent iterations when searching
    :param allow_loops: true if loops are allowed

    :returns: a set of facts
    """
    facts = set()
    q = deque()

    search_iteration = 0
    visited = [atom]
    q.append(atom)
    while len(q) > 0 and size > 0:
        for s, p, o in knowledge_graph.graph.triples((q.popleft(), None, None)):
            if (s, p, o) in facts:
                search_iteration += 1
                continue
            if not allow_loops and o in visited:
                continue

            facts.add((s, p, o))
            q.append(o)
            visited.append(o)

            size -= 1
            if size <= 0:
                break

            search_iteration = 0
        if search_iteration >= search_iteration_limit:
            logger.info("Reached maximum number of search iterations")
            break

    if strict_size and size > 0:
        facts = set()

    return facts

def facts_to_context(atom, facts=[]):
    """ translate connected facts to a context definition

    :param atom: the atom from which all walks or paths start
    :param facts: a list of facts (s, p, o) representing walks or paths

    :return: a context definition as a set
    """

    context_definition = set()
    for s, p, o in facts:
        predicate_list = [p]
        while s != atom:
            for u, w, v in facts:
                if s == v:
                    s = u
                    predicate_list.insert(0, w)

                    break

        if len(predicate_list) == 1:
            context_definition.add(predicate_list[0])
        else:
            context_definition.add(tuple(predicate_list))

    return context_definition

def shared_context(contexts=[]):
    """ determine shares context elements

    :param context: a list of contexts (sets)

    :returns: a set of shared context elements
    """
    shared_context = {contexts[0]}
    for context in contexts[1:]:
        shared_context.intersection_update(context)

    return shared_context

def context_elements(contexts=[]):
    """ determine all context elements

    :param context: a list of contexts (sets)

    :returns: a set of all used context elements
    """
    context_elements = {}
    for context in contexts[1:]:
        context_elements.update(context)

    return context_elements

if __name__ == "__main__":
    print("Auxiliarly functions for context sampling")
