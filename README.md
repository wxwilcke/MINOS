# MINOS
MINing On Semantics

MINoS is a Semantic Web Mining pipeline that facilitates an implementation of a descriptive rule-mining algorithm. The
pipeline consists of two high-level components: a backend and a frontend. All processing and computational steps occur
within the former, whereas the former concerns a CLI to the user. 

Users should first provide a set of constraints. These constraints will be used to automatically generate a suitable
SPARQL query that matches the users' current topic of interest. This query will be used to retrieve a subset from a
local or remote (SPARQL endpoint) Knowledge Graph. Upon the successful retrieval of the subset, its data will be made
suitable for further processing by sampling the semantic contexts of all instances in the data set. These will then be
offered to the rule-mining module, which will generate Semantic Association Rules with support and confidence values.
Once generated, the rules will be presented to the user for evaluation, who may separate the wheat from the chaff by
adding various filters. Finally, the user may choose to store any or all of the rules. 

## USAGE

At present, the pipeline consists of three primary modules.

### Rule Miner
usage: rule\_miner [-h] [-a ABOX] [-d DIRECTIVE] [-i] [-o OUTPUT] -t [TBOX] [-v]

optional arguments:
*  -h, --help            show this help message and exit
*  -a ABOX, --abox ABOX  ABox graph
*  -d DIRECTIVE, --directive DIRECTIVE Directive for rule learning
*  -i, --interactive     Interactive mode
*  -o OUTPUT, --output OUTPUT output path
*  -t TBOX, --tbox TBOX  TBox graph
*  -v, --verbose         increase output verbosity


### Model Evaluator
usage: model\_evaluator [-h] [-f FILTER] [-m MODEL] [-o OUTPUT] [-v]

optional arguments:
*  -h, --help            show this help message and exit
*  -f FILTER, --filter FILTER Custom filter
*  -m MODEL, --model MODEL Rule-based model
*  -o OUTPUT, --output OUTPUT Output path
*  -v, --verbose         Increase output verbosity

### Anomaly Detector
usage: anomaly\_detector [-h] [-a ABOX] [-i] [-m MODEL] [-o OUTPUT] [-v]

optional arguments:
*  -h, --help            show this help message and exit
*  -a ABOX, --abox ABOX  ABox graph
*  -i, --interactive     Interactive mode
*  -m MODEL, --model MODEL Rule-based model
*  -o OUTPUT, --output OUTPUT output path
*  -v, --verbose         increase output verbosity
