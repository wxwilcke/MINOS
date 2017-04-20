#!/usr/bin/python3

import logging
import rdflib
from auxiliarly.progress_indicator import ProgressIndicator
from .abstract_instruction_set import AbstractInstructionSet


class Filter(AbstractInstructionSet):
    def __init__(self, time=""):
        self.time = time
        self.logger = logging.getLogger(__name__)

    def run(self, model):
        pi = ProgressIndicator(after=" Applying custom filter ")

        filtered_model = []
        for irule in model.model:
            pi.call()
            if not self.is_multirule(irule)\
               and not self.is_unique(irule)\
               and not self.is_common(irule)\
               and not self.is_rare(irule)\
               and not self.has_irrelevant_antecedent(irule)\
               and not self.has_irrelevant_consequent(irule):
                filtered_model += [irule]

        pi.end()
        model.model = filtered_model

        print(" {} rules remaining".format(model.size()))

    def is_common(self, irule):
        return True if irule.support.value >= 0.9 else False

    def is_multirule(self, irule):
        return True if len(irule.rule.consequent) >= 2 else False

    def is_unique(self, irule):
        return True if (irule.support.numerator <= 1 or\
                        irule.confidence.numerator <= 1) else False

    def is_rare(self, irule):
        return True if (irule.support.denominator <= 2 or\
                        irule.confidence.denominator <= 2) else False

    def has_irrelevant_antecedent(self, irule):
        return self.is_irrelevant_predicate(irule.rule.antecedent[0])

    def has_irrelevant_consequent(self, irule):
        for consequent in irule.rule.consequent:
            if self.is_irrelevant_predicate(consequent[0]):
                return True
        return False

    def is_irrelevant_predicate(self, p):
        return True if p == rdflib.namespace.RDF.type\
                or p == rdflib.namespace.RDFS.label\
                or p == rdflib.namespace.OWL.sameAs\
                or p == rdflib.namespace.SKOS.prefLabel\
                or p == rdflib.namespace.SKOS.note\
                or p == rdflib.namespace.SKOS.scopeNote\
                or p == rdflib.namespace.SKOS.inScheme\
                or p == rdflib.namespace.SKOS.topConceptOf\
                or p == rdflib.namespace.DCTERMS.issued\
                or p == rdflib.namespace.DCTERMS.medium\
                or p == rdflib.URIRef("http://www.cidoc-crm.org/cidoc-crm/P48_has_preferred_identifier")\
                or p == rdflib.URIRef("http://www.cidoc-crm.org/cidoc-crm/P1_is_identified_by")\
                or p == rdflib.URIRef("http://www.cidoc-crm.org/cidoc-crm/P3_has_note")\
                or p == rdflib.URIRef("http://www.cidoc-crm.org/cidoc-crm/P70_documents")\
                or p == rdflib.URIRef("http://prismstandard.org/namespaces/basic/2.1/versionIdentifier")\
                or p == rdflib.URIRef("http://www.opengis.net/ont/geosparql#asGML")\
                else False
