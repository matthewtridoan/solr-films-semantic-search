# Solr-Based Semantic Search with OpenAI Embeddings

This project demonstrates how to set up a Solr Cloud cluster, generate embeddings for a dataset using OpenAI’s API, and index those embeddings into Solr for semantic search.

## Prerequisites

Before you begin, ensure that you have the following installed:

- Docker and Docker Compose
- Python 3.7+ and `pip`
- An OpenAI API key (make sure to set it in your `.env` file)

## Requirements

This project requires the following Python dependencies:

- `openai`
- `pysolr`
- `python-dotenv`

You can install them using `pip`:

```bash
pip install -r requirements.txt
```

## Setup

### 1. Clone the repository

Clone the repository to your local machine:

```bash
git clone https://github.com/matthewtridoan/solr-films-semantic-search.git
cd solr-films-semantic-search
```

### 2. Set up Solr Cluster using Docker Compose

This project uses Docker Compose to set up a Solr Cloud cluster with 3 Solr nodes and Zookeeper. To start the Solr cluster:

1. **Make sure Docker and Docker Compose are installed.**
2. Navigate to the project directory and run:

   ```bash
   docker-compose up -d
   ```

   This will start the Solr cluster and Zookeeper instances. Solr will be accessible on ports `8981`, `8982`, and `8983` respectively.

### 3. Create the Solr Collection

After the Solr cluster is running, create the Solr collection by running:

```bash
docker-compose exec solr1 bin/solr create -c films
```

This will create a collection named `films` in Solr.

### 4. Define the Schema for KNN Search

To enable KNN (k-nearest neighbor) search with the generated embeddings, you need to configure the schema in Solr. Run the following commands to add the necessary fields to the schema:

```bash
curl http://localhost:8983/solr/films/schema -X POST -H 'Content-type:application/json' --data-binary '{
  "add-field-type" : {
    "name":"knn_vector_1536",
    "class":"solr.DenseVectorField",
    "vectorDimension":1536,
    "similarityFunction":"cosine",
    "knnAlgorithm":"hnsw"
  },
  "add-field" : [
      {
        "name":"film_vector",
        "type":"knn_vector_1536",
        "indexed":true,
        "stored":true
      },
      {
        "name":"name",
        "type":"text_general",
        "multiValued":false,
        "stored":true
      },
      {
        "name":"initial_release_date",
        "type":"pdate",
        "stored":true
      }
    ]
}'
```

This schema defines the field for the film vector and other fields for film attributes (e.g., name, release date).

Next, add the **catchall field** to the schema:

```bash
curl -X POST -H 'Content-type:application/json' --data-binary '{"add-copy-field" : {"source":"*","dest":"_text_"}}' http://localhost:8983/solr/films/schema
```

This will create a catchall field (`_text_`) that copies all fields into one. This is useful for full-text search and ensuring all film-related data is searchable.

### 5. Set Up OpenAI API Key

Create a `.env` file in the root directory of the project, and add your OpenAI API key:

```bash
OPENAI_API_KEY=your-api-key-here
```

### 6. Generate Embeddings for the Films Dataset

You will need to generate embeddings for the films dataset using OpenAI's API. The following Python script will load the films data, generate embeddings for each film, and save them to a new file:

1. Place your films data JSON file in the `example/films/films.json` file.
2. Run the `generate_embeddings.py` script:

   ```bash
   python generate_embeddings.py
   ```

   This will generate a file `films_with_embeddings.json`, which contains the film data along with the generated embeddings.

### 7. Index the Films Data into Solr

Now that you have the film data with embeddings, you can index it into Solr. Run the following `curl` command to index the documents:

```bash
curl http://localhost:8983/solr/films/update?commit=true -X POST -H 'Content-Type: application/json' --data-binary @films_with_embeddings.json
```

This will index the films along with their embeddings into Solr.

## Running Semantic Search

Now that your Solr cluster is populated with the film data and embeddings, you can perform semantic searches. To do this, run the following Python script:

1. **Semantic Search Script**: `semantic_search.py`

   To perform a semantic search based on a query, run:

   ```bash
   python semantic_search.py
   ```

   The script will:

   - Ask you for a search query (e.g., "Movies based on basketball").
   - Generate an embedding for the query using OpenAI.
   - Search Solr for the closest films based on the generated query embedding.

### Example:

```bash
Enter your search query: Movies based on basketball
Enter the number of top results to return (default is 10): 5
Found 5 results:
- Movie 1 : 0.89
- Movie 2 : 0.85
...
```

## Running Vector Search

In addition to semantic search, you can use `vector_search.py` to directly perform a vector search in Solr based on a query vector. This script allows you to input a 1536-dimensional vector and retrieve the most similar documents from Solr.

1. **Running `vector_search.py`**:

   To run a vector search, first generate the 1536-dimensional vector (e.g., from OpenAI embeddings) and use the script like this:

   ```bash
   python vector_search.py
   ```

2. **Interactive Input**:

   The script will prompt you to paste the vector in Python list format. Once the vector is entered, it will perform the search and display the results.

### Example:

```bash
Enter a 1536-dimensional vector in Python list format (e.g., [0.3, 0.5, ...]):
[0.1, 0.2, 0.3, ..., 0.1536]

Performing vector search...
Top results from Solr:
- ID: 1, Name: Movie A
- ID: 2, Name: Movie B
...
```

You can customize the number of top results returned by changing the `rows` value in the `vector_search.py` script.
