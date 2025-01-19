from openai import OpenAI
import json
import os
from dotenv import load_dotenv
import pysolr

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("API key not found. Please set OPENAI_API_KEY in your .env file.")

client = OpenAI(api_key=api_key)

SOLR_COLLECTION = os.getenv("SOLR_COLLECTION", "films")
SOLR_BASE_URL = os.getenv("SOLR_BASE_URL", "http://localhost:8983/solr")
SOLR_URL = f"{SOLR_BASE_URL}/{SOLR_COLLECTION}"

solr = pysolr.Solr(SOLR_URL)


def semantic_search(query, top_k=10, rows=10):
    """
    Perform a semantic search in Solr using OpenAI embeddings.

    Args:
        query (str): The query text.
        top_k (int): Top k nearest neighbors.
        rows  (int): Number of rows to print.

    Returns:
        None
    """
    print(f"Performing semantic search for: {query}")

    try:
        # Generate embedding for the query
        response = client.embeddings.create(
            input=query,
            model="text-embedding-3-small"
        )
        embedding = response.data[0].embedding

        # Perform Solr vector search
        solr_query = f"{{!knn f=film_vector topK={top_k}}}{json.dumps(embedding)}"
        solr_response = solr.search(q=solr_query, rows=rows, fl=["id", "name", "score"])

        print(f"\nFound {len(solr_response)} results:")
        for item in solr_response:
            print(f"- {item['name']} : {item['score']}")

    except Exception as e:
        print(f"Error during semantic search: {e}")


def main():
    query = input("Enter your search query: ")
    top_k = input("Enter top_k (default 10): ")
    rows = input("Enter rows (default 10): ")

    try:
        top_k = int(top_k) if top_k.strip().isdigit() else 10
        rows = int(rows) if rows.strip().isdigit() else 10
        semantic_search(query, top_k=top_k, rows=rows)
    except ValueError:
        print("Invalid value for top_k. Please enter a valid number.")


if __name__ == "__main__":
    main()
