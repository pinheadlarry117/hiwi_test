# Hiwi

Consist of two part: Ontology merge and synthetic data related 
Ontology merge are scripts for matching, comparing, and merging ontologies.
Synthetic data related are scripts for parsing, generating synthetic data and letting llm analize sensitive data.

# Ontology merge

## run_matching.py

compare two ontologies and gives the classes which have similarity beyond certain threshold.

## run_merge.py

merge the two ontologies. Merge the classes beyond threshold and add other classes.

## run_compare.py 

compare the merged output with the original ontology and gives out the number of classes before and after merge and merged classes and added classes.

# Synthetic data related

## run_synthetic_data.py

generate synthetic data.

## run_cim_parser.py

parse cim data

## run_LLM.py

run LLM to read data then gives out the sensitive data which should be anonymized.