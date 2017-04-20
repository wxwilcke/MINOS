#!/usr/bin/python3

import logging
import argparse
from datetime import datetime
from readers import pickler
from ui import rule_evaluator


def run(args, time):
    model = pickler.read(args.model)
    if args.filter is not None:
        filter_path = args.filter.split('.')

        mod = __import__('.'.join(filter_path[:-1]), fromlist=[filter_path[-1:]])
        klass = getattr(mod, *filter_path[-1:])

        program = klass(time)
        program.run(model)

    rule_evaluator.cli(model, args.abox, args.tbox, args.vocab, args.output, args.mode, args.lang)

def print_header():
    header = 'An Experimental Pipeline for Data Mining on Linked Archaeological Data'
    print('=' * len(header))
    print(header)
    print('=' * len(header))

def set_logging(args, time):
    logging.basicConfig(filename='./logs/{}.log'.format(time),
                        format='%(asctime)s %(levelname)s: %(message)s',
                        level=logging.INFO)

    if args.verbose:
        logging.getLogger().addHandler(logging.StreamHandler())

if __name__ == "__main__":
    time = datetime.now().isoformat()

    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--model", help="Rule-based model", default=None)
    parser.add_argument("-o", "--output", help="Output path", default="./of/output-{}".format(time))
    parser.add_argument("-v", "--verbose", help="Increase output verbosity", action="store_true")
    parser.add_argument("--abox", help="ABox graph", default=None)
    parser.add_argument("--filter", help="Custom filter", default=None)
    parser.add_argument("--tbox", help="TBox graph", default=None)
    parser.add_argument("--vocab", help="Controlled vocabulary graph", default=None)
    parser.add_argument("--mode", help="Rule output mode", choices=['uri', 'label', 'natural'])
    parser.add_argument("--lang", help="Rule natural output language", default="en")
    args = parser.parse_args()

    set_logging(args, time)
    logger = logging.getLogger(__name__)
    logger.info("Arguments:\n{}".format(
        "\n".join(["\t{}: {}".format(arg,getattr(args, arg)) for arg in vars(args)])))

    print_header()
    run(args, time)

    logging.shutdown()
