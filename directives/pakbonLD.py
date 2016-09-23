#!/usr/bin/python3

import logging
from collections import namedtuple
from time import perf_counter
from datetime import datetime
import rdflib
from .abstract_instruction_set import AbstractInstructionSet
from readers import rdf
from writers import rule_set
from samplers import by_definition as sampler
from algorithms.semantic_rule_learning import generate_semantic_association_rules,\
                                              generate_semantic_item_sets,\
                                              generate_common_behaviour_sets,\
                                              support_of,\
                                              confidence_of


class PakbonLD(AbstractInstructionSet):
    def __init__(self):
        pass

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
        kg = rdf.query(query_string, endpoint)
        """

        # read graph
        kg = rdf.read(local_path="/data/ARIADNE/pakbon2rdf/pakbonnen/ttl/output.ttl")

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

        dataset = kg.sample(sampler, pattern=pattern, context=context)

        return dataset

    def run_program(self, dataset, hyperparameters):
        # fit model
        t0 = perf_counter()

        # generate semantic item sets from sampled graph
        si_sets = generate_semantic_item_sets(dataset)

        # generate common behaviour sets
        cbs_sets = generate_common_behaviour_sets(si_sets,
                                                  hyperparameters["similarity_threshold"],
                                                  hyperparameters["max_cbs_size"])

        # generate semantic association rules
        rules = generate_semantic_association_rules(dataset,
                                                    cbs_sets,
                                                    hyperparameters["minimal_local_support"])

        # calculate support and confidence, skip those not meeting minimum requirements
        final_rule_set = []
        SCRule = namedtuple('SCRule', ['rule', 'support', 'confidence'])
        for rule in rules:
            support = support_of(dataset, rule)
            confidence = confidence_of(dataset, rule)

            if support >= hyperparameters["minimal_support"] and\
               confidence >= hyperparameters["minimal_confidence"]:
                final_rule_set.append(SCRule(rule, support, confidence))

        t1 = perf_counter()

        # time took
        dt = t1 - t0
        logging.info("Program completed in {} ms".format(dt))

        return final_rule_set

    def write_to_file(self, output=[]):
        path = "./output-{}".format(datetime.now().isoformat())
        overwrite = False

        rule_set.write(output, path, overwrite)

    def run(self):
        self.print_header()

        hyperparameters = {}
        hyperparameters["similarity_threshold"] = .8
        hyperparameters["max_cbs_size"] = 2
        hyperparameters["minimal_local_support"] = .8
        hyperparameters["minimal_support"] = .1
        hyperparameters["minimal_confidence"] = .75

        dataset = self.load_dataset()
        output = self.run_program(dataset, hyperparameters)
        self.write_to_file(output)
