#!/usr/bin/python3

import logging
import argparse
from datetime import datetime


def run(args, time):
    directive = args.directive.split('.')

    mod = __import__('.'.join(directive[:-1]), fromlist=[directive[-1:]])
    klass = getattr(mod, *directive[-1:])

    program = klass(time)
    program.run(args.abox, args.tbox, args.output, args.interactive)

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
    parser.add_argument("-a", "--abox", help="ABox graph", default=None)
    parser.add_argument("-d", "--directive", help="Directive for rule learning", default=None)
    parser.add_argument("-i", "--interactive", help="Interactive mode", action="store_true")
    parser.add_argument("-o", "--output", help="output path", default="./of/output-{}".format(time))
    parser.add_argument("-t", "--tbox", help="TBox graph", default=None)
    parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
    args = parser.parse_args()

    set_logging(args, time)
    logger = logging.getLogger(__name__)
    logger.info("Arguments:\n{}".format(
        "\n".join(["\t{}: {}".format(arg,getattr(args, arg)) for arg in vars(args)])))

    print_header()
    run(args, time)

    logging.shutdown()
