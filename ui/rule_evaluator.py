#!/usr/bin/python3

import logging
from models.rule_base import RuleBase
from readers import rdf
from writers.rule_set import pretty_write, natural_write, _rule_to_string
from writers.pickler import write
from ui.auxiliarly import clear_term
from ui.font import Font


logger = logging.getLogger(__name__)

def cli(rule_base, abox=None, tbox=None, vocab=None, path="./of/rule_set", transcribe=False, overwrite=True, compress=False):
    logger.info("Initiating CLI")

    if abox is not None:
        logger.info("Loading ABox Graph")
        abox = rdf.read(local_path=abox)
        transcribe = True
    if tbox is not None:
        logger.info("Loading TBox Graph")
        tbox = rdf.read(local_path=tbox)
        transcribe = True
    if vocab is not None:
        logger.info("Loading Controlled Vocabulary")
        vocab = rdf.read(local_path=vocab)
        transcribe = True

    _ui(rule_base, abox, tbox, vocab, path, transcribe, overwrite, compress)

def _ui(rule_base, abox, tbox, vocab, path, transcribe, overwrite, compress):
    font = Font()
    filters = RuleBase.Filter()
    output = RuleBase()

    print()
    n = rule_base.size()

    i = 0
    while i < n:
        clear_term()
        print("RULE {} / {}".format(i+1, n))
        print(_rule_to_string(rule_base.model[i]))
        print("[ACTION] ([{}] / {} / {} / {} / {} / {}): ".format(font.bold_first_char("next"),
                                                                  font.bold_first_char("previous"),
                                                                  font.bold_first_char("filter"),
                                                                  font.bold_first_char("save current"),
                                                                  font.bold_first_char("write selection"),
                                                                  font.bold_first_char("abort")),
              end="")
        answer = input()

        if answer == "p" or answer == "previous":
            i -= 1
            continue
        elif answer == "f" or answer == "filter":
            _add_filters(rule_base, filters, font)
            n = rule_base.size()
            i = 0
            continue
        elif answer == "s" or answer.startswith("save"):
            output.add(rule_base.model[i])
            print(" rule saved to temporary buffer!", end="")
            input(" [continue]")
        elif answer == "w" or answer.startswith("write"):
            if transcribe:
                natural_write(rule_base, path+'.selection', abox, tbox, vocab, overwrite, compress)
            else:
                pretty_write(rule_base, path+'.selection', overwrite, compress)
            write(rule_base, path+'.selection.pickle', overwrite)
            print("current selection written to {} !".format(path+'.selection'), end="")
            input(" [continue]")
        elif answer == "a" or answer == "abort":
            break

        # next
        i += 1


    if output.size() > 0:
        print("write {} saved rule(s)? ({} / [{}]): ".format(output.size(),
                                                            font.bold_first_char("yes"),
                                                            font.bold_first_char("no")),
              end="")

        if input().startswith("y"):
            if transcribe:
                natural_write(output, path+'.saved', abox, tbox, vocab, overwrite, compress)
            else:
                pretty_write(output, path+'.saved', overwrite, compress)
            write(rule_base, path+'.saved.pickle', overwrite)
            print("Saved {} of {} rules".format(output.size(), n))
            logger.info("Saved {} of {} rules".format(output.size(), n))

def _add_filters(rule_base, filters, font):
    key = None
    while True:
        print("[FILTER] ({} / {} / {} / [{}]): ".format(font.bold_first_char("add"),
                                                        font.bold_first_char("rmv"),
                                                        font.bold_first_char("clear"),
                                                        font.bold_first_char("back")),
              end="")
        answer = input()
        print()

        if answer == "a" or answer == "add" or answer == "r" or answer == "rmv":
            filters, key = _add_filter(rule_base, filters, answer, font)
            rule_base.filter(filters)

            while rule_base.size() == 0:
                filters, key = _revert_filter(rule_base, filters, key, font)
                rule_base.filter(filters)

            print("Filters updated!\n")
        elif answer == "c" or answer == "clear":
            filters.clear()
            rule_base.filter(filters)

            print("Filters cleared!\n")
        else:
            return

def _add_filter(rule_base, filters, operation, font, key=None):
    if key is None:
        clear_term()
        print("Select Filter:\n\ta) class\n\tb) antecedent\n\tc) consequent\n\td) support\n\te) confidence\n")
        answer = input(": ")

        key = None
        if answer == "a":
            key = "class"
        elif answer == "b":
            key = "antecedent"
        elif answer == "c":
            key = "consequent"
        elif answer == "d":
            key = "support"
        elif answer == "e":
            key = "confidence"
        else:
            return (filters, None)

    if operation.startswith("a"):
        if key == "support" or key == "confidence":
            minv = input("set minimal value [{}]: ".format(rule_base.filters.filters["minimal_"+key]))\
                    or rule_base.filters.filters["minimal_"+key]
            maxv = input("set maximal value [{}]: ".format(rule_base.filters.filters["maximal_"+key]))\
                    or rule_base.filters.filters["maximal_"+key]

            filters.set("minimal_"+key, float(minv))
            filters.set("maximal_"+key, float(maxv))
        else:
            value = input("set new value [{}]: ".format(rule_base.filters.filters[key]))\
                    or rule_base.filters.filters[key]
            # => rdflib

            filters.set(key, value)
    else:  # rmv operation
        if key == "support" or key == "confidence":
            filters.set("minimal_"+key, filters._default_filters["minimal_"+key])
            filters.set("maximal_"+key, filters._default_filters["maximal_"+key])
        else:
            filters.set(key, filters._default_filters[key])

    return (filters, key)

def _revert_filter(rule_base, filters, key, font):
    clear_term()
    print("No rules left\nUndo filter? ([{}], {}, {}): ".format(font.bold_first_char("no"),
                                                                  font.bold_first_char("last"),
                                                                  font.bold_first_char("all")),
         end="")
    answer = input()
    if answer == "l" or answer == "last":
        filters, _ = _add_filter(rule_base, filters, "rmv", font, key=key)
    elif answer == "a" or answer == "all":
        filters.clear()

    return (filters, None)
