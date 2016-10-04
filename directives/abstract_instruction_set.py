#!/usr/bin/python3

import abc


class AbstractInstructionSet():
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def print_header(self):
        """Print description of instruction set"""
        return

    @abc.abstractmethod
    def load_dataset(self, hyperparameters):
        """Load dataset into container"""
        return

    @abc.abstractmethod
    def run_program(self, dataset, hyperparameters):
        """Main loop of instruction set"""
        return

    @abc.abstractmethod
    def run(self):
        """Control running this instruction set"""
        return
