#!/usr/bin/python3

def write(output=[], path="./", overwrite=True):
    mode = 'w' if overwrite else 'x'

    with open(path, mode) as f:
        for rule in output:
            f.write(rule_to_string(rule)+"\n")

def rule_to_string(irule):
    consequent = """\t     {}""".format("""\n\t AND """.join(
        ["({}, {})".format(p, o) for p, o in irule.rule.consequent]))

    string = """[{}]
    \tIF   {}
    \tTHEN {}
     Support:    {}
     Confidence: {}""".format(irule.rule.ctype,
                              irule.rule.antecedent,
                              consequent,
                              irule.support,
                              irule.confidence)

    return string
