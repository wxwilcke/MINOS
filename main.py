#!/usr/bin/python3

import logging
from datetime import datetime

def run(time):
    from directives.pakbonLD import PakbonLD
    program = PakbonLD(time)
    program.run()

def print_header():
    header = 'An Experimental Pipeline for Data Mining on Linked Archaeological Data'
    print(header)
    print('=' * len(header))
    print('')

if __name__ == "__main__":
    time = datetime.now().isoformat()
    
    logging.basicConfig(filename='./logs/MINOS_{}.log'.format(time),
                        format='%(asctime)s %(levelname)s: %(message)s', 
                        level=logging.INFO)

    print_header()
    run(time)
