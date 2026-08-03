from openai import OpenAI

client = OpenAI(
    base_url="https://chat.kiconnect.nrw/api/v1",
    api_key="6a44d0a3040b4bc18af2057f:bhMgV3VHbSlAcFGgpR1oUkLSuwNuL0nYLQeO4kOlZX8="
)

for temp in [0.1, 0.6, 1.2]:
    response = client.chat.completions.create(
        model="mistral-small-4-119b-2603",
        messages=[
            {"role": "user", "content": "Generate a fictional company name."}
        ],
        temperature=temp,
    )

    print(f"\nTemperature={temp}")
    print(response.choices[0].message.content)
