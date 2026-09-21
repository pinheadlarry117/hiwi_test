from ontology_merge.bert_match import find_matches
import pandas as pd

MODEL_PATH = r"C:\Users\75909\Downloads\ENERGYBert"

OEO_PATH = "data/input/oeo.rdf"
BEO_PATH = "data/input/beo.rdf"

OUTPUT_MATCHES = "data/output/oeo_beo_matches_above_0.90.csv"

matches, similarities, oeo_classes, beo_classes = find_matches(
    OEO_PATH,
    BEO_PATH,
    MODEL_PATH,
    threshold=0.9
)

matches_df = pd.DataFrame(matches)

matches_df.sort_values(
    by="Similarity",
    ascending=False,
    inplace=True
)

matches_df.to_csv(
    OUTPUT_MATCHES,
    index=False
)

print(
    f"Saved {len(matches_df)} matches to "
    f"{OUTPUT_MATCHES}"
)