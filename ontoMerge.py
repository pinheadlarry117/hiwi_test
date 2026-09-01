from ENERGYBert import *
from owlready2 import *
import pandas as pd

# Load ontologies
onto1 = get_ontology(
    r"C:\Users\yga-hzh\Downloads\oeo1.rdf"
).load()

onto2 = get_ontology(
    r"C:\Users\yga-hzh\Downloads\beo1.rdf"
).load()


#delete same class, beo as mother class, oeo as child class



# Read matches
df = pd.read_csv(
    r"C:\Users\yga-hzh\Downloads\hiwi\hiwi_test\oeo_beo_matches_above_0.9.csv"
)

for _, row in df.iterrows():

    oeo_class = IRIS[row["OEO_IRI"]]
    beo_class = IRIS[row["BEO_IRI"]]

    print(f"Replacing {oeo_class.name} with {beo_class.name}")

    # Replace OEO class in subclass relations
    for child in list(oeo_class.subclasses()):
        for parent in child.is_a:
            if parent == oeo_class:
                child.is_a.remove(parent)

        if beo_class not in child.is_a:
            child.is_a.append(beo_class)

    # Transfer class restrictions involving object/data properties
    for cls in onto1.classes():
        for parent in list(cls.is_a):
            if hasattr(parent, "value") and parent.value == oeo_class:
                cls.is_a.remove(parent)

                try:
                    new_restriction = type(parent)(
                        parent.property,
                        parent.type,
                        beo_class
                    )
                    cls.is_a.append(new_restriction)
                except:
                    pass

            elif parent == oeo_class:
                cls.is_a.remove(parent)
                cls.is_a.append(beo_class)

    # Move instances to BEO class
    for inst in list(oeo_class.instances()):
        if oeo_class in inst.is_a:
            inst.is_a.remove(oeo_class)
        if beo_class not in inst.is_a:
            inst.is_a.append(beo_class)

    # Delete OEO class
    destroy_entity(oeo_class)

# Save merged ontology
onto1.save(
    file=r"C:\Users\yga-hzh\Downloads\merged1.owl",
    format="rdfxml"
)