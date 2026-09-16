from rdflib import *
from rdflib.namespace import RDF, RDFS, OWL
from rdflib import BNode

before = Graph()
#before.parse(
#    r"C:\Users\yga-hzh\Downloads\beo1.rdf",
#    format="xml"
#)

before.parse(
    r"C:\Users\75909\Downloads\beo.rdf",
    format="xml"
)


after = Graph()
#after.parse(
#    r"C:\Users\yga-hzh\Downloads\mergetest2.rdf",
#    format="xml"
#)

after.parse(
    r"C:\Users\75909\Downloads\mergedtest_all.owl",
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
