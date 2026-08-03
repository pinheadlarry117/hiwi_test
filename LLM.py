from openai import OpenAI
import pandas as pd
import json

#INPUT_FILE = r"C:\Users\Administrator\Downloads\SMX.xlsx"
#INPUT_FILE2 = r"C:\Users\Administrator\Downloads\sampledata_short.csv"
#INPUT_FILE3 = r"C:\Users\Administrator\Downloads\weather_data.json"
INPUT_FILE4 = r"C:\Users\yga-hzh\Downloads\feeder_metadata.csv"

#
#file_path = r"C:\Users\Administrator\Downloads\weather_data.parquet"
#df = pd.read_parquet(file_path)

#output_path = r"C:\Users\Administrator\Downloads\weather_data.json"
#df.to_json(output_path, orient="records", indent=2)

#data1 = pd.read_excel(INPUT_FILE)
#table1_test = data1.to_csv(index=False)
#data2 = pd.read_csv(INPUT_FILE2)
#table2_test = data2.to_csv(index=False)

#data3 = pd.read_json(INPUT_FILE3, orient="records")
#table3_test = data3.head(100).to_csv(index=False)


#data4 = pd.read_csv(INPUT_FILE4)
data4 = pd.read_csv(INPUT_FILE4)
data4_markdown = pd.read_csv(INPUT_FILE4, nrows=10)
#table4_test = data4.to_csv(index=False)
table4_test = data4.to_dict(orient="records")
table4_test_markdown = data4_markdown.to_dict(orient="records")
column_name = data4.columns.tolist()  # Get the first column name
#print(table4_test_markdown)
#print(table4_test)
#columns = str(list(data3.columns))
#print(columns)


client = OpenAI(base_url="https://chat.kiconnect.nrw/api/v1",
                api_key="6a44d0a3040b4bc18af2057f:bhMgV3VHbSlAcFGgpR1oUkLSuwNuL0nYLQeO4kOlZX8=") 

response = client.chat.completions.create(
    model="gpt-5.4-mini", # Ein verfügbares Modell wählen gpt-oss-120b mistral-small-4-119b-2603 gpt-5.4-mini gpt-5.5
    
    messages=[
        {
            "role": "user",
            "content": f"""
            You are a knowledgeable assistant who helps to decide the columns to be anonymized. You have expert knowledge in Data catalogy vocabulary (DCAT) and Data Privacy Vocabulary (DPV).
            
            We want you to read the table {table4_test_markdown}.
            Instructions:
            1. Review the whole table and column names of the table.
            2. Based on input table, give the confidence score in percentage for all the columns.
            3. Give me the columns that should be anonymized, and the reasons why they should be anonymized based on the expert knowlegde.
            """
        }
    ],
)

print(response.choices[0].message.content)
#print(response)



"""

client = OpenAI(base_url="https://ollama.fit.fraunhofer.de/api",
                api_key="sk-9c747e879bbd494f93fbd30130261b54") 


Hier ist eine Website, die die Information für anonymisieren von Daten enthält: https://w3c.github.io/dpv/2.3/tech/#dpv-classes
            Sag mir um welche data type es es sich für diese Website handelt.

 Kannst du diese Tabelle lesen und mir sagen, welche Spalten sie enthält?
            Gib mir eine Liste der Spalten in dieser Tabelle, die ich anonymisieren sollte. Und gib mir ein confidence score in percentage für jede Spalte, damit ich entscheiden kann, welche Spalten ich anonymisieren möchte.
            Und auch die Gruende, warum du denkst, dass diese Spalten anonymisiert werden sollten.

            
        Base on the standing of the content, which combination of columns do you think is more sensitive and should be anonymized together, 
        and give me the confidence score for this combination in percentage, and also give me the reason why you think this combination is more sensitive than others.
        Give me seperate output of the 2 questions.
"""