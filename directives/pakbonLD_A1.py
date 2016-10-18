#!/usr/bin/python3

import logging
from operator import itemgetter
from timeit import default_timer as timer
import rdflib
from .abstract_instruction_set import AbstractInstructionSet
from readers import rdf
from writers import rule_set, pickler
from samplers import by_depth as sampler
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
        header = "PAKBON: Context (*) with * attributes"
        print(header)
        print('-' * len(header))

    def load_dataset(self, abox, tbox, parameters):
        # read graphs
        kg_i = rdf.read(local_path=abox)
        kg_s = rdf.read(local_path=tbox)

        # sample by pattern
        pattern = (None,
                   None,
                   rdflib.URIRef("http://purl.org/crmeh#EHE0007_Context"))


        kg_i_sampled = kg_i.sample(sampler, patterns=[pattern], depth=parameters["depth"])

        return (kg_i_sampled, kg_s)

    def run_program(self, dataset, parameters):
        self.logger.info("Starting run\nParameters:\n{}".format(
            "\n".join(["\t{}: {}".format(k,v) for k,v in parameters.items()])))

        kg_i, kg_s = dataset

        # fit model
        t0 = timer()

        # generate semantic item sets from sampled graph
        si_sets = generate_semantic_item_sets(kg_i)

        # generate common behaviour sets
        cbs_sets = generate_common_behaviour_sets(si_sets,
                                                  parameters["similarity_threshold"],
                                                  parameters["max_cbs_size"])

        # generate semantic association rules
        rules = generate_semantic_association_rules(kg_i,
                                                    kg_s,
                                                    cbs_sets,
                                                    parameters["minimal_local_support"])

        # calculate support and confidence, skip those not meeting minimum requirements
        final_rule_set = []
        for rule in rules:
            support = support_of(kg_i, rule)
            confidence = confidence_of(kg_i, rule)

            if support >= parameters["minimal_support"] and\
               confidence >= parameters["minimal_confidence"]:
                final_rule_set.append((rule, support, confidence))

        # sorting rules on both support and confidence
        final_rule_set.sort(key=itemgetter(2, 1), reverse=True)

        # time took
        t1 = timer()
        dt = t1 - t0
        print("  Program completed in {:.3f} ms".format(dt))

        print("  Found {} rules".format(len(final_rule_set)))
        return final_rule_set

    def write_to_file(self, path="./of/latest", output=[]):
        overwrite = False

        print(" Writing output to {}...".format(path))
        rule_set.pretty_write(output, path, overwrite)
        pickler.write(output, path+".pickle", overwrite)

    def run(self, abox, tbox, output_path):
        self.print_header()
        print(" {}\n".format(self.time))

        parameters = {}
        parameters["sample_depth"] = 3
        parameters["similarity_threshold"] = .6
        parameters["max_cbs_size"] = 2
        parameters["minimal_local_support"] = 0.0
        parameters["minimal_support"] = 0.0
        parameters["minimal_confidence"] = 0.0

        print(" Importing Data Sets...")
        dataset = self.load_dataset(abox, tbox, parameters)

        print(" Initiated Pattern Learning...")
        output = self.run_program(dataset, parameters)

        if len(output) > 0:
            self.write_to_file(output_path, output)
