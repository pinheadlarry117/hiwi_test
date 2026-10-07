from synthetic_data_related.cim_parser import save_csv


def main():

    xml_file = (
        r"data/input/21060207T0628Z_YYY_EQ.xml"
    )

    output_csv = (
        r"data/output/CIM_EQ.csv"
    )

    df = save_csv(xml_file, output_csv)

    print(df.head())


if __name__ == "__main__":
    main()