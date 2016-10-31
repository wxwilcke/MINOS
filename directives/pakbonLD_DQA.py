#!/usr/bin/python3

import logging
from .abstract_instruction_set import AbstractInstructionSet
from readers import rdf
from readers import pickler as model_reader
from writers import fact_set
from writers import pickler as model_writer
from algorithms.data_quality_analysing import check
from ui import fact_evaluator


class PakbonLD(AbstractInstructionSet):
    def __init__(self, time=""):
        self.time = time
        self.logger = logging.getLogger(__name__)

    def print_header(self):
        header = "PAKBON: Data Quality Analysis"
        print(header)
        print('-' * len(header))

    def load_dataset(self, abox):
        # read graphs
        return rdf.read(local_path=abox)

    def run_program(self, dataset, model):
        self.logger.info("Starting run\nUsing model of size {}".format(len(model)))

        return check(dataset, model)

    def write_to_file(self, path="./of/latest", output=[]):
        overwrite = False

        print(" Writing output to {}...".format(path))
        fact_set.pretty_write(output, path, overwrite)
        model_writer.write(output, path+".pickle", overwrite)

    def run(self, abox, model_path, output_path, interactive):
        self.print_header()
        print(" {}\n".format(self.time))

        print(" Importing Data Sets...")
        dataset = self.load_dataset(abox)

        print(" Importing Model...")
        model = model_reader.read(model_path)

        print(" Initiated Data Quality Analyser...")
        output = self.run_program(dataset, model)

        if interactive:
            print(" Initiating Evaluation Protocol...")
            output = fact_evaluator.cli(output)

        if len(output) > 0:
            self.write_to_file(output_path, output)
