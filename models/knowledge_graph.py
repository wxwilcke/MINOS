#!/usr/bin/python3.5

import logging
from itertools import chain

import rdflib


class KnowledgeGraph:
    """ Knowledge Graph Class
    A wrapper around an imported rdflib.Graph object with convenience functions
    """
    graph = None

    def __init__(self, graph=None):
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initiating Knowledge Graph")
        self.graph = graph

    def load(self, graph=None):
        if graph is not None:
            self.graph = graph
            self.logger.info("Graph loaded into Knowledge Graph")

    ### Generators ###

    def atoms(self, omit_duplicates=True):
        self.logger.info("Yielding atoms")
        if omit_duplicates:
            atoms = frozenset(chain(self.graph.subjects(), self.graph.objects()))
        else:
            atoms = list(chain(self.graph.subjects(), self.graph.objects()))

        for atom in atoms:
            yield(atom)

    def non_terminal_atoms(self, omit_duplicates=True):
        self.logger.info("Yielding non-terminal atoms")
        if omit_duplicates:
            non_terminal_atoms = frozenset(self.graph.subjects())
        else:
            non_terminal_atoms = self.graph.subjects()

        for atom in non_terminal_atoms:
            yield(atom)

    def terminal_atoms(self, omit_duplicates=True):
        non_terminal_atoms = list(self.non_terminal_atoms())
        if omit_duplicates:
            terminal_atoms = frozenset(self.graph.objects())
        else:
            terminal_atoms = self.graph.objects()

        self.logger.info("Yielding terminal atoms")
        for atom in terminal_atoms:
            if atom in non_terminal_atoms:
                continue

            yield(atom)

    def literals(self):
        self.logger.info("Yielding literals")
        for obj in self.graph.objects():
            if type(obj) is rdflib.Literal:
                yield(obj)

    def resources(self, omit_blank_nodes=False):
        self.logger.info("Yielding resources")
        for res in self.atoms():
            if (type(res) is rdflib.Literal or
               (omit_blank_nodes and type(res) is rdflib.BNode)):
                continue

            yield(res)

    def predicates(self, omit_literals=False, omit_duplicates=True):
        if omit_literals:
            literals = frozenset(self.literals())

        if omit_duplicates:
            predicates = frozenset(self.graph.predicates())
        else:
            predicates = self.graph.predicates()

        self.logger.info("Yielding predicates")
        for p in predicates:
            if omit_literals and len(set(self.graph.objects(None, p))-literals) <= 0:
                # p is only used with a literal as object
                continue

            yield(p)

    def triples(self, ignore_literals=False):
        self.logger.info("Yielding triples")
        for s,p,o in self.graph:
            if ignore_literals and type(o) is rdflib.Literal:
                continue

            yield (s, p, o)

    ### Operators ###

    def propositionalize(self, strategy=None, **kwargs):
        """ Propositionalize this graph using the given strategy
        returns a propositional dataset
        """
        if strategy is None:
            raise ValueError('Strategy cannot be left undefined')

        self.logger.info("Propositionalizing graph")
        return strategy.propositionalize(self, kwargs)

    def upgrade(self, strategy=None, **kwargs):
        """ Upgrade a propositional dataset into a graph using the given strategy
        returns a KnowledgeGraph instance
        """
        if strategy is None:
            raise ValueError('Strategy cannot be left undefined')

        self.logger.info("Upgrading graph")
        return strategy.upgrade(self, kwargs)

    def sample(self, strategy=None, **kwargs):
        """ Sample this graph using the given strategy
        returns a KnowledgeGraph instance
        """
        if strategy is None:
            raise ValueError('Strategy cannot be left undefined')

        self.logger.info("Sampling graph")
        return strategy.sample(self, **kwargs)


### Independent Functions ##

def union(knowledge_graph_a=None, knowledge_graph_b=None):
    """ Union of Knowledge Graphs
    returns a new KnowledgeGraph instance
    """
    kg = KnowledgeGraph(rdflib.Graph())
    if knowledge_graph_a.graph is not None and knowledge_graph_b.graph is not None:
        kg.graph = knowledge_graph_a.graph + knowledge_graph_b.graph

    return kg

def minimalGraphOntology(data = None, ontology = None):
    """ Remove concepts from the ontology that are not used in the data 
    """
    elements = frozenset(chain(data.graph.subjects(), data.graph.predicates(), data.graph.objects()))
    ontology.graph -= [(s,p,o) for s,p,o in list(ontology.graph) if s not in elements]

    return ontology

def relationDistribution(knowledge_graph=None):
    from collections import Counter

    return sorted(Counter(knowledge_graph.predicates()).items(), key=lambda i:i[1], reverse=True)

if __name__ == "__main__":
    print("Knowledge Graph")
