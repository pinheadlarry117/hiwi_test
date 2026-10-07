from synthetic_data_related.parquet_to_csv import parquet_to_csv


def main():
    parquet_to_csv(
        input_file=r"C:\Users\yga-hzh\Downloads\weather_data.parquet",
        output_file="data/output/weather_data.csv",
    )


if __name__ == "__main__":
    main()
