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

arguments:
*  -h, --help            _show this help message and exit_
*  -a ABOX, --abox ABOX  _ABox graph_
*  -d DIRECTIVE, --directive DIRECTIVE _Directive for rule learning_
*  -i, --interactive     _Interactive mode_
*  -o OUTPUT, --output OUTPUT _output path_
*  -t TBOX, --tbox TBOX  _TBox graph_
*  -v, --verbose         _increase output verbosity_


### Model Evaluator
usage: model\_evaluator [-h] [-f FILTER] [-m MODEL] [-o OUTPUT] [-v]

arguments:
*  -h, --help            _show this help message and exit_
*  -f FILTER, --filter FILTER _Custom filter_
*  -m MODEL, --model MODEL _Rule-based model_
*  -o OUTPUT, --output OUTPUT _Output path_
*  -v, --verbose         _Increase output verbosity_

### Anomaly Detector
usage: anomaly\_detector [-h] [-a ABOX] [-i] [-m MODEL] [-o OUTPUT] [-v]

arguments:
*  -h, --help            _show this help message and exit_
*  -a ABOX, --abox ABOX  _ABox graph_
*  -i, --interactive     _Interactive mode)_
*  -m MODEL, --model MODEL _Rule-based model_
*  -o OUTPUT, --output OUTPUT _output path_
*  -v, --verbose         _increase output verbosity_
