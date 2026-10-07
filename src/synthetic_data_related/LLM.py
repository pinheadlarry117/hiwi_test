from openai import OpenAI
import pandas as pd


def load_data(input_file, nrows_preview=10):
    data = pd.read_csv(input_file)

    preview = pd.read_csv(
        input_file,
        nrows=nrows_preview
    )

    return data, preview


def analyze_columns(
    input_file,
    base_url,
    api_key,
    model_name="mistral-small-4-119b-2603"
):
    data, preview = load_data(input_file)

    table_preview = preview.to_dict(orient="records")
    column_names = data.columns.tolist()

    client = OpenAI(
        base_url=base_url,
        api_key=api_key
    )

    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {
                "role": "user",
                "content": f"""
You are a knowledgeable assistant who helps decide which columns should be anonymized.

You have expert knowledge of:
- Data Catalog Vocabulary (DCAT)
- Data Privacy Vocabulary (DPV)

Columns:
{column_names}

Table Preview:
{table_preview}

Instructions:
1. Review the table and column names.
2. Give a confidence score (%) for every column.
3. Identify columns that should be anonymized.
4. Explain the reasons based on privacy and data protection principles.
"""
            }
        ]
    )

    return response.choices[0].message.content


def main():
    INPUT_FILE = "data/input/feeder_metadata.csv"

    result = analyze_columns(
        input_file=INPUT_FILE,
        base_url="https://chat.kiconnect.nrw/api/v1",
        api_key="6ab12b138b0459668a7be856:3JFTBY/TAjp3429hf8IFD1Gi3Dq30j5dm5IGTwzkoNY="
    )

    print(result)


if __name__ == "__main__":
    main()