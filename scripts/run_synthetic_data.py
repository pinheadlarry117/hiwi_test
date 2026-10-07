from synthetic_data_related.synthetic_data import run_pipeline


def main():

    results = run_pipeline(
        input_file="data/input/sampledata.csv",
        num_rows=20,
    )

    print()
    print("Pipeline completed")
    print()

    print(
        "Gaussian Quality Score:",
        results["gaussian_score"],
    )

    print(
        "CTGAN Quality Score:",
        results["ctgan_score"],
    )

    print(
        "Results stored in:",
        results["results_dir"],
    )


if __name__ == "__main__":
    main()