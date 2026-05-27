import os
import json
from pathlib import Path
import pandas as pd
from sdv.metadata import Metadata
from sdv.single_table import GaussianCopulaSynthesizer, CTGANSynthesizer
from sdv.evaluation.single_table import run_diagnostic, evaluate_quality
from faker import Faker



INPUT_FILE = Path(r"C:\Users\Administrator\Downloads\sampledata.csv")



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
    Remove rows without DATE or TIMESTAMP, save dataset under
    test_results/filtered_data, and return the file path.
    """

    #  Replace empty strings with NaN
    data = data.replace("", pd.NA)

    #  Remove rows without DATE or TIMESTAMP
    filtered_data = data.dropna(subset=['DATE', 'TIMESTAMP'])

    # remove time from TIMESTAMP
    filtered_data['TIMESTAMP'] = pd.to_datetime(filtered_data['TIMESTAMP']).dt.date
    filtered_data['TIMESTAMP'] = pd.to_datetime(filtered_data['TIMESTAMP']).dt.strftime('%Y/%m/%d')

    #  Create directory
    filtered_dir = results_root / "filtered_data"
    filtered_dir.mkdir(parents=True, exist_ok=True)

    #  Save cleaned data
    output_path = filtered_dir / filename
    filtered_data.to_csv(output_path, index=False)

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





saved_filtered_path = save_filtered_data(data, RESULTS_ROOT)
print(saved_filtered_path)
print(f"✅ Filtered data saved to: {saved_filtered_path}")

data = pd.read_csv(saved_filtered_path)
print(data)

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
            #fmt = "%Y/%m/%d %H:%M"
            fmt = "%Y/%m/%d"

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

"""
# Rebuild DATE from TIMESTAMP
synthetic_gauss['DATE'] = synthetic_gauss['TIMESTAMP'].dt.strftime('%Y/%m/%d')
synthetic_gauss['TIMESTAMP'] = synthetic_gauss['TIMESTAMP'].dt.strftime(
    '%Y/%m/%d %H:%M'
)
"""
synthetic_gauss.to_csv(
    GAUSS_DIR / "synthetic_data" / f"{saved_filtered_path.stem}_gaussian.csv",
    index=False
)

gauss_quality_report = evaluate_quality(data, synthetic_gauss, metadata)

print(synthetic_gauss)

gauss_score = gauss_quality_report.get_score()

column_name = f"{saved_filtered_path.stem.replace(' ', '_')}_gaussian_quality_score"

df = pd.DataFrame({
    column_name: [gauss_score]
})

output_path = GAUSS_DIR / "overall_scores" / "gaussian_quality_score.csv"

df.to_csv(
    output_path,
    mode='a',                               # append mode
    header=True,
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

"""
# Rebuild DATE from TIMESTAMP
synthetic_ctgan['DATE'] = synthetic_ctgan['TIMESTAMP'].dt.strftime('%Y/%m/%d')
synthetic_ctgan['TIMESTAMP'] = synthetic_ctgan['TIMESTAMP'].dt.strftime(
    '%Y/%m/%d %H:%M'
)
"""

synthetic_ctgan.to_csv(
    CTGAN_DIR / "synthetic_data" / f"{saved_filtered_path.stem}_ctgan.csv",
    index=False
)

ctgan_quality_report = evaluate_quality(data, synthetic_ctgan, metadata)
ctgan_score = ctgan_quality_report.get_score()

column_name = f"{saved_filtered_path.stem.replace(' ', '_')}_ctgan_quality_score"
df = pd.DataFrame({
    column_name: [ctgan_score]
})

output_path = CTGAN_DIR / "overall_scores" / "ctgan_quality_score.csv"

df.to_csv(
    output_path,
    mode='a',                               # append mode
    header=True,
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