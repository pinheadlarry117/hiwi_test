from pathlib import Path

from ontology_merge.merge import merge_ontologies

ROOT = Path(__file__).resolve().parents[1]

merge_ontologies(
    oeo_path=ROOT / "data" / "input" / "oeo.rdf",
    beo_path=ROOT / "data" / "input" / "beo.rdf",
    mapping_file=ROOT / "data" / "output" / "oeo_beo_matches_above_0.90.csv",
    output_file=ROOT / "data" / "output" / "merged.owl"
)