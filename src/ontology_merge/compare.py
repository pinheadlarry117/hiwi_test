from rdflib import Graph, BNode
from rdflib.namespace import RDF, OWL


def get_named_classes(g):
    classes = set()

    for c in g.subjects(RDF.type, OWL.Class):
        if not isinstance(c, BNode):
            classes.add(c)

    return classes


def compare_ontologies(before_path, after_path):
    before = Graph()
    before.parse(before_path, format="xml")

    after = Graph()
    after.parse(after_path, format="xml")

    before_classes = get_named_classes(before)
    after_classes = get_named_classes(after)

    added_classes = after_classes - before_classes
    removed_classes = before_classes - after_classes

    print("Classes before:", len(before_classes))
    print("Classes after :", len(after_classes))
    print("Added classes :", len(added_classes))
    print("Removed classes:", len(removed_classes))

    return added_classes, removed_classes


def main():
    before_path = "data/input/beo.rdf"
    after_path = "data/output/mergedtest_all.owl"

    compare_ontologies(
        before_path,
        after_path
    )


if __name__ == "__main__":
    main()