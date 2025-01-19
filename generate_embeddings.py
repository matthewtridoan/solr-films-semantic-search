from openai import OpenAI
import json
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("API key not found. Please set OPENAI_API_KEY in your .env file.")

client = OpenAI(api_key=api_key)

with open("example/films/films.json", "r") as f: # Replace with path/to/data.json
    films_data = json.load(f)

def combine_fields(doc):
    excluded_fields = {"id", "film_vector"}
    combined_text = " ".join(
        str(value) if not isinstance(value, list) else " ".join(value)
        for key, value in doc.items()
        if key not in excluded_fields
    )
    return combined_text

documents = []
for film in films_data:
    combined_text = combine_fields(film)
    response = client.embeddings.create(
        input=combined_text,
        model="text-embedding-3-small"
    )
    embedding = response.data[0].embedding

    # Add the embedding to the document
    film["film_vector"] = embedding
    documents.append(film)

with open("films_with_embeddings.json", "w") as f:
    json.dump(documents, f)

print("Embeddings generated and saved to films_with_embeddings.json")