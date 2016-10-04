#!/usr/bin/python3.5

import logging

from rdflib import Graph
from rdflib.util import guess_format
from SPARQLWrapper import SPARQLWrapper

from models.knowledge_graph import KnowledgeGraph


logger = logging.getLogger(__name__)

def read(local_path=None, remote_path=None, format=None):
    """ Imports a RDF graph from local or remote file.
    Returns a Knowledge Graph
    """

    if local_path is None and remote_path is None:
        raise ValueError("Path cannot be left undefined")
    logger.info("Importing RDF Graph from file")

    path = local_path if local_path is not None else remote_path
    logger.info("Path set to '{}'".format(path))

    if not format:
        format = guess_format(path)
    logger.info("Format guessed to be '{}'".format(format))

    graph = Graph()
    graph.parse(path, format=format)
    logger.info("RDF Graph ({} facts) succesfully imported".format(len(graph)))

    return KnowledgeGraph(graph)

def query(query_string="", endpoint=""):
    """ Constructs a Knowledge Graph from a SPARQL endpoint and a CONSTRUCT query.
    Returns a Knowledge Graph
    """

    if endpoint == "":
        raise ValueError("Endpoint cannot be left undefined")
    if query_string == "":
        raise ValueError("Query cannot be left undefined")

    logger.info("Importing RDF Graph via SPARQL query")
    logger.info("Endpoint set to '{}'".format(endpoint))
    logger.info("Query set to '{}'".format(query_string))

    try:
        sparql = SPARQLWrapper(endpoint)
        sparql.setQuery(query_string)
        graph = sparql.queryAndConvert()
    except:
        raise RuntimeError("Query Failed")
    logger.info("Query results ({} facts) succesfully retrieved".format(len(graph)))

    return KnowledgeGraph(graph)

if __name__ == "__main__":
    print("RDF import wrapper")
