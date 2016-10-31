#!/usr/bin/python3

import logging
from writers.fact_set import _fact_to_string
from ui.font import Font


logger = logging.getLogger(__name__)

def cli(facts=[]):
    logger.info("Initiating CLI")
    font = Font()
    output = []
    dump = False

    print()
    n = len(facts)
    for i in range(n):
        if dump is True:
            output.append(facts[i])
            continue

        print("FACT {} / {}".format(i+1, n))
        print(_fact_to_string(facts[i]))

        print("Tag fact {} as dubious? ({}, [{}], {}, {}) ".format(i+1,
                                                                   font.bold_first_char("yes"),
                                                                   font.bold_first_char("no"),
                                                                   font.bold_first_char("dump"),
                                                                   font.bold_first_char("abort")),
              end="")
        answer = input()
        print()

        if answer == "y" or answer == "yes":
            output.append(facts[i])
        elif answer == "d" or answer == "dump":
            output.append(facts[i])
            dump = True
        elif answer == "a" or answer == "abort":
            break
        else:
            continue

    logger.info("Tagged {} of {} candidate facts as dubious".format(len(output), n))
    return output
