from owlready2 import *
import pandas as pd
import re

# --------------------------------------------------
# Load ontologies
# --------------------------------------------------
oeo = get_ontology(
    r"C:\Users\yga-hzh\Downloads\oeo1.rdf"
).load()

beo = get_ontology(
    r"C:\Users\yga-hzh\Downloads\beo1.rdf"
).load()

# --------------------------------------------------
# Load mappings
# --------------------------------------------------
df = pd.read_csv(
    r"C:\Users\yga-hzh\Downloads\hiwi\hiwi_test\oeo_beo_matches_above_0.9.csv"
)

# --------------------------------------------------
# Extract IRIs from HTML strings if necessary
# --------------------------------------------------
def extract_iri(value):

    value = str(value)

    match = re.search(r'href="([^"]+)"', value)

    if match:
        return match.group(1)

    return value.strip()

df["OEO_IRI"] = df["OEO_IRI"].apply(extract_iri)
df["BEO_IRI"] = df["BEO_IRI"].apply(extract_iri)

# --------------------------------------------------
# Keep only the best match for each OEO class
# --------------------------------------------------
df = df.sort_values(
    by="Similarity",
    ascending=False
)

df = df.drop_duplicates(
    subset=["OEO_IRI"],
    keep="first"
)

print("Mappings used:", len(df))

# --------------------------------------------------
# Merge
# --------------------------------------------------
merged_count = 0

for _, row in df.iterrows():

    try:

        oeo_class = IRIS[row["OEO_IRI"]]
        beo_class = IRIS[row["BEO_IRI"]]

        if oeo_class is None:
            print("OEO class not found:", row["OEO_IRI"])
            continue

        if beo_class is None:
            print("BEO class not found:", row["BEO_IRI"])
            continue

        print(
            f"Merging "
            f"{oeo_class.label.first() if oeo_class.label else oeo_class.name}"
            f" --> "
            f"{beo_class.label.first() if beo_class.label else beo_class.name}")

        # ------------------------------------------
        # Move subclasses
        # ------------------------------------------
        for child in list(oeo_class.subclasses()):

            if oeo_class in child.is_a:
                child.is_a.remove(oeo_class)

            if beo_class not in child.is_a:
                child.is_a.append(beo_class)

        # ------------------------------------------
        # Replace references in both ontologies
        # ------------------------------------------
        classes_to_check = (
            list(oeo.classes()) +
            list(beo.classes())
        )

        for cls in classes_to_check:

            for parent in list(cls.is_a):

                # direct superclass
                if parent == oeo_class:

                    cls.is_a.remove(parent)

                    if beo_class not in cls.is_a:
                        cls.is_a.append(beo_class)

                # restrictions
                elif isinstance(parent, Restriction):

                    if getattr(parent, "value", None) == oeo_class:

                        cls.is_a.remove(parent)

                        try:

                            new_rest = type(parent)(
                                parent.property,
                                parent.type,
                                beo_class
                            )

                            cls.is_a.append(new_rest)

                        except Exception as e:
                            print(
                                f"Restriction error: {e}"
                            )

        # ------------------------------------------
        # Move individuals
        # ------------------------------------------
        for ind in list(oeo_class.instances()):

            if oeo_class in ind.is_a:
                ind.is_a.remove(oeo_class)

            if beo_class not in ind.is_a:
                ind.is_a.append(beo_class)

        # ------------------------------------------
        # Copy labels
        # ------------------------------------------
        try:
            for label in oeo_class.label:
                if label not in beo_class.label:
                    beo_class.label.append(label)
        except:
            pass

        # ------------------------------------------
        # Copy comments
        # ------------------------------------------
        try:
            for comment in oeo_class.comment:
                if comment not in beo_class.comment:
                    beo_class.comment.append(comment)
        except:
            pass

        # ------------------------------------------
        # Delete OEO class
        # ------------------------------------------
        destroy_entity(oeo_class)

        merged_count += 1

    except Exception as e:
        print("\nRestriction error")
        print("Class:", cls)
        print("Restriction:", parent)
        print("Property:", parent.property)
        print("Type:", parent.type)
        print("Value:", getattr(parent, "value", None))
        print(e)

print(f"\nMerged classes: {merged_count}")

# --------------------------------------------------
# Save merged ontology
# --------------------------------------------------
beo.save(
    file=r"C:\Users\yga-hzh\Downloads\mergedtest.owl",
    format="rdfxml"
)

print("Merged ontology saved.")