from openai import OpenAI
import pandas as pd
from pathlib import Path
import json
from rdflib import Graph


def load_data(input_file, nrows_preview=10):
    data = pd.read_csv(input_file)

    preview = pd.read_csv(
        input_file,
        nrows=nrows_preview
    )

    return data, preview


def load_ontology(ontology_file, max_triples=500):
    """
    Convert ontology triples into text for the LLM.
    """

    g = Graph()
    g.parse(str(ontology_file))

    def short(uri):
        try:
            return g.namespace_manager.normalizeUri(uri)
        except Exception:
            return str(uri)

    triples = []

    for i, (s, p, o) in enumerate(g):
        if i >= max_triples:
            break

        triples.append(
            f"{short(s)} | {short(p)} | {short(o)}"
        )

    return "\n".join(triples)


def get_prompt(column_names, table_preview, ontology_context):
    return f"""
Ontology Context:
{ontology_context}

Columns:
{column_names}

Table Preview:
{table_preview}

Instructions:
1. Review the ontology context.
2. How many classes and properties are there in the ontology context?  Give a brief summary of the ontology context.
3. Review the table and column names
4. For every column provide: confidence_score in percentage about the likelihood of needing anonymization, anonymization_need (Yes/No) and reasoning

Return ONLY valid JSON in this format:

{{
  "columns": [
    {{
      "column": "column_name",
      "confidence_score": 95,
      "anonymization_need": "Yes",
      "reasoning": "reason"
    }}
  ]
}}

Do not return markdown.
Do not return explanations outside the JSON.

5. Explain the reasons based on privacy and data protection principles for each column which needs anonymization.
"""





def analyze_with_model(
    client,
    model_name,
    prompt
):
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0,
            response_format={"type": "json_object"}
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"ERROR: {str(e)}"


def analyze_columns(
    input_file,
    ontology_file,
    base_url,
    api_key,
    models
):
    data, preview = load_data(input_file)

    table_preview = preview.to_dict(orient="records")
    column_names = data.columns.tolist()

    ontology_context = load_ontology(ontology_file, max_triples=500)

    prompt = get_prompt(
        column_names=column_names,
        table_preview=table_preview,
        ontology_context=ontology_context
    )

    client = OpenAI(
        base_url=base_url,
        api_key=api_key
    )

    results = []

    for model in models:
        print(f"Running {model}...")

        answer = analyze_with_model(
            client=client,
            model_name=model,
            prompt=prompt
        )
        
        try:
            parsed_answer = json.loads(answer)
        except Exception:
            parsed_answer = {
                "raw_response": answer
            }

        results.append(
            {
                "model": model,
                "response": parsed_answer
            }
        )

    return pd.DataFrame(results)


def save_results(df, output_file):
    Path(output_file).parent.mkdir(
        parents=True,
        exist_ok=True
    )

    records = df.to_dict(orient="records")

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(
            records,
            f,
            ensure_ascii=False,
            indent=4
        )

    print(f"Results saved to: {output_file}")


"""
def save_results(df, output_file):
    Path(output_file).parent.mkdir(
        parents=True,
        exist_ok=True
    )

    df.to_csv(
        output_file,
        index=False,
        encoding="utf-8"
    )

    print(f"Results saved to: {output_file}")
"""

def main():

    INPUT_FILE = "data/input/feeder_metadata.csv"
    OUTPUT_FILE = "data/output/anonymization_analysis_test_with_onto_1.json"

    MODELS = [
        "mistral-small-4-119b-2603",
        "qwen3.8-27b",
        "gpt-oss-120b"
    ]

    BASE_URL = "https://chat.kiconnect.nrw/api/v1"
    API_KEY = "6accc00f0e6d635d72fb716c:+EZitVoIXtGMayhAle8wKzGvzx3Uy/+yVT1hA0Sx8yY="

    results_df = analyze_columns(
        input_file=INPUT_FILE,
        ontology_file=r"C:\Users\yga-hzh\Downloads\pd-owl.rdf",
        base_url=BASE_URL,
        api_key=API_KEY,
        models=MODELS
    )

    save_results(
        results_df,
        OUTPUT_FILE
    )

    print(results_df)


if __name__ == "__main__":
    main()



"""
You are a knowledgeable assistant who helps decide which columns should be anonymized.

Columns:
{column_names}

Table Preview:
{table_preview}

For every column provide:
- confidence_score (0-100)
- anonymization_need (Yes/No)
- reasoning

Return ONLY valid JSON in this format:

{{
  "columns": [
    {{
      "column": "column_name",
      "confidence_score": 95,
      "anonymization_need": "Yes",
      "reasoning": "reason"
    }}
  ]
}}

Do not return markdown.
Do not return explanations outside the JSON.
"""


"""
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
2. Give a confidence score related to the anonymization need (%) for every column and identify columns that should be anonymized.
3. Explain the reasons based on privacy and data protection principles for each column which needs anonymization.
5. Return the answer of second instruction in the following structured format: | **Column**                     | **Confidence Score (%)** | **Anonymization Need** | **Reasoning** |.
"""

"""
You are a knowledgeable assistant who helps decide which columns should be anonymized.

You have expert knowledge of:
- Data Catalog Vocabulary (DCAT)
- Data Privacy Vocabulary (DPV)

Columns:
{column_names}

Table Preview:
{table_preview}

Instructions:
1. Review the table and column names
2. For every column provide: confidence_score in percentage about the likelihood of needing anonymization, anonymization_need (Yes/No) and reasoning

Return ONLY valid JSON in this format:

{{
  "columns": [
    {{
      "column": "column_name",
      "confidence_score": 95,
      "anonymization_need": "Yes",
      "reasoning": "reason"
    }}
  ]
}}

Do not return markdown.
Do not return explanations outside the JSON.

3. Explain the reasons based on privacy and data protection principles for each column which needs anonymization.
"""


"""
Review the ontology context.

Ontology Context:
{ontology_context}

Then help to decide which columns should be anonymized.

Columns:
{column_names}

Table Preview:
{table_preview}

Instructions:
1. Review the table and column names
2. For every column provide: confidence_score in percentage about the likelihood of needing anonymization, anonymization_need (Yes/No) and reasoning

Return ONLY valid JSON in this format:

{{
  "columns": [
    {{
      "column": "column_name",
      "confidence_score": 95,
      "anonymization_need": "Yes",
      "reasoning": "reason"
    }}
  ]
}}

Do not return markdown.
Do not return explanations outside the JSON.

3. Explain the reasons based on privacy and data protection principles for each column which needs anonymization.
"""
