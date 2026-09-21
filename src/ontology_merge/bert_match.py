from sentence_transformers import SentenceTransformer
from sentence_transformers.util import cos_sim
from transformers import AutoTokenizer, AutoModel
from rdflib import Graph
from rdflib.namespace import RDF, OWL, RDFS
import pandas as pd


def load_classes(ontology_path):
    g = Graph()
    g.parse(ontology_path)

    classes = []

    for cls in g.subjects(RDF.type, OWL.Class):
        label = g.value(cls, RDFS.label)

        if label:
            classes.append({
                "label": str(label),
                "iri": str(cls)
            })

    return classes


def load_energybert(model_path):
    tokenizer = AutoTokenizer.from_pretrained(model_path)

    AutoModel.from_pretrained(
        model_path,
        device_map="auto"
    )

    model = SentenceTransformer(model_path)

    return tokenizer, model


def find_matches(
    oeo_path,
    beo_path,
    model_path,
    threshold=0.9
):
    _, model = load_energybert(model_path)

    oeo_classes = load_classes(oeo_path)
    beo_classes = load_classes(beo_path)

    print(f"OEO classes: {len(oeo_classes)}")
    print(f"BEO classes: {len(beo_classes)}")

    emb_oeo = model.encode(
        [c["label"] for c in oeo_classes],
        convert_to_tensor=True
    )

    emb_beo = model.encode(
        [c["label"] for c in beo_classes],
        convert_to_tensor=True
    )

    similarities = cos_sim(
        emb_oeo,
        emb_beo
    )

    matches = []

    for i, oeo_cls in enumerate(oeo_classes):
        for j, beo_cls in enumerate(beo_classes):

            score = similarities[i, j].item()

            if score > threshold:
                matches.append({
                    "Similarity": score,
                    "OEO_Label": oeo_cls["label"],
                    "OEO_IRI": oeo_cls["iri"],
                    "BEO_Label": beo_cls["label"],
                    "BEO_IRI": beo_cls["iri"]
                })

    return matches, similarities, oeo_classes, beo_classes