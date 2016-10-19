#!/usr/bin/python3

import logging
from operator import itemgetter
from multiprocessing import Process, Manager, Pool, cpu_count
from functools import partial
from math import floor
from timeit import default_timer as timer
import rdflib
from .abstract_instruction_set import AbstractInstructionSet
from readers import rdf
from writers import rule_set, pickler
from samplers import by_definition as sampler
from algorithms.semantic_rule_learning_mp import generate_semantic_association_rules,\
                                                 generate_semantic_item_sets,\
                                                 generate_common_behaviour_sets,\
                                                 extend_common_behaviour_sets,\
                                                 evaluate_rules


NUM_CORES_PER_CPU = 2
NUM_OF_WORKERS = cpu_count() * NUM_CORES_PER_CPU

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

    def run_program(self, dataset, parameters):
        self.logger.info("Starting run\nParameters:\n{}".format(
            "\n".join(["\t{}: {}".format(k,v) for k,v in parameters.items()])))
        self.logger.info("Distributing load over {} cores".format(NUM_OF_WORKERS))

        kg_i, kg_s = dataset

        # fit model
        t0 = timer()

        # MP manager
        manager = Manager()

        # generate semantic item sets from sampled graph
        triples = manager.list(kg_i.graph)
        chunksize = max(1, floor(len(triples) / NUM_OF_WORKERS))
        slices = [slice(i, i+chunksize) for i in range(0, len(triples), chunksize)]
        batches = [triples[slc] for slc in slices]
        si_sets = manager.dict()
        with Pool(processes=NUM_OF_WORKERS) as pool:
            it = pool.imap_unordered(func=generate_semantic_item_sets, iterable=batches)

            while True:
                try:
                    # sync dicts
                    si_set = next(it)
                    for k in si_set.keys():
                        if k in si_sets.keys():
                            items = si_sets[k]
                            items.update(si_set[k])
                            si_sets[k] = items
                            continue
                        si_sets[k] = si_set[k]
                except StopIteration:
                    break


        # generate common behaviour sets
        work = manager.Queue()
        keys = list(si_sets.keys())
        slices = self.diagonal_matrix_slicer(keys)

        cbs_sets = manager.list()
        pool = []
        for i in range(NUM_OF_WORKERS):
            p = Process(target=generate_common_behaviour_sets, args=(si_sets,
                                                                     cbs_sets,
                                                                     work,
                                                                     parameters["similarity_threshold"]))
            p.daemon = True
            p.start()
            pool.append(p)

        for slce in slices:
            work.put(slce)

        for p in pool:
            work.put(None)

        # join shared variables
        for p in pool:
            p.join()


        # extend common behaviour sets
        cbs_size = 2
        cbs_sets_extended = manager.list(cbs_sets)
        while cbs_size < parameters["max_cbs_size"]:
            func = partial(extend_common_behaviour_sets, cbs_sets_extended, parameters["similarity_threshold"])

            slices = self.diagonal_matrix_slicer(cbs_sets_extended)
            cbs_sets_extention = manager.list()
            with Pool(processes=NUM_OF_WORKERS) as pool:
                it = pool.imap_unordered(func=func, iterable=slices)

                while True:
                    try:
                        cbs_subset = next(it)
                        cbs_sets_extention.extend(cbs_subset)
                    except StopIteration:
                        break

            cbs_sets.extend(cbs_sets_extention)
            cbs_sets_extended = cbs_sets_extention
            cbs_size *= 2


        # generate semantic association rules
        rules = manager.list()
        work = manager.Queue()
        size = max(1, floor(len(cbs_sets) / NUM_OF_WORKERS))
        slices = [slice(i, i+size) for i in range(0, len(cbs_sets), size)]

        pool = []
        for i in range(NUM_OF_WORKERS):
            p = Process(target=generate_semantic_association_rules, args=(kg_i,
                                                                          kg_s,
                                                                          cbs_sets,
                                                                          work,
                                                                          rules,
                                                                          parameters["minimal_local_support"]))
            p.daemon = True
            p.start()
            pool.append(p)

        for slce in slices:
            work.put(slce)

        for p in pool:
            work.put(None)

        # join shared variables
        for p in pool:
            p.join()


        # calculate support and confidence, skip those not meeting minimum requirements
        final_rule_set = manager.list()
        work = manager.Queue()
        size = max(1, floor(len(rules) / NUM_OF_WORKERS))
        slices = [slice(i, i+size) for i in range(0, len(rules), size)]

        pool = []
        for i in range(NUM_OF_WORKERS):
            p = Process(target=evaluate_rules, args=(kg_i,
                                                     rules,
                                                     work,
                                                     final_rule_set,
                                                     parameters["minimal_support"],
                                                     parameters["minimal_confidence"]))

            p.daemon = True
            p.start()
            pool.append(p)

        for slce in slices:
            work.put(slce)

        for p in pool:
            work.put(None)

        # join shared variables
        for p in pool:
            p.join()


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
        parameters["similarity_threshold"] = .8
        parameters["max_cbs_size"] = 4
        parameters["minimal_local_support"] = 0.0
        parameters["minimal_support"] = 0.0
        parameters["minimal_confidence"] = 0.0

        print(" Importing Data Sets...")
        dataset = self.load_dataset(abox, tbox)

        print(" Initiated Pattern Learning...")
        output = self.run_program(dataset, parameters)

        if len(output) > 0:
            self.write_to_file(output_path, output)

    def diagonal_matrix_slicer(self, items=[]):
        slices = []
        n = len(items)
        total_work_load = sum(range(n))
        avg_work_load = total_work_load / NUM_OF_WORKERS
        work_load_start = n
        work_load_end = work_load_start
        while len(slices) < NUM_OF_WORKERS:
            work_load = 0
            while work_load < avg_work_load and work_load_start > 0:
                work_load_start -= 1
                work_load = sum(range(work_load_end, work_load_start, -1))

            slices.append(range(n-work_load_end, n-work_load_start))
            work_load_end = work_load_start

        return slices
