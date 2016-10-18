#!/usr/bin/python3

import logging
from operator import itemgetter
from timeit import default_timer as timer
import rdflib
from .abstract_instruction_set import AbstractInstructionSet
from readers import rdf
from writers import rule_set, pickler
from samplers import by_definition as sampler
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
        header = "PAKBON: Context ('Sporen') with 12 attributes"
        print(header)
        print('-' * len(header))

    def load_dataset(self, abox, tbox):
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
        kg_i = rdf.read(local_path=abox)
        kg_s = rdf.read(local_path=tbox)

        # sample by pattern
        pattern = (None,
                   rdflib.URIRef("http://pakbon-ld.spider.d2s.labs.vu.nl/ont/SIKB0102S_grondspoortype"),
                   None)

        # define context
        # spoor with vulling
        context = [rdflib.URIRef("http://pakbon-ld.spider.d2s.labs.vu.nl/ont/SIKB0102S_grondspoortype"),
                   rdflib.URIRef("http://www.cidoc-crm.org/cidoc-crm/P53i_is_former_or_current_location_of"),
                   (rdflib.URIRef("http://www.cidoc-crm.org/cidoc-crm/P89_falls_within"),
                    rdflib.URIRef("http://pakbon-ld.spider.d2s.labs.vu.nl/ont/SIKB0102S_contexttype")),
                   (rdflib.URIRef("http://purl.org/crmeh#EHP3i"),
                    rdflib.URIRef("http://pakbon-ld.spider.d2s.labs.vu.nl/ont/SIKB0102S_kleur")),
                   (rdflib.URIRef("http://purl.org/crmeh#EHP3i"),
                    rdflib.URIRef("http://pakbon-ld.spider.d2s.labs.vu.nl/ont/SIKB0102S_textuur")),
                   (rdflib.URIRef("http://www.cidoc-crm.org/cidoc-crm/P53i_is_former_or_current_location_of"),
                    rdflib.URIRef("http://pakbon-ld.spider.d2s.labs.vu.nl/ont/SIKB0102S_structuurtype")),
                   (rdflib.URIRef("http://pakbon-ld.spider.d2s.labs.vu.nl/ont/SIKB0102S_diepte"),
                    rdflib.URIRef("http://www.cidoc-crm.org/cidoc-crm/P40_observed_dimension"),
                    rdflib.URIRef("http://www.cidoc-crm.org/cidoc-crm/P90_has_value")),
                   (rdflib.URIRef("http://pakbon-ld.spider.d2s.labs.vu.nl/ont/SIKB0102S_diepte"),
                    rdflib.URIRef("http://www.cidoc-crm.org/cidoc-crm/P40_observed_dimension"),
                    rdflib.URIRef("http://www.cidoc-crm.org/cidoc-crm/P91_has_unit")),
                   (rdflib.URIRef("http://www.cidoc-crm.org/cidoc-crm/P140i_was_attributed_by"),
                    rdflib.URIRef("http://www.cidoc-crm.org/cidoc-crm/P141_assigned"),
                    rdflib.URIRef("http://pakbon-ld.spider.d2s.labs.vu.nl/ont/SIKB0102S_beginperiode")),
                   (rdflib.URIRef("http://www.cidoc-crm.org/cidoc-crm/P140i_was_attributed_by"),
                    rdflib.URIRef("http://www.cidoc-crm.org/cidoc-crm/P141_assigned"),
                    rdflib.URIRef("http://pakbon-ld.spider.d2s.labs.vu.nl/ont/SIKB0102S_eindperiode")),
                   (rdflib.URIRef("http://www.cidoc-crm.org/cidoc-crm/P53i_is_former_or_current_location_of"),
                    rdflib.URIRef("http://www.cidoc-crm.org/cidoc-crm/P140i_was_attributed_by"),
                    rdflib.URIRef("http://www.cidoc-crm.org/cidoc-crm/P141_assigned"),
                    rdflib.URIRef("http://pakbon-ld.spider.d2s.labs.vu.nl/ont/SIKB0102S_beginperiode")),
                   (rdflib.URIRef("http://www.cidoc-crm.org/cidoc-crm/P53i_is_former_or_current_location_of"),
                    rdflib.URIRef("http://www.cidoc-crm.org/cidoc-crm/P140i_was_attributed_by"),
                    rdflib.URIRef("http://www.cidoc-crm.org/cidoc-crm/P141_assigned"),
                    rdflib.URIRef("http://pakbon-ld.spider.d2s.labs.vu.nl/ont/SIKB0102S_eindperiode"))]

        kg_i_sampled = kg_i.sample(sampler, patterns=[pattern], context=context)

        return (kg_i_sampled, kg_s)

    def run_program(self, dataset, hyperparameters):
        self.logger.info("Starting run\nParameters:\n{}".format(
            "\n".join(["\t{}: {}".format(k,v) for k,v in hyperparameters.items()])))

        kg_i, kg_s = dataset

        # fit model
        t0 = timer()

        # generate semantic item sets from sampled graph
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
        for rule in rules:
            support = support_of(kg_i, rule)
            confidence = confidence_of(kg_i, rule)

            if support >= hyperparameters["minimal_support"] and\
               confidence >= hyperparameters["minimal_confidence"]:
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

        hyperparameters = {}
        hyperparameters["similarity_threshold"] = .8
        hyperparameters["max_cbs_size"] = 8
        hyperparameters["minimal_local_support"] = 0.0
        hyperparameters["minimal_support"] = 0.0
        hyperparameters["minimal_confidence"] = 0.0

        print(" Importing Data Sets...")
        dataset = self.load_dataset(abox, tbox)

        print(" Initiated Pattern Learning...")
        output = self.run_program(dataset, hyperparameters)

        if len(output) > 0:
            self.write_to_file(output_path, output)
