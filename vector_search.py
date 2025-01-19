import json
import os
import pysolr

SOLR_COLLECTION = os.getenv("SOLR_COLLECTION", "films")
SOLR_BASE_URL = os.getenv("SOLR_BASE_URL", "http://localhost:8983/solr")

SOLR_URL = f"{SOLR_BASE_URL}/{SOLR_COLLECTION}"

solr = pysolr.Solr(SOLR_URL)

def vector_search(vector, vector_field, top_k=10, rows=10):
    """
    Perform a vector search in Solr.

    Args:
        vector       (list): A 1536-dimensional vector for the query.
        vector_field (str):  Name of vector field in Solr.
        top_k        (int):  Top k nearest neighbors.
        rows         (int):  Number of rows to return.

    Returns:
        dict: Solr search response.
    """

    try:
        solr_query = f"{{!knn f={vector_field} topK={top_k}}}{json.dumps(vector)}"
        solr_response = solr.search(q=solr_query, rows=rows, fl=["id", "name", "score"])

        return solr_response

    except Exception as e:
        print(f"Error during vector search: {e}")


def get_multiline_input():
    """
    Reads multi-line input until EOF or an empty line.
    Returns the full input as a single string.
    """
    print("Paste your vector (press Enter twice when done):")
    lines = []
    while True:
        line = input()
        if line.strip() == "":  # Empty line signals end of input
            break
        lines.append(line)
    return " ".join(lines)


def main():
    print("Enter a 1536-dimensional vector in Python list format (e.g., [0.3, 0.5, ...]).")
    try:
        input_text = get_multiline_input()
        vector = json.loads(input_text)

        if not isinstance(vector, list) or len(vector) != 1536:
            print(f"Error: Vector must be a list with exactly 1536 dimensions. You entered {len(vector) if isinstance(vector, list) else 'an invalid format'}.")
            return

        print("Performing vector search...")
        results = vector_search(vector, vector_field="film_vector", top_k=10, rows=10)
        print("\nTop results from Solr:")

        for item in results:
            print(f"- ID: {item['id']}, Name: {item['name']}")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()