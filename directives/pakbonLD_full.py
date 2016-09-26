#!/usr/bin/python3

import logging
from collections import namedtuple
from timeit import default_timer as timer
from .abstract_instruction_set import AbstractInstructionSet
from readers import rdf
from writers import rule_set, pickler
from algorithms.semantic_rule_learning import generate_semantic_association_rules,\
                                              generate_semantic_item_sets,\
                                              generate_common_behaviour_sets,\
                                              support_of,\
                                              confidence_of


class PakbonLD(AbstractInstructionSet):
    def __init__(self, time=""):
        self.time = time
        self.logger = logging.getLogger(__name__)

    def print_header(self):
        header = 'A directive to learn association rules over the PakbonLD cloud'
        print(header)
        print('-' * len(header))

    def load_dataset(self):
        """
        # pakbonLD SPARQL endpoint
        endpoint = "http://pakbon-ld.spider.d2s.labs.vu.nl/sparql/"

        # query
        query_string = "" "
            prefix pbont: <http://pakbon-ld.spider.d2s.labs.vu.nl/ont/>
            prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

            SELECT DISTINCT ?s ?p ?o
            WHERE {
             ?s a pbont:SIKB0102S_Vondstcontext;
                ?p ?o.
             FILTER (?p != rdf:type)
             } LIMIT 1000"" "

        # perform query and return a KnowledgeGraph instance
        kg_i = rdf.query(query_string, endpoint)
        """

        # read graphs
        kg_i = rdf.read(local_path="./if/instance_graph.ttl")
        kg_s = rdf.read(local_path="./if/ontology_graph.ttl")

        return (kg_i, kg_s)

    def run_program(self, dataset, hyperparameters):
        self.logger.info("Starting run\nParameters:\n{}".format(
            "\n".join(["\t{}: {}".format(k,v) for k,v in hyperparameters.items()])))

        kg_i, kg_s = dataset

        # fit model
        t0 = timer()

        # generate semantic item sets from graph
        si_sets = generate_semantic_item_sets(kg_i)

        # generate common behaviour sets
        cbs_sets = generate_common_behaviour_sets(si_sets,
                                                  hyperparameters["similarity_threshold"],
                                                  hyperparameters["max_cbs_size"])

        # generate semantic association rules
        rules = generate_semantic_association_rules(kg_i,
                                                    kg_s,
                                                    cbs_sets,
                                                    hyperparameters["minimal_local_support"])

        # calculate support and confidence, skip those not meeting minimum requirements
        final_rule_set = []
        SCRule = namedtuple('SCRule', ['rule', 'support', 'confidence'])
        for rule in rules:
            support = support_of(kg_i, rule)
            confidence = confidence_of(kg_i, rule)

            if support >= hyperparameters["minimal_support"] and\
               confidence >= hyperparameters["minimal_confidence"]:
                final_rule_set.append(SCRule(rule, support, confidence))

        t1 = timer()

        # time took
        dt = t1 - t0
        print("  Program completed in {:.3f} ms".format(dt))

        print("  Found {} rules".format(len(final_rule_set)))
        return final_rule_set

    def write_to_file(self, output=[]):
        path = "./of/output-{}".format(self.time)
        overwrite = False

        print(" Writing output to {}...".format(path))
        rule_set.pretty_write(output, path, overwrite)
        pickler.write(output, path+".pickle", overwrite)

    def run(self):
        self.print_header()

        hyperparameters = {}
        hyperparameters["similarity_threshold"] = .6
        hyperparameters["max_cbs_size"] = 8
        hyperparameters["minimal_local_support"] = 0.0
        hyperparameters["minimal_support"] = 0.0
        hyperparameters["minimal_confidence"] = 0.5

        print(" Importing Data Sets...")
        dataset = self.load_dataset()

        print(" Initiated Pattern Learning...")
        output = self.run_program(dataset, hyperparameters)

        if len(output) > 0:
            self.write_to_file(output)
