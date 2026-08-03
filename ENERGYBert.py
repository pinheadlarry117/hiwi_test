from sentence_transformers import SentenceTransformer
from PyPDF2 import PdfReader

pdf_path = r"C:\Users\yga-hzh\Downloads\24S-202.pdf"

reader = PdfReader(pdf_path)

text = ""

for page in reader.pages:
    page_text = page.extract_text()
    if page_text:
        text += page_text + "\n"

#print(text)

#model = SentenceTransformer("ontology/EnergyBert")
model = SentenceTransformer(r"C:\Users\yga-hzh\Downloads\ENERGYBert")

"""
sentences = [
    "That is a happy person",
    "That is a happy dog",
    "That is a very happy person",
    "Today is a sunny day"
]
"""

embedding = model.encode(text)

#similarities = model.similarity(embeddings, embeddings)
#print(similarities.shape)
#print(similarities)
print("Embedding shape:", embedding.shape)

paragraphs = [
    p.strip()
    for p in text.split("\n\n")
    if len(p.strip()) > 50
]

embeddings = model.encode(paragraphs)

print(f"Found {len(paragraphs)} paragraphs")

query = "Nuclear power plant safety and regulations"

query_embedding = model.encode(
    query,
    convert_to_tensor=True
)

paragraph_embeddings = model.encode(
    paragraphs,
    convert_to_tensor=True
)

scores = model.similarity(
    query_embedding,
    paragraph_embeddings
)[0]

top_indices = scores.argsort(descending=True)[:5]

for idx in top_indices:
    print("\nScore:", float(scores[idx]))
    #print(paragraphs[int(idx)])