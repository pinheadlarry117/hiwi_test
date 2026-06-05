from openai import OpenAI
import pandas as pd
import json

#INPUT_FILE = r"C:\Users\Administrator\Downloads\SMX.xlsx"
#INPUT_FILE2 = r"C:\Users\Administrator\Downloads\sampledata_short.csv"
INPUT_FILE3 = r"C:\Users\Administrator\Downloads\weather_data.json"
INPUT_FILE4 = r"C:\Users\Administrator\Downloads\feeder_metadata.csv"

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


data4 = pd.read_csv(INPUT_FILE4)
#table4_test = data4.to_csv(index=False)
table4_test = data4.to_dict(orient="records")

#print(table4_test)
#columns = str(list(data3.columns))
#print(columns)


client = OpenAI(base_url="https://ollama.fit.fraunhofer.de/api",
                api_key="sk-9c747e879bbd494f93fbd30130261b54") 

response = client.chat.completions.create(
    model="elmtex-dighe-dsai-2024-11:8b", # Ein verfügbares Modell wählen
    
    messages=[
        {
            "role": "user",
            "content": f"""
            Hier ist eine Tabelle im CSV-Format:
            {table4_test}
            Kannst du diese Tabelle lesen und mir sagen, welche Spalten sie enthält?
            Gib mir eine Liste der Spalten in dieser Tabelle, die ich anonymisieren sollte. Und gib mir ein confidence score in percentage für jede Spalte, damit ich entscheiden kann, welche Spalten ich anonymisieren möchte.
            Und auch die Gruende, warum du denkst, dass diese Spalten anonymisiert werden sollten.

            """
        }
    ],
    temperature=0
)
print(response.choices[0].message.content)



"""
Hier ist eine Website, die die Information für anonymisieren von Daten enthält: https://w3c.github.io/dpv/2.3/tech/#dpv-classes
            Sag mir um welche data type es es sich für diese Website handelt.

 Kannst du diese Tabelle lesen und mir sagen, welche Spalten sie enthält?
            Gib mir eine Liste der Spalten in dieser Tabelle, die ich anonymisieren sollte. Und gib mir ein confidence score in percentage für jede Spalte, damit ich entscheiden kann, welche Spalten ich anonymisieren möchte.
            Und auch die Gruende, warum du denkst, dass diese Spalten anonymisiert werden sollten.

            
        Base on the standing of the content, which combination of columns do you think is more sensitive and should be anonymized together, 
        and give me the confidence score for this combination in percentage, and also give me the reason why you think this combination is more sensitive than others.
        Give me seperate output of the 2 questions.
"""