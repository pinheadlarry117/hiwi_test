from pathlib import Path

import pandas as pd


def parquet_to_csv(
    input_file: str,
    output_file: str
) -> None:
    df = pd.read_parquet(input_file)

    Path(output_file).parent.mkdir(
        parents=True,
        exist_ok=True
    )

    df.to_csv(
        output_file,
        index=False,
        encoding="utf-8"
    )

    print(f"Converted {input_file} -> {output_file}")
