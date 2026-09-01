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

oeo_classes = []
for cls in g_oeo.subjects(RDF.type, OWL.Class):
    label_oeo = g_oeo.value(cls, RDFS.label)

    if label_oeo:
        oeo_classes.append({
            "label": str(label_oeo),
            "iri": str(cls)
        })

g_beo = Graph()
g_beo.parse(
    r"C:\Users\yga-hzh\Downloads\beo1.rdf"
)

beo_classes = []
for cls in g_beo.subjects(RDF.type, OWL.Class):
    label_beo = g_beo.value(cls, RDFS.label)

    if label_beo:
        beo_classes.append({
            "label": str(label_beo),
            "iri": str(cls)
        })

print(len(oeo_classes))
print(len(beo_classes))
print(oeo_classes[:10])
print(beo_classes[:10])

emb_oeo = model_sen.encode(
    [cls["label"] for cls in oeo_classes],
    convert_to_tensor=True
)

emb_beo = model_sen.encode(
    [cls["label"] for cls in beo_classes],
    convert_to_tensor=True
)
similarities_oeobeo = cos_sim(emb_oeo, emb_beo)
print("Ontology similarities for oeo and beo: ", similarities_oeobeo)

# Convert tensor to DataFrame
df = pd.DataFrame(
    similarities_oeobeo.cpu().numpy(),
    index=[cls["label"] for cls in oeo_classes],
    columns=[cls["label"] for cls in beo_classes]
)

if not Path("hiwi_test/oeo_beo_similarity_matrix.csv").exists():
    df.to_csv("hiwi_test/oeo_beo_similarity_matrix.csv", index=False)


threshold = 0.9

high_similarity_matches = []

for i, oeo_cls in enumerate(oeo_classes):
    for j, beo_cls in enumerate(beo_classes):
        score = similarities_oeobeo[i, j].item()

        if score > threshold:
            high_similarity_matches.append({
                "Similarity": score,
                "OEO_Label": oeo_cls["label"],
                "OEO_IRI": oeo_cls["iri"],
                "BEO_Label": beo_cls["label"],
                "BEO_IRI": beo_cls["iri"]
            })

high_similarity_matches.sort(reverse=True, key=lambda x: x["Similarity"])

print(f"Found {len(high_similarity_matches)} matches with similarity > {threshold}\n")

for match in high_similarity_matches:
    print(f"Similarity: {match['Similarity']:.4f}")
    print(f"OEO: {match['OEO_Label']} ({match['OEO_IRI']})")
    print(f"BEO: {match['BEO_Label']} ({match['BEO_IRI']})")
    print("-" * 50)
    
matches_df = pd.DataFrame(high_similarity_matches)

matches_df.sort_values(
    by="Similarity",
    ascending=False,
    inplace=True
)

matches_df.to_csv(
    "hiwi_test/oeo_beo_matches_above_0.9.csv",
    index=False
)


