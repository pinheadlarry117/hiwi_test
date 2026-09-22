import os
from pathlib import Path

import pandas as pd
from sdv.metadata import Metadata
from sdv.single_table import (
    GaussianCopulaSynthesizer,
    CTGANSynthesizer,
)
from sdv.evaluation.single_table import evaluate_quality


def save_original_data(data, results_root, filename):
    original_dir = results_root / "original_data"
    original_dir.mkdir(parents=True, exist_ok=True)

    output_path = original_dir / filename
    data.to_csv(output_path, index=False)

    return output_path


def save_filtered_data(data, results_root, filename):

    data = data.replace("", pd.NA)

    filtered_data = data.dropna(
        subset=["DATE", "TIMESTAMP"]
    ).copy()

    filtered_data["TIMESTAMP"] = pd.to_datetime(
        filtered_data["TIMESTAMP"]
    ).dt.date

    filtered_data["TIMESTAMP"] = pd.to_datetime(
        filtered_data["TIMESTAMP"]
    ).dt.strftime("%Y/%m/%d")

    filtered_dir = results_root / "filtered_data"
    filtered_dir.mkdir(parents=True, exist_ok=True)

    output_path = filtered_dir / filename

    filtered_data.to_csv(output_path, index=False)

    return output_path


def build_metadata(data, metadata_path):

    metadata = Metadata.detect_from_dataframe(
        data,
        table_name="table",
    )

    for col, info in metadata.tables["table"].columns.items():

        if info.get("sdtype") == "datetime":

            if col == "DATE":
                fmt = "%Y/%m/%d"

            elif col == "TIMESTAMP":
                fmt = "%Y/%m/%d"

            else:
                fmt = None

            metadata.update_column(
                table_name="table",
                column_name=col,
                sdtype="datetime",
                datetime_format=fmt,
            )

    metadata.validate()

    metadata.save_to_json(
        metadata_path,
        mode="overwrite",
    )

    return metadata


def run_gaussian(
    data,
    metadata,
    output_dir,
    dataset_name,
    num_rows,
):

    synthesizer = GaussianCopulaSynthesizer(metadata)

    synthesizer.fit(data)

    synthetic = synthesizer.sample(num_rows)

    synthetic.to_csv(
        output_dir
        / "synthetic_data"
        / f"{dataset_name}_gaussian.csv",
        index=False,
    )

    report = evaluate_quality(
        data,
        synthetic,
        metadata,
    )

    score = report.get_score()

    pd.DataFrame(
        {
            f"{dataset_name}_gaussian_quality_score":
            [score]
        }
    ).to_csv(
        output_dir
        / "overall_scores"
        / "gaussian_quality_score.csv",
        index=False,
    )

    report.save(
        output_dir
        / "quality_reports"
        / f"{dataset_name}_gaussian.pkl"
    )

    return score


def run_ctgan(
    data,
    metadata,
    output_dir,
    dataset_name,
    num_rows,
):

    synthesizer = CTGANSynthesizer(metadata)

    synthesizer.fit(data)

    synthetic = synthesizer.sample(num_rows)

    synthetic.to_csv(
        output_dir
        / "synthetic_data"
        / f"{dataset_name}_ctgan.csv",
        index=False,
    )

    report = evaluate_quality(
        data,
        synthetic,
        metadata,
    )

    score = report.get_score()

    pd.DataFrame(
        {
            f"{dataset_name}_ctgan_quality_score":
            [score]
        }
    ).to_csv(
        output_dir
        / "overall_scores"
        / "ctgan_quality_score.csv",
        index=False,
    )

    report.save(
        output_dir
        / "quality_reports"
        / f"{dataset_name}_ctgan.pkl"
    )

    return score


def run_pipeline(
    input_file,
    num_rows=20,
):
    input_file = Path(input_file)

    # hiwi_test/
    project_root = Path(__file__).resolve().parents[2]

    # hiwi_test/test_results/
    results_root = project_root / "test_results"

    ctgan_dir = results_root / "CTGAN_results"
    gauss_dir = results_root / "Gauss_results"
    metadata_dir = results_root / "metadata"

    for base in [ctgan_dir, gauss_dir]:
        for sub in [
            "synthetic_data",
            "quality_reports",
            "overall_scores",
        ]:
            (base / sub).mkdir(
                parents=True,
                exist_ok=True,
            )

    metadata_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    data = pd.read_csv(input_file)

    dataset_name = input_file.stem.replace(
        " ",
        "_",
    )

    save_original_data(
        data,
        results_root,
        f"{dataset_name}_original.csv",
    )

    filtered_path = save_filtered_data(
        data,
        results_root,
        f"{dataset_name}_filtered.csv",
    )

    filtered_data = pd.read_csv(filtered_path)

    metadata = build_metadata(
        filtered_data,
        metadata_dir
        / f"{dataset_name}_metadata.json",
    )

    gaussian_score = run_gaussian(
        filtered_data,
        metadata,
        gauss_dir,
        dataset_name,
        num_rows,
    )

    ctgan_score = run_ctgan(
        filtered_data,
        metadata,
        ctgan_dir,
        dataset_name,
        num_rows,
    )

    print("\nResults saved to:")
    print(results_root)

    return {
        "gaussian_score": gaussian_score,
        "ctgan_score": ctgan_score,
        "results_dir": str(results_root),
    }