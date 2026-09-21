from ontology_merge.compare import compare_ontologies

results = {}

results["added"], results["removed"] = compare_ontologies(
    "data/input/beo.rdf",
    "data/output/merged.owl"
)

"""
print("\nFirst 20 added classes:")
for cls in sorted(map(str, results["added"]))[:20]:
    print(cls)
"""