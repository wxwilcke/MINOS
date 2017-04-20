#!/usr/bin/python3

import logging
import tarfile
import io
import re


logger = logging.getLogger(__name__)
LANG_DEFAULT = "en"

def get_label(node, knowledge_graphs=[], lang=LANG_DEFAULT, fallback=True):
    """ Retrieve label in preferred language

    :param node: a resource
    :param knowledge_graphs: a list of KnowledgeGraph instances

    :returns: a string
    """
    labels = []
    if len(knowledge_graphs) >= 0:
        for knowledge_graph in knowledge_graphs:
            if knowledge_graphs is not None:
                labels.extend(knowledge_graph.graph.preferredLabel(node, lang))

        if len(labels) <= 0 and lang != LANG_DEFAULT and fallback:
            for knowledge_graph in knowledge_graphs:
                if knowledge_graphs is not None:
                    labels.extend(knowledge_graph.graph.preferredLabel(node, LANG_DEFAULT))

    label = node.toPython()
    if len(labels) <= 0:
        match = re.match('.*[/|#](.*)', label)
        if match is not None:
            label = match.group(1)
    else:
        label = labels[0][1].toPython()

    return label

def write(output=[], path="./of/latest", overwrite=True, compress=False, printer=None, abox=None, tbox=None, vocab=None,
         lang=None):
    """ Write a list of items

    :param output: a list of items
    :param path: file path to write to
    :param overwrite: overwrite file at path if exists
    :param compress: compress output as tar

    :returns: none
    """
    buff = ""
    for item in output:
        buff += printer(item, abox, tbox, vocab, lang) + "\n"
    buff += "<EOF>"

    mode = 'w' if overwrite else 'x'
    logger.info("Writing (mode {}, compress = {}) to {}".format(mode, compress, path))
    if compress:
        _tar_write(buff, path+".tar", mode+":bz2")
    else:
        _raw_write(buff, path, mode)

def _raw_write(buff, path, mode):
    with open(path, mode) as f:
        f.write(buff)

def _tar_write(buff, path, mode):
    info = tarfile.TarInfo(name=re.match('.*/(.*).tar', path).group(1))
    info.size = len(buff)
    info.type = tarfile.REGTYPE
    with tarfile.open(path, mode) as t:
        t.addfile(tarinfo=info, fileobj=io.BytesIO(buff.encode('utf8')))
