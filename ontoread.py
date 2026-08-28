from rdflib import Graph, RDF, RDFS, OWL

# OEO
g_oeo = Graph()
g_oeo.parse(r"C:\Users\yga-hzh\Downloads\oeo1.rdf")

print("=== OEO Classes ===")
for cls in g_oeo.subjects(RDF.type, OWL.Class):
    label = g_oeo.value(cls, RDFS.label)

    print(f"Label: {label if label else 'No label'}")
    print(f"URI  : {cls}")
    print()

# BEO
g_beo = Graph()
g_beo.parse(r"C:\Users\yga-hzh\Downloads\beo1.rdf")

print("=== BEO Classes ===")
for cls in g_beo.subjects(RDF.type, OWL.Class):
    label = g_beo.value(cls, RDFS.label)

    print(f"Label: {label if label else 'No label'}")
    print(f"URI  : {cls}")
    print()
