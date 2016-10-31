#!/usr/bin/python3

import logging
from writers.rule_set import _rule_to_string
from ui.font import Font


logger = logging.getLogger(__name__)

def cli(rule_base=[]):
    logger.info("Initiating CLI")
    font = Font()
    output = []
    dump = False

    print()
    n = len(rule_base)
    for i in range(n):
        if dump is True:
            output.append(rule_base[i])
            continue

        print("RULE {} / {}".format(i+1, n))
        print(_rule_to_string(rule_base[i]))

        print("Save Rule {}? ({}, [{}], {}, {}) ".format(i+1,
                                                         font.bold_first_char("yes"),
                                                         font.bold_first_char("no"),
                                                         font.bold_first_char("dump"),
                                                         font.bold_first_char("abort")),
              end="")
        answer = input()
        print()

        if answer == "y" or answer == "yes":
            output.append(rule_base[i])
        elif answer == "d" or answer == "dump":
            output.append(rule_base[i])
            dump = True
        elif answer == "a" or answer == "abort":
            break
        else:
            continue

    logger.info("Saved {} of {} candidate rules".format(len(output), n))
    return output
