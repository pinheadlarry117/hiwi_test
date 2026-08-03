from datetime import datetime, timedelta

from openai import OpenAI
from huggingface_hub import hf_hub_download

# Modify OpenAI's API key and API base to use vLLM's API server.
openai_api_key = "6a44d0a3040b4bc18af2057f:bhMgV3VHbSlAcFGgpR1oUkLSuwNuL0nYLQeO4kOlZX8="
openai_api_base = "https://chat.kiconnect.nrw/api/v1"

TEMP = 0.1
# use TEMP = 0.7 for reasoning="high"

client = OpenAI(
    api_key=openai_api_key,
    base_url=openai_api_base,
)

models = client.models.list()
model = models.data[0].id


def load_system_prompt(repo_id: str, filename: str) -> str:
    file_path = hf_hub_download(repo_id=repo_id, filename=filename)
    with open(file_path, "r") as file:
        system_prompt = file.read()
    today = datetime.today().strftime("%Y-%m-%d")
    yesterday = (datetime.today() - timedelta(days=1)).strftime("%Y-%m-%d")
    model_name = repo_id.split("/")[-1]
    return system_prompt.format(name=model_name, today=today, yesterday=yesterday)


SYSTEM_PROMPT = load_system_prompt(model, "SYSTEM_PROMPT.txt")

messages = [
    {"role": "system", "content": SYSTEM_PROMPT},
    {
        "role": "user",
        "content": "Write me a sentence where every word starts with the next letter in the alphabet - start with 'a' and end with 'z'.",
    },
]

response = client.chat.completions.create(
    model=model,
    messages=messages,
    temperature=TEMP,
    reasoning_effort="none",
)

assistant_message = response.choices[0].message.content
print(assistant_message)