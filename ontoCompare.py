from rdflib import *
from rdflib.namespace import RDF, RDFS, OWL

before = Graph()
before.parse(
    r"C:\Users\yga-hzh\Downloads\beo1.rdf",
    format="xml"
)

after = Graph()
after.parse(
    r"C:\Users\yga-hzh\Downloads\mergedtest.owl",
    format="xml"
)

def get_classes(g):

    classes = set()

    classes.update(
        g.subjects(RDF.type, OWL.Class)
    )

    classes.update(
        g.subjects(RDFS.subClassOf, None)
    )

    classes.update(
        g.objects(None, RDFS.subClassOf)
    )

    return classes

before_classes = get_classes(before)
after_classes = get_classes(after)

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