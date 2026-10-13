import json
from pathlib import Path

from rdflib import Graph, RDF, RDFS, OWL


def local_name(uri):
    uri = str(uri)
    if "#" in uri:
        return uri.split("#")[-1]
    return uri.rstrip("/").split("/")[-1]


def ontology_to_json(input_file: str | Path) -> dict:
    g = Graph()
    g.parse(str(input_file))

    result = {
        "classes": [],
        "object_properties": [],
        "datatype_properties": [],
    }

    # Classes
    for cls in g.subjects(RDF.type, OWL.Class):
        result["classes"].append(
            {
                "name": local_name(cls),
                "uri": str(cls),
                "label": str(g.value(cls, RDFS.label) or ""),
                "comment": str(g.value(cls, RDFS.comment) or ""),
            }
        )

    # Object Properties
    for prop in g.subjects(RDF.type, OWL.ObjectProperty):
        result["object_properties"].append(
            {
                "name": local_name(prop),
                "uri": str(prop),
                "domain": (
                    local_name(g.value(prop, RDFS.domain))
                    if g.value(prop, RDFS.domain)
                    else None
                ),
                "range": (
                    local_name(g.value(prop, RDFS.range))
                    if g.value(prop, RDFS.range)
                    else None
                ),
            }
        )

    # Datatype Properties
    for prop in g.subjects(RDF.type, OWL.DatatypeProperty):
        result["datatype_properties"].append(
            {
                "name": local_name(prop),
                "uri": str(prop),
                "domain": (
                    local_name(g.value(prop, RDFS.domain))
                    if g.value(prop, RDFS.domain)
                    else None
                ),
                "range": str(g.value(prop, RDFS.range))
                if g.value(prop, RDFS.range)
                else None,
            }
        )

    return result


def save_json(data: dict, output_file: str | Path) -> None:
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)