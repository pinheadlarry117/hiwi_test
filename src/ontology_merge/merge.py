from owlready2 import *
import pandas as pd
import re


def extract_iri(value):
    value = str(value)

    match = re.search(r'href="([^"]+)"', value)

    if match:
        return match.group(1)

    return value.strip()


def load_mappings(csv_file):
    df = pd.read_csv(csv_file)

    df["OEO_IRI"] = df["OEO_IRI"].apply(extract_iri)
    df["BEO_IRI"] = df["BEO_IRI"].apply(extract_iri)

    df = df.sort_values(
        by="Similarity",
        ascending=False
    )

    df = df.drop_duplicates(
        subset=["OEO_IRI"],
        keep="first"
    )

    return df


def merge_ontologies(
    oeo_path,
    beo_path,
    mapping_file,
    output_file
):
    oeo = get_ontology(str(oeo_path)).load()
    beo = get_ontology(str(beo_path)).load()

    df = load_mappings(mapping_file)

    print("Mappings used:", len(df))

    merged_count = 0

    for _, row in df.iterrows():

        try:
            oeo_class = IRIS[row["OEO_IRI"]]
            beo_class = IRIS[row["BEO_IRI"]]

            if oeo_class is None or beo_class is None:
                continue

            print(
                f"Merging "
                f"{oeo_class.name} -> "
                f"{beo_class.name}"
            )

            for child in list(oeo_class.subclasses()):

                if oeo_class in child.is_a:
                    child.is_a.remove(oeo_class)

                if beo_class not in child.is_a:
                    child.is_a.append(beo_class)

            for ind in list(oeo_class.instances()):

                if oeo_class in ind.is_a:
                    ind.is_a.remove(oeo_class)

                if beo_class not in ind.is_a:
                    ind.is_a.append(beo_class)

            destroy_entity(oeo_class)

            merged_count += 1

        except Exception as e:
            print("Merge error:", e)

    matched_oeo = set(df["OEO_IRI"])

    for cls in list(oeo.classes()):

        if cls.iri not in matched_oeo:
            with beo:
                cls.namespace = beo

    default_world.save(
        file=str(output_file),
        format="rdfxml"
    )

    print(f"Merged classes: {merged_count}")

    return merged_count
