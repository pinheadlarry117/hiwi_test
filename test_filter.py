import os
import json
from pathlib import Path
import pandas as pd
from sdv.metadata import Metadata
from sdv.single_table import GaussianCopulaSynthesizer, CTGANSynthesizer
from sdv.evaluation.single_table import run_diagnostic, evaluate_quality
from faker import Faker


#INPUT_FILE = Path(r"C:\Users\Administrator\Downloads\SMX.xlsx")
INPUT_FILE = Path(r"C:\Users\Administrator\Downloads\sampledata_short.csv")
#INPUT_FILE = Path(r"C:\Users\Administrator\Downloads\sampledata.csv")

def save_original_data(
    data: pd.DataFrame,
    results_root: Path,
    filename: str = f"{INPUT_FILE.stem.replace(' ', '_')}_original.csv"
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

def save_filtered_data(
    data: pd.DataFrame,
    results_root: Path,
    filename: str = f"{INPUT_FILE.stem.replace(' ', '_')}_filtered.csv"
) -> Path:
    """
    Save the filtered input dataset under test_results/filtered_data.

    Returns the path of the saved file.
    """
    filtered_dir = results_root / "filtered_data"
    filtered_dir.mkdir(parents=True, exist_ok=True)

    output_path = filtered_dir / filename
    
    subset.to_csv(output_path, index=False)
    print(f"Saved: {output_path}")


    return output_path


# ---------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------

RESULTS_ROOT = Path("test_results")

CTGAN_DIR = RESULTS_ROOT / "CTGAN_results"
GAUSS_DIR = RESULTS_ROOT / "Gauss_results"
METADATA_DIR = RESULTS_ROOT / "metadata"

SUBFOLDERS = ["synthetic_data", "quality_reports", "overall_scores"]

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

#data = pd.read_excel(INPUT_FILE)
data = pd.read_csv(INPUT_FILE)

saved_original_path = save_original_data(data, RESULTS_ROOT)
print(f"✅ Original data saved to: {saved_original_path}")

"""
Faker.seed(0)
fake = Faker()
new_values = []

for _ in data["_Project"]:
    new_values.append(fake.company_suffix())

data["_Project"] = new_values
print(data["_Project"])
"""

location = "Logistic centre"
energy = "electricity"

subset = data[
    (data["LOCATION"] == location) &
    (data["ENERGY_SOURCE"] == energy)
]

saved_filtered_path = save_filtered_data(subset, RESULTS_ROOT)
print(f"✅ Filtered data saved to: {saved_filtered_path}")

data = pd.read_csv(saved_filtered_path)

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

metadata.validate()

for col, info in table.columns.items():
    if info.get("sdtype") == "datetime":

        if col == "DATE":
            fmt = "%Y/%m/%d"

        elif col == "TIMESTAMP":
            fmt = "%Y/%m/%d %H:%M"

        else:
            fmt = None

        metadata.update_column(
            table_name="table",
            column_name=col,
            sdtype="datetime",
            datetime_format=fmt
        )

metadata.save_to_json(
    METADATA_DIR / f"{saved_filtered_path.stem}_metadata.json",
    mode = "overwrite"
)

# ---------------------------------------------------------------------
# Gaussian Copula
# ---------------------------------------------------------------------

gauss = GaussianCopulaSynthesizer(metadata)

print(gauss.get_parameters())


gauss.fit(data)

synthetic_gauss = gauss.sample(NUM_SYNTHETIC_ROWS)

synthetic_gauss['TIMESTAMP'] = pd.to_datetime(
    synthetic_gauss['TIMESTAMP'],
    errors='coerce'
)


# Rebuild DATE from TIMESTAMP
synthetic_gauss['DATE'] = synthetic_gauss['TIMESTAMP'].dt.strftime('%Y/%m/%d')
synthetic_gauss['TIMESTAMP'] = synthetic_gauss['TIMESTAMP'].dt.strftime(
    '%Y/%m/%d %H:%M'
)

synthetic_gauss.to_csv(
    GAUSS_DIR / "synthetic_data" / f"{saved_filtered_path.stem}_gaussian.csv",
    index=False
)

gauss_quality_report = evaluate_quality(data, synthetic_gauss, metadata)
gauss_score = gauss_quality_report.get_score()
pd.DataFrame(
    {"gaussian_quality_score": [gauss_score]}
).to_csv(
    GAUSS_DIR / "overall_scores" / f"{saved_filtered_path.stem.replace(' ', '_')}_gaussian_quality_score.csv",
    index=False
)

    
gauss_quality_report.save(
    GAUSS_DIR / "quality_reports" / f"{saved_filtered_path.stem.replace(' ', '_')}_gaussian_model.pkl"
)

# ---------------------------------------------------------------------
# CTGAN
# ---------------------------------------------------------------------

ctgan = CTGANSynthesizer(metadata)

ctgan.fit(data)

synthetic_ctgan = ctgan.sample(NUM_SYNTHETIC_ROWS)

synthetic_ctgan['TIMESTAMP'] = pd.to_datetime(
    synthetic_ctgan['TIMESTAMP'],
    errors='coerce'
)

# Rebuild DATE from TIMESTAMP
synthetic_ctgan['DATE'] = synthetic_ctgan['TIMESTAMP'].dt.strftime('%Y/%m/%d')
synthetic_ctgan['TIMESTAMP'] = synthetic_ctgan['TIMESTAMP'].dt.strftime(
    '%Y/%m/%d %H:%M'
)
synthetic_ctgan.to_csv(
    CTGAN_DIR / "synthetic_data" / f"{saved_filtered_path.stem}_ctgan.csv",
    index=False
)

ctgan_quality_report = evaluate_quality(data, synthetic_ctgan, metadata)
ctgan_score = ctgan_quality_report.get_score()
pd.DataFrame(
    {"ctgan_quality_score": [ctgan_score]}
).to_csv(
    CTGAN_DIR / "overall_scores" / f"{saved_filtered_path.stem.replace(' ', '_')}_ctgan_quality_score.csv",
    index=False
)    

ctgan_quality_report.save(
    CTGAN_DIR / "quality_reports" / f"{saved_filtered_path.stem.replace(' ', '_')}_ctgan_model.pkl"
)

# ---------------------------------------------------------------------
# Final Summary
# ---------------------------------------------------------------------

print("✅ SDV pipeline completed successfully")
print(f"📁 Results stored in: {RESULTS_ROOT.resolve()}")