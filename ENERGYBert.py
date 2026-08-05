from sentence_transformers import SentenceTransformer
from PyPDF2 import PdfReader
from transformers import AutoTokenizer, AutoModel
import re
from sentence_transformers.util import cos_sim
from rdflib import Graph
from rdflib.namespace import RDF, OWL, RDFS, SKOS
import pandas as pd
from pathlib import Path

#tokenizer = AutoTokenizer.from_pretrained("ontology/EnergyBert")
#model = AutoModel.from_pretrained("ontology/EnergyBert", device_map="auto")
tokenizer = AutoTokenizer.from_pretrained(r"C:\Users\yga-hzh\Downloads\ENERGYBert")
model = AutoModel.from_pretrained(r"C:\Users\yga-hzh\Downloads\ENERGYBert", device_map="auto")

#model = SentenceTransformer("ontology/EnergyBert")
model_sen = SentenceTransformer(r"C:\Users\yga-hzh\Downloads\ENERGYBert")

r"""

#test EnergyBert model with ontology terms
ontology_a = [
    "PowerGeneration",
    "ElectricityConsumption",
    "CarbonDioxide Emission",
]

ontology_b = [
    "EnergyProduction",
    "PowerUsage",
    "CO2 Output"
]

emb_a = model_sen.encode(
    ontology_a,
    convert_to_tensor=True
)

emb_b = model_sen.encode(
    ontology_b,
    convert_to_tensor=True
)

similarities = cos_sim(emb_a, emb_b)
print("Ontology similarities for ontology a and b: ", similarities)

#test EnergyBert model with ontology 
g = Graph()
g.parse(r"C:\Users\yga-hzh\Downloads\pizza.owl.xml")

#Extract labels
pizza_labels = []
for cls in g.subjects(RDF.type, OWL.Class):
    label_pizza = g.value(cls, RDFS.label)

    if label_pizza:
        pizza_labels.append(str(label_pizza))

print(pizza_labels[:])

g_pd = Graph()
g_pd.parse(
    r"C:\Users\yga-hzh\Downloads\pd-owl (1).ttl",
    format="turtle"
)
print(len(g_pd))

pd_labels = []
for cls in g_pd.subjects(RDF.type, RDFS.Class):
    label_pd = g_pd.value(cls, SKOS.prefLabel)

    if label_pd:
        pd_labels.append(str(label_pd))

g_loc = Graph()
g_loc.parse(
    r"C:\Users\yga-hzh\Downloads\loc-owl (1).ttl",
    format="turtle"
)
print(len(g_loc))

loc_labels = []
for cls in g_loc.subjects(RDF.type, RDFS.Class):
    label_loc = g_loc.value(cls, SKOS.prefLabel)

    if label_loc:
        loc_labels.append(str(label_loc))

print(pd_labels[:10])
print(loc_labels[:10])

emb_pizza = model_sen.encode(
    pizza_labels,
    convert_to_tensor=True
)

emb_pd = model_sen.encode(
    pd_labels,
    convert_to_tensor=True
)

emb_loc = model_sen.encode(
    loc_labels,
    convert_to_tensor=True
)

similarities_pdpizza = cos_sim(emb_pizza, emb_pd)
similarities_pdloc = cos_sim(emb_pd, emb_loc)
similarities_pizzaloc = cos_sim(emb_pizza, emb_loc)
print("Ontology similarities for pd and pizza: ", similarities_pdpizza)
print("Ontology similarities for pd and loc: ", similarities_pdloc)
print("Ontology similarities for pizza and loc: ", similarities_pizzaloc)
"""

g_oeo = Graph()
g_oeo.parse(
    r"C:\Users\yga-hzh\Downloads\oeo1.rdf"
)

oeo_labels = []
for cls in g_oeo.subjects(RDF.type, OWL.Class):
    label_oeo = g_oeo.value(cls, RDFS.label)

    if label_oeo:
        oeo_labels.append(str(label_oeo))

g_beo = Graph()
g_beo.parse(
    r"C:\Users\yga-hzh\Downloads\beo1.rdf"
)

beo_labels = []
for cls in g_beo.subjects(RDF.type, OWL.Class):
    label_beo = g_beo.value(cls, RDFS.label)

    if label_beo:
        beo_labels.append(str(label_beo))

print(len(oeo_labels))
print(len(beo_labels))
print(oeo_labels[:10])
print(beo_labels[:10])

emb_oeo = model_sen.encode(
    oeo_labels,
    convert_to_tensor=True
)

emb_beo = model_sen.encode(
    beo_labels,
    convert_to_tensor=True
)
similarities_oeobeo = cos_sim(emb_oeo, emb_beo)
print("Ontology similarities for oeo and beo: ", similarities_oeobeo)

# Convert tensor to DataFrame
df = pd.DataFrame(
    similarities_oeobeo.cpu().numpy(),
    index=oeo_labels,
    columns=beo_labels
)

if not Path("hiwi_test/oeo_beo_similarity_matrix.csv").exists():
    df.to_csv("hiwi_test/oeo_beo_similarity_matrix.csv", index=False)

results = []

for i, oeo_label in enumerate(oeo_labels):
    for j, beo_label in enumerate(beo_labels):
        results.append(
            (similarities_oeobeo[i, j].item(), oeo_label, beo_label)
        )

results.sort(reverse=True, key=lambda x: x[0])

print("\nTop 20 Matches:")
for score, oeo, beo in results[:20]:
    print(f"Score: {score:.4f}")
    print(f"OEO: {oeo}")
    print(f"BEO: {beo}")
    print("-" * 50)