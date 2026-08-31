from ENERGYBert import *
from owlready2 import *
import pandas as pd

# Load ontologies
onto1 = get_ontology(
    r"C:\Users\yga-hzh\Downloads\oeo1.rdf"
).load()

onto2 = get_ontology(
    r"C:\Users\yga-hzh\Downloads\beo1.rdf"
).load()

# Read matches
df = pd.read_csv(
    r"C:\Users\yga-hzh\Downloads\hiwi\hiwi_test\oeo_beo_matches_above_0.9.csv"
)

for _, row in df.iterrows():

    c1 = IRIS[row["OEO_IRI"]]
    c2 = IRIS[row["BEO_IRI"]]

    c1.equivalent_to.append(c2)

# Save ontology with mappings
onto1.save(file="merged.owl")