import os
import json
import pandas as pd
from sdv.metadata import Metadata
from sdv.single_table import GaussianCopulaSynthesizer, CTGANSynthesizer

# ---------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------

RANDOM_STATE = 42
NUM_SYNTHETIC_ROWS = 10
OUTPUT_DIR = "test_results"
INPUT_FILE = r"C:\Users\Administrator\Downloads\SMX.xlsx"


os.makedirs(OUTPUT_DIR, exist_ok=True)

# ---------------------------------------------------------------------
# Step 1: Load Data
# ---------------------------------------------------------------------

data = pd.read_excel(INPUT_FILE)

# Save basic data summary
data_summary = data.describe(include="all").transpose()
data_summary["n_unique"] = data.nunique()
data_summary["n_missing"] = data.isnull().sum()

data_summary.to_csv(
    os.path.join(OUTPUT_DIR, "01_data_summary.csv"),
    index=True
)

# ---------------------------------------------------------------------
# Step 2: Detect Metadata
# ---------------------------------------------------------------------

metadata = Metadata.detect_from_dataframe(data)

# Relax datetime validation (prevents common SDV runtime failures)
for col, info in metadata.columns.items():
    if info.get("sdtype") == "datetime":
        metadata.update_column(
            column_name=col,
            sdtype="datetime",
            datetime_format=None
        )

# Save metadata as JSON
with open(os.path.join(OUTPUT_DIR, "02_detected_metadata.json"), "w", encoding="utf-8") as f:
    json.dump(metadata.to_dict(), f, indent=2)

# ---------------------------------------------------------------------
# Step 3: Gaussian Copula Synthesizer
# ---------------------------------------------------------------------

gaussian = GaussianCopulaSynthesizer(
    metadata=metadata,
    random_state=RANDOM_STATE
)

gaussian.fit(data)

synthetic_gaussian = gaussian.sample(NUM_SYNTHETIC_ROWS)

synthetic_gaussian.to_csv(
    os.path.join(OUTPUT_DIR, "04_synthetic_gaussian.csv"),
    index=False
)

gaussian.save(
    os.path.join(OUTPUT_DIR, "03_gaussian_copula.pkl")
)

# ---------------------------------------------------------------------
# Step 4: CTGAN Synthesizer
# ---------------------------------------------------------------------

ctgan = CTGANSynthesizer(
    metadata=metadata,
    epochs=300,
    random_state=RANDOM_STATE,
    verbose=True
)

ctgan.fit(data)

synthetic_ctgan = ctgan.sample(NUM_SYNTHETIC_ROWS)

synthetic_ctgan.to_csv(
    os.path.join(OUTPUT_DIR, "06_synthetic_ctgan.csv"),
    index=False
)

ctgan.save(
    os.path.join(OUTPUT_DIR, "05_ctgan.pkl")
)

# ---------------------------------------------------------------------
# Step 5: Save CTGAN Training Loss Plot
# ---------------------------------------------------------------------

loss_fig = ctgan.get_loss_values_plot()
loss_fig.write_html(
    os.path.join(OUTPUT_DIR, "07_ctgan_loss.html")
)

# ---------------------------------------------------------------------
# Final Console Summary
# ---------------------------------------------------------------------

print("✅ SDV pipeline completed successfully")
print(f"📁 Output directory: {os.path.abspath(OUTPUT_DIR)}")
print("📄 Files generated:")
for f in sorted(os.listdir(OUTPUT_DIR)):
    print(f"   - {f}")


"""
import pandas as pd
from sdv.single_table import GaussianCopulaSynthesizer
from sdv.single_table import CTGANSynthesizer
from sdv.metadata import Metadata
from sdv.utils import load_synthesizer

data = pd.read_excel(r"C:\Users\Administrator\Downloads\SMX.xlsx")
#data = pd.read_excel(r"C:\Users\Administrator\Downloads\SMX.xlsx")

metadata = Metadata.detect_from_dataframe(data)


synthesizer = GaussianCopulaSynthesizer(metadata)
synthesizer.fit(data)
synthetic_data = synthesizer.sample(num_rows=10)

synthesizerCTGAN = CTGANSynthesizer(metadata)
synthesizerCTGAN.fit(data)

synthetic_data_CTGAN = synthesizerCTGAN.sample(num_rows=10)

fig = synthesizerCTGAN.get_loss_values_plot()
fig.show()

synthetic_data.to_csv('synthetic_data.csv', index=False)
synthetic_data_CTGAN.to_csv('synthetic_data_CTGAN.csv', index=False)
print(metadata)
print(data.nunique())
"""

