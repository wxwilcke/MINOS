#!/usr/bin/python3

import logging

def run():
    from directives.pakbonLD import PakbonLD
    program = PakbonLD()
    program.run()

def print_header():
    header = 'An Experimental Pipeline for Data Mining on Linked Archaeological Data'
    print(header)
    print('=' * len(header))
    print('')

if __name__ == "__main__":
    logging.basicConfig(filename='example.log',
                        format='%(asctime)s %(levelname)s: %(message)s', 
                        level=logging.INFO)

    print_header()
    run()
