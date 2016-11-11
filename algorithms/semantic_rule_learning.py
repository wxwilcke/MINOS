#!/usr/bin/python3

import sys
import logging
from rdflib.namespace import RDF, RDFS
from models.rule_base import RuleBase, IRule, Rule


"""
Implementation of SWARM Semantic Rule Mining algorithm [Barati2016].

Alterations:
    * Limit on exactly two SI sets per CBS is lifted. This allows conjunctions in the consequent, e.g. A -> B /\ C.
    * Added local coverage of a class type wrt the union of multiple ES in a CBS to prevent overgeneralization.
    * LLC with broadest coverage is prefered.
    * Rules with more-than-one LLC are split.
    * Added all permutations of a CBS to form a rule, e.g. A -> B /\ C, B -> A /\ C, and C -> A /\ B.

@Inbook{Barati2016,
 author="Barati, Molood and Bai, Quan and Liu, Qing",
 editor="Booth, Richard and Zhang, Min-Ling",
 title="SWARM: An Approach for Mining Semantic Association Rules from Semantic Web Data",
 bookTitle="PRICAI 2016: Trends in Artificial Intelligence: 14th Pacific Rim International Conference on Artificial Intelligence, Phuket, Thailand, August 22-26, 2016, Proceedings",
 year="2016",
 publisher="Springer International Publishing",
 address="Cham",
 pages="30--43",
 isbn="978-3-319-42911-3",
 doi="10.1007/978-3-319-42911-3_3",
}
"""

logger = logging.getLogger(__name__)

def generate_semantic_association_rules(instance_graph=None, ontology_graph=None, list_of_cbs=[], minimal_local_support=1.0):
    """ Generate semantic association rules from CBS

    :param instance_graph: a knowledge graph instance
    :param ontology_graph: a knowledge graph instance
    :param list_of_cbs: list of (CBS, similarity) tuples
    :param minimal_local_support: skip rules that do not meet the minimal local support

    :returns: a list of rules as tuples (class type, antecedent, consequent [with conjunctions])
    """

    logger.info("Generating Semantic Association Rules (LS >= {})".format(minimal_local_support))
    rules = RuleBase()
    for cbs, _ in list_of_cbs:
        for ctype, (coverage, local_support) in _lowest_level_class(instance_graph, ontology_graph, cbs).items():
            if local_support < minimal_local_support:
                continue

            cbs_list = list(cbs)
            for i in range(len(cbs_list)):
                rule = Rule(ctype, cbs_list[i][1], [pa for _, pa in cbs_list[:i]+cbs_list[i+1:]])
                rules.add(IRule(rule, support_of(instance_graph, rule), confidence_of(instance_graph, rule)))

    logger.info("Generated {} Semantic Association Rules".format(len(rules)))

    return rules

def generate_semantic_item_sets(instance_graph=None, pattern=(None, None, None)):
    """ Generate semantic item sets from a knowledge graph

    :param instance_graph: a knowledge graph instance
    :param pattern: filter triples by pattern
    """

    if instance_graph is None:
        raise ValueError('Missing input values.')

    logger.info("Generating Semantic Item Set")
    item_set = {}
    for s, p, o in instance_graph.graph.triples(pattern):
        k = (p, o)
        if k in item_set.keys():
            if s not in item_set[k]:
                item_set[k].add(s)
            continue

        item_set[k] = {s}

    logger.info("Generated {} Semantic Item Sets".format(len(item_set)))

    return item_set

def generate_common_behaviour_sets(item_sets={}, similarity_threshold=.75, max_cbs_size=2):
    """ Generate Common Behaviour Sets (CBS) from Semantic Item Sets

    :param item_sets: dictionary with (p, o)-pairs as key and item sets as value
    :param similarity_threshold: only generalize if the similarity exceeds this value
    :param max_cbs_size: limit number of ES per CBS to this value

    :returns: a list of tuples (CBS, s), with s being the similarity
    """

    logger.info("Generating Common Behaviour Sets (sim >= {}, s <= {})".format(similarity_threshold,
                                                                           max_cbs_size))
    common_behavioural_sets = []
    keys = list(item_sets.keys())
    for i in range(len(keys)):
        pa_0 = keys[i]
        es_0 = frozenset(item_sets[pa_0])
        for pa_1 in keys[i+1:]:
            es_1 = frozenset(item_sets[pa_1])
            similarity = _similarity_of(es_0, es_1)
            if similarity < similarity_threshold:
                continue

            common_behavioural_sets.append((frozenset({
                                              (es_0, pa_0),
                                              (es_1, pa_1)}),
                                              similarity))
    _cbs_extender(common_behavioural_sets, similarity_threshold, max_cbs_size)

    logger.info("Generated {} Common Behaviour Sets".format(len(common_behavioural_sets)))

    return common_behavioural_sets

def _cbs_extender(cbs_list=[], similarity_threshold=.75, max_cbs_size=sys.maxsize, _size=2):
    """ Recursively extend Common Behaviour Sets (CBS)

    :param cbs_list: list of tuples tuples (CBS, s), with s being the similarity
    :param similarity_threshold: only generalize if the similarity exceeds this value
    :param max_cbs_size: limit number of ES per CBS to this value

    :updates: original cbs_list
    :returns: none
    """

    if len(cbs_list) <= 1 or max_cbs_size <= _size:
        return cbs_list

    extended_cbs_list = []
    for i in range(len(cbs_list)):
        cbs_0, _ = cbs_list[i]
        es_0 = frozenset.union(*[es for es, _ in cbs_0])
        for cbs_1, _ in cbs_list[i+1:]:
            es_1 = frozenset.union(*[es for es, _ in cbs_1])
            similarity = _similarity_of(es_0, es_1)
            if similarity < similarity_threshold:
                continue

            extended_cbs_list.append((frozenset.union(cbs_0, cbs_1), similarity))

    cbs_list.extend(extended_cbs_list)
    _cbs_extender(extended_cbs_list, similarity_threshold, max_cbs_size=max_cbs_size, _size=_size*2)

def _similarity_of(*list_of_element_sets):
    """ Calculate similarity between element sets

    :param list_of_element_sets: list of element sets

    :returns: similarity value 0.0 <= v <= 1.0
    """

    if len(frozenset.union(*list_of_element_sets)) > 0:
        return (len(frozenset.intersection(*list_of_element_sets)) /
                len(frozenset.union(*list_of_element_sets)))
    else:
        return 0.0

def _class_hierarchy_branches(instance_graph, ontology_graph, cbs):
    """ Generate class hierarchy branch of all ESs in a CBS

    :param instance_graph: a knowledge graph instance
    :param ontology_graph: a knowledge graph instance
    :param cbs: a CBS as a set

    :returns: a dictionary with elements as keys and branches as (nested) lists
    """
    logger.debug("Determining class hierarchy branches")
    element_branches = {}
    for es, _ in cbs:
        for e in es:
            if e in element_branches.keys():
                continue

            branch = []
            for t in instance_graph.graph.objects(e, RDF.type):
                subbranch = [t]
                _branch_traversal(ontology_graph, t, subbranch)

                branch.append(subbranch)

            element_branches[e] = branch

    return element_branches

def _coverage_per_class(instance_graph, element_branches):
    """ Determine instance coverage of class types

    :param instance_graph: a knowledge graph instance
    :param cbs: a dictionary with elements as keys and branches as (nested) lists

    :returns: a dictionary with class types as keys and (instances, local coverage) tuples as items
    """
    logger.debug("Determining coverage per class")
    coverage = {}
    for e in element_branches.keys():
        for ctype in instance_graph.graph.objects(e, RDF.type):
            if ctype in coverage.keys():
                continue
            coverage[ctype] = ({e}, 0.0)
            for f in element_branches.keys():
                if e is f:
                    continue
                for branch in element_branches[f]:
                    if ctype in branch:  # ignore multiple inheritence
                        coverage[ctype][0].add(f)
                        break

    return coverage

def _lowest_level_class(instance_graph=None, ontology_graph=None, cbs=frozenset()):
    """ Determine the Lower Level Classes of the SE's in CBS

    :param instance_graph: a knowledge graph instance
    :param ontology_graph: a knowledge graph instance
    :param cbs: a CBS (set of (es, pa) sets)

    :returns: a dictionary holding class:({covered elements}, coverage support) items
    """
    # determing class hierarchy for elements in cbs
    element_branches = _class_hierarchy_branches(instance_graph, ontology_graph, cbs)
    number_of_elements = len(element_branches)

    # determine coverage per class
    coverage = _coverage_per_class(instance_graph, element_branches)

    logger.debug("Filtering LLC coverage")
    sorted_keys = sorted(coverage, key=lambda k: len(coverage[k][0]), reverse=True)
    for i in range(1, len(sorted_keys)):
        # prever broader coverage
        coverage[sorted_keys[i]][0].difference_update(*[coverage[sorted_keys[j]][0] for j in range(i)])
        if len(coverage[sorted_keys[i]][0]) <= 0:
            del coverage[sorted_keys[i]]
            continue

        # support within this CBS
        if number_of_elements > 0:
            coverage[sorted_keys[i]] = (coverage[sorted_keys[i]][0], len(coverage[sorted_keys[i]][0]) / number_of_elements)
        else:
            coverage[sorted_keys[i]] = 0.0

    return coverage

def _branch_traversal(ontology_graph, ctype, branch):
    """ Determine the upward class hierarchy branch for each class

    :param ontology_graph: a knowledge graph instance
    :param ctype: the class type to start from
    :param branch: a list representing the branch, multiple inheritence results in nested lists

    :updates: branch
    :returns: none
    """
    sclasses = list(ontology_graph.graph.objects(ctype, RDFS.subClassOf))
    if len(sclasses) == 1:
        sclass = sclasses[0]
        branch.append(sclass)
        _branch_traversal(ontology_graph, sclass, branch)
    elif len(sclasses) >= 2:
        for sclass in sclasses:
            subbranch = [sclass]
            _branch_traversal(ontology_graph, sclass, subbranch)
            branch.append(subbranch)

def support_of(instance_graph, rule):
    """ Calculate the support for rule r given knowledge graph G

    :param instance_graph: a knowledge graph instance
    :param rule: a semantic association rule as tuple (type, antecedent, consequent(s))

    :returns: support value between 0 and 1
    """
    ctype = rule[0]
    p, o = rule[1]  # antecedent

    logger.debug("Calculating support")
    number_of_supporting_facts = 0
    elements_of_type = frozenset(instance_graph.graph.subjects(RDF.type, ctype))
    for s in elements_of_type:
        if (s, p, o) in instance_graph.graph:
            number_of_supporting_facts += 1

    if len(elements_of_type) > 0:
        support = number_of_supporting_facts / len(elements_of_type)
    else:
        support = 0.0

    return support

def confidence_of(instance_graph, rule):
    """ Calculate the confidence for rule r given knowledge graph G

    :param instance_graph: a knowledge graph instance
    :param rule: a semantic association rule as tuple (type, antecedent, consequent(s))

    :returns: confidence value between 0 and 1
    """
    ctype = rule[0]
    p_0, o_0 = rule[1]  # antecedent

    logger.debug("Calculating confidence")
    number_of_antecedent_supporting_facts = 0
    number_of_rule_supporting_facts = 0
    elements_of_type = frozenset(instance_graph.graph.subjects(RDF.type, ctype))
    for s in elements_of_type:
        if (s, p_0, o_0) not in instance_graph.graph:
            continue

        number_of_antecedent_supporting_facts += 1
        for p_1, o_1 in rule[2]:  # consequent
            if (s, p_1, o_1) not in instance_graph.graph:
                break

        number_of_rule_supporting_facts += 1

    if number_of_antecedent_supporting_facts > 0:
        confidence = number_of_rule_supporting_facts / number_of_antecedent_supporting_facts
    else:
        confidence = 0.0

    return confidence

if __name__ == "__main__":
    print("Functions for Semantic Rule Learning")
