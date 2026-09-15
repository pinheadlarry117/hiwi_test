from rdflib import *
from rdflib.namespace import RDF, RDFS, OWL
from rdflib import BNode

before = Graph()
before.parse(
    r"C:\Users\yga-hzh\Downloads\beo1.rdf",
    format="xml"
)

after = Graph()
after.parse(
    r"C:\Users\yga-hzh\Downloads\mergetest2.rdf",
    format="xml"
)


def get_named_classes(g):
    classes = set()

    for c in g.subjects(RDF.type, OWL.Class):
        if not isinstance(c, BNode):
            classes.add(c)

    return classes

before_classes = get_named_classes(before)
after_classes = get_named_classes(after)

added_classes = after_classes - before_classes
removed_classes = before_classes - after_classes

print("Classes before:", len(before_classes))
print("Classes after :", len(after_classes))
print("Added classes :", len(added_classes))
print("Removed classes:", len(removed_classes))

#print("\n===== Added Classes =====")
#for c in sorted(map(str, added_classes)):
#    print(c)

#print("\n===== Removed Classes =====")
#for c in sorted(map(str, removed_classes)):
#    print(c)

oeo_count = 0

for c in after_classes:
    if "openenergy-platform.org/ontology/oeo" in str(c):
        oeo_count += 1

print("OEO classes in merged ontology:", oeo_count)
