from pathlib import Path

from synthetic_data_related.OWL_to_JSON import (
    ontology_to_json,
    save_json,
)


def main():
    ontology_file = Path("data/input/pd-owl.rdf")
    output_file = Path("data/output/pd.json")

    ontology_json = ontology_to_json(ontology_file)
    save_json(ontology_json, output_file)

    print(f"Saved ontology JSON to {output_file}")


if __name__ == "__main__":
    main()