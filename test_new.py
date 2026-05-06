import os
import json
from pathlib import Path
import pandas as pd
from sdv.metadata import Metadata
from sdv.single_table import GaussianCopulaSynthesizer, CTGANSynthesizer
from sdv.evaluation.single_table import run_diagnostic, evaluate_quality
from faker import Faker
from faker.providers import BaseProvider
from sdv.metadata import SingleTableMetadata



"""
def anonymize_project(val):
    if val not in project_map:
        project_map[val] = fake.company_suffix()  # or fake.word(), fake.bs()
    return project_map[val]
"""

def save_original_data(
    data: pd.DataFrame,
    results_root: Path,
    filename: str = "original_data.csv"
) -> Path:
    """
    Save the original input dataset under test_results/original_data.

    Returns the path of the saved file.
    """
    original_dir = results_root / "original_data"
    original_dir.mkdir(parents=True, exist_ok=True)

    output_path = original_dir / filename
    data.to_csv(output_path, index=False)

    return output_path


# ---------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------

RESULTS_ROOT = Path("test_results")

CTGAN_DIR = RESULTS_ROOT / "CTGAN_results"
GAUSS_DIR = RESULTS_ROOT / "Gauss_results"
METADATA_DIR = RESULTS_ROOT / "metadata"

SUBFOLDERS = ["synthetic_data", "quality_reports", "overall_scores"]

INPUT_FILE = Path(r"C:\Users\Administrator\Downloads\SMX.xlsx")
#INPUT_FILE = Path(r"C:\Users\Administrator\Downloads\sampledata.xlsx")
#INPUT_FILE = Path(r"C:\Users\Administrator\Downloads\sampledata.csv")
RANDOM_STATE = 42
NUM_SYNTHETIC_ROWS = 20

# ---------------------------------------------------------------------
# Create Folder Structure
# ---------------------------------------------------------------------

for base in [CTGAN_DIR, GAUSS_DIR]:
    for sub in SUBFOLDERS:
        os.makedirs(base / sub, exist_ok=True)

os.makedirs(METADATA_DIR, exist_ok=True)

# ---------------------------------------------------------------------
# Load Data
# ---------------------------------------------------------------------

data = pd.read_excel(INPUT_FILE)
#data = pd.read_csv(INPUT_FILE)

fake = Faker()

new_values = []

for _ in data["_Project"]:
    new_values.append(fake.company_suffix())

data["_Project"] = new_values
print(data["_Project"])

saved_original_path = save_original_data(data, RESULTS_ROOT)
print(f"✅ Original data saved to: {saved_original_path}")

# ---------------------------------------------------------------------
# Detect + Save Metadata
# ---------------------------------------------------------------------

metadata = Metadata.detect_from_dataframe(
    data,
    table_name="table"
)

for col, info in metadata.tables["table"].columns.items():
    print(col, "→", info)


table = metadata.tables["table"]


"""
metadata.update_column(
    table_name="table",
    column_name="_Country",
    sdtype="country",
    pii=True
)

metadata.update_column(
    table_name="table",
    column_name="_City",
    sdtype="city",
    pii=True
)

metadata.update_column(
    table_name="table",
    column_name="_Actor_type",
    sdtype="text",
    pii=True
)

metadata.update_column(
    table_name="table",
    column_name="_GPS",
    sdtype="text",
    pii=True
)
"""
#datetime can't be pii
#metadata.update_column(
#    table_name="table",
#    column_name="__SMXtimestamp",
#    sdtype="datetime",
#    pii=True
#)


metadata.validate()

# Relax datetime strictness
for col, info in table.columns.items():
    if info.get("sdtype") == "datetime":
        metadata.update_column(
            table_name="table",
            column_name=col,
            sdtype="datetime",
            datetime_format=None
        )


with open(METADATA_DIR / "detected_metadata.json", "w", encoding="utf-8") as f:
    json.dump(metadata.to_dict(), f, indent=2)

# ---------------------------------------------------------------------
# Gaussian Copula
# ---------------------------------------------------------------------

gauss = GaussianCopulaSynthesizer(metadata,
                                  locales=["fr_CA"],)

print(gauss.get_parameters())


gauss.fit(data)

synthetic_gauss = gauss.sample(NUM_SYNTHETIC_ROWS)

synthetic_gauss.to_csv(
    GAUSS_DIR / "synthetic_data" / "synthetic_gaussian.csv",
    index=False
)

gauss_quality_report = evaluate_quality(data, synthetic_gauss, metadata)
gauss_score = gauss_quality_report.get_score()
pd.DataFrame(
    {"gaussian_quality_score": [gauss_score]}
).to_csv(
    GAUSS_DIR / "overall_scores" / "gaussian_quality_score.csv",
    index=False
)

    
gauss_quality_report.save(
    GAUSS_DIR / "quality_reports" / "gaussian_model.pkl"
)

# ---------------------------------------------------------------------
# CTGAN
# ---------------------------------------------------------------------

ctgan = CTGANSynthesizer(metadata)

ctgan.fit(data)

synthetic_ctgan = ctgan.sample(NUM_SYNTHETIC_ROWS)

synthetic_ctgan.to_csv(
    CTGAN_DIR / "synthetic_data" / "synthetic_ctgan.csv",
    index=False
)

ctgan_quality_report = evaluate_quality(data, synthetic_ctgan, metadata)
ctgan_score = ctgan_quality_report.get_score()
pd.DataFrame(
    {"ctgan_quality_score": [ctgan_score]}
).to_csv(
    CTGAN_DIR / "overall_scores" / "ctgan_quality_score.csv",
    index=False
)    

ctgan_quality_report.save(
    CTGAN_DIR / "quality_reports" / "ctgan_model.pkl"
)

# ---------------------------------------------------------------------
# Final Summary
# ---------------------------------------------------------------------

print("✅ SDV pipeline completed successfully")
print(f"📁 Results stored in: {RESULTS_ROOT.resolve()}")