from sentence_transformers import SentenceTransformer
from PyPDF2 import PdfReader
from transformers import AutoTokenizer, AutoModel
import re
from sentence_transformers.util import cos_sim
from rdflib import Graph
from rdflib.namespace import RDF, OWL, RDFS, SKOS

#tokenizer = AutoTokenizer.from_pretrained("ontology/EnergyBert")
#model = AutoModel.from_pretrained("ontology/EnergyBert", device_map="auto")
tokenizer = AutoTokenizer.from_pretrained(r"C:\Users\yga-hzh\Downloads\ENERGYBert")
model = AutoModel.from_pretrained(r"C:\Users\yga-hzh\Downloads\ENERGYBert", device_map="auto")

pdf_path = r"C:\Users\yga-hzh\Downloads\24S-202.pdf"
reader = PdfReader(pdf_path)

text = ""

for page in reader.pages:
    page_text = page.extract_text()
    if page_text:
        text += page_text + "\n"

#print(text)

#model = SentenceTransformer("ontology/EnergyBert")
model_sen = SentenceTransformer(r"C:\Users\yga-hzh\Downloads\ENERGYBert")

"""
sentences = [
    "That is a happy person",
    "That is a happy dog",
    "That is a very happy person",
    "Today is a sunny day"
]
"""

embedding = model_sen.encode(text)

#similarities = model.similarity(embeddings, embeddings)
#print(similarities.shape)
#print(similarities)
print("Embedding shape:", embedding.shape)

paragraphs = [
    p.strip()
    for p in re.split(r'\.\s+', text)
    if len(p.strip()) > 10
]

print(len(paragraphs))
embeddings = model_sen.encode(paragraphs)

print(f"Found {len(paragraphs)} paragraphs")

query = "Nuclear power plant safety and regulations"

query_embedding = model_sen.encode(
    query,
    convert_to_tensor=True
)

paragraph_embeddings = model_sen.encode(
    paragraphs,
    convert_to_tensor=True
)

scores = model_sen.similarity(
    query_embedding,
    paragraph_embeddings
)[0]

top_indices = scores.argsort(descending=True)[:5]

for idx in top_indices:
    print("\nScore:", float(scores[idx]))
    print(paragraphs[int(idx)])


#test EnergyBert model with ontology terms
ontology_a = [
    "PowerGeneration",
    "ElectricityConsumption",
    "CarbonEmission"
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
print("Ontology similarities: ", similarities)

#test EnergyBert model with ontology 
g = Graph()
g.parse(r"C:\Users\yga-hzh\Downloads\pizza.owl.xml")

#for s, p, o in g:
#    print(s, p, o)

#Extract labels
for cls in g.subjects(RDF.type, OWL.Class):
    label = g.value(cls, RDFS.label)

    if label:
        #print(label)
        pass
    else:
        #print(cls)
        pass


g_pd = Graph()
g_pd.parse(
    r"C:\Users\yga-hzh\Downloads\pd-owl (1).ttl",
    format="turtle"
)
print(len(g_pd))


for cls in g_pd.subjects(RDF.type, RDFS.Class):
    label_pd = g_pd.value(cls, SKOS.prefLabel)

    if label_pd:
        print(label_pd)
    else:
        print(cls)


g_loc = Graph()
g_loc.parse(
    r"C:\Users\yga-hzh\Downloads\loc-owl (1).ttl",
    format="turtle"
)
print(len(g_loc))


for cls in g_loc.subjects(RDF.type, RDFS.Class):
    label_loc = g_loc.value(cls, SKOS.prefLabel)

    if label_loc:
        print(label_loc)
    else:
        print(cls)

pd_classes = [
    str(cls)
    for cls in g_pd.subjects(RDF.type, RDFS.Class)
]

loc_classes = [
    str(cls)
    for cls in g_loc.subjects(RDF.type, RDFS.Class)
]

emb_pd = model_sen.encode(
    pd_classes,
    convert_to_tensor=True
)

emb_loc = model_sen.encode(
    loc_classes,
    convert_to_tensor=True
)

similarities = cos_sim(emb_pd, emb_loc)
print("Ontology similarities: ", similarities)