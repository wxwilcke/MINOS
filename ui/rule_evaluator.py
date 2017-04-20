#!/usr/bin/python3

import logging
from time import time
from models.rule_base import RuleBase
from readers import rdf
from writers.rule_set import pretty_write, pretty_label_write, natural_write, _rule_to_string, _rule_to_label_string, _rule_to_natural_text
from writers.pickler import write as dump
from ui.auxiliarly import clear_term
from ui.font import Font


logger = logging.getLogger(__name__)

def cli(rule_base, abox=None, tbox=None, vocab=None, path="./of/rule_set", mode="uri", lang="en", overwrite=True, compress=False):
    logger.info("Initiating CLI")

    if abox is not None:
        logger.info("Loading ABox Graph")
        abox = rdf.read(local_path=abox)
    if tbox is not None:
        logger.info("Loading TBox Graph")
        tbox = rdf.read(local_path=tbox)
    if vocab is not None:
        logger.info("Loading Controlled Vocabulary")
        vocab = rdf.read(local_path=vocab)

    printer = None
    writer = None
    if mode == "label":
        printer = _rule_to_label_string
        writer = pretty_label_write
    elif mode == "natural":
        printer = _rule_to_natural_text
        writer = natural_write
    else:  # mode == uri
        writer = pretty_write
        printer = _rule_to_string

    _ui(rule_base, abox, tbox, vocab, path, printer, writer, lang, overwrite, compress)

def _ui(rule_base, abox, tbox, vocab, path, printer, writer, lang, overwrite, compress):
    font = Font()
    filters = RuleBase.Filter()
    output = RuleBase()

    print()
    n = rule_base.size()

    i = 0
    while i < n:
        clear_term()
        print("RULE {} / {}".format(i+1, n))
        print(printer(rule_base.model[i], abox, tbox, vocab, lang))
        print("[ACTION] ([{}] / {} / {} / {} / {} / {}): ".format(font.bold_first_char("next"),
                                                                  font.bold_first_char("previous"),
                                                                  font.bold_first_char("add to buffer"),
                                                                  font.bold_first_char("filter"),
                                                                  font.bold_first_char("write rule set"),
                                                                  font.bold_first_char("exit")),
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
        elif answer == "a" or answer.startswith("add"):
            output.add(rule_base.model[i])
            print(" rule saved to temporary buffer!", end="")
            i -= 1
            input(" [continue]")
        elif answer == "w" or answer.startswith("write"):
            _write_dialogue(font, rule_base, path, writer, overwrite, compress, abox, tbox, vocab, lang)
        elif answer == "e" or answer == "exit":
            break

        # next
        i += 1


    if output.size() > 0:
        print("write {} rules in buffer? ({} / [{}]): ".format(output.size(),
                                                            font.bold_first_char("yes"),
                                                            font.bold_first_char("no")),
              end="")

        if input().startswith("y"):
            _write_dialogue(font, rule_base, path+'_buffer{}'.format(int(time())), writer, overwrite,
                            compress, abox, tbox, vocab, lang)
            print("Saved {} of {} rules".format(output.size(), n))
            logger.info("Saved {} of {} rules".format(output.size(), n))

def _write_dialogue(font, rule_set, path, writer, overwrite, compress, abox, tbox, vocab, lang):
    print("[WRITE] ({} / {} / {} / [{}]): ".format(font.bold_first_char("text file"),
                                                   font.bold_first_char("pickle file"),
                                                   font.bold_first_char("both"),
                                                   font.bold_first_char("return")),
          end="")
    answer = input()

    if answer == "t" or answer.startswith("text"):
        writer(rule_set, path+'.rules', overwrite, compress, abox, tbox, vocab, lang)
        print("written to {} !".format(path+'.rules'), end="")
    elif answer == "p" or answer.startswith("pickle"):
        dump(rule_set, path+'.pickle', overwrite)
        print("written to {} !".format(path+'.pickle'), end="")
    elif answer == "b" or answer.startswith("both"):
        writer(rule_set, path+'.rules', overwrite, compress, abox, tbox, vocab, lang)
        print("written to {} !".format(path+'.rules'), end="\n")
        dump(rule_set, path+'.pickle', overwrite)
        print("written to {} !".format(path+'.pickle'), end="")
    else:
        return

    input(" [continue]")

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
