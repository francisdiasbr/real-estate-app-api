# 🏠Real Estate App

*Read this in other languages: [Portuguese](README_PT.md)* 

## Description

This project aims to create an API for real estate search based on embeddings and vector search.

The properties are stored in a MongoDB Atlas database and the embeddings are generated using OpenAI's `text-embedding-3-small` model.

<br/>

<details>
<summary><h2 style="display: inline">Installation</h2></summary>

### Create virtual environment
```bash 
python3 -m venv venv
```

### Activate virtual environment
```bash
source venv/bin/activate
```

### Install dependencies
```bash
pip install -r requirements.txt
```
</details>
<br/>

<details>
<summary><h2 style="display: inline">Prepare the environment (initialize vector search index, generate embeddings and listings) and run the API</h2></summary>

### Initialize vector search index and populate database (mock_data.json)
```bash
python3 init_db.py
```

### Generate embeddings and listings

```bash
python3 generate_listings_and_embeddings.py
```

## Run the API

```bash
python3 app.py
```

## Execute search

```bash
curl --location 'http://localhost:5000/api/search' \
--header 'Content-Type: application/json' \
--data '{
    "query": "luxury apartment with pool in São Paulo",
    "limit": 1
}'
```
</details>
<br/>

<details>
<summary><h2 style="display: inline">Response</h2></summary>

```json
{
    "results": [
        {
            "anuncio": "\"Live with refinement and comfort in a 180m² apartment in the heart of Itaim Bibi, São Paulo. With 3 bedrooms, heated pool, spa and premium gym. For only R$3,200,000, your new luxury home awaits you. Schedule your visit today!\"",
            "dados": {
                "amenidades": [
                    "Heated Pool",
                    "Spa",
                    "Premium Gym",
                    "Wine Cellar"
                ],
                "caracteristicas": {
                    "area": 180,
                    "banheiros": 4,
                    "quartos": 3,
                    "suites": 3,
                    "vagas": 3
                },
                "descricao": "Sophisticated apartment in new building with complete leisure area.",
                "id": "imovel_006",
                "localizacao": {
                    "bairro": "Itaim Bibi",
                    "cidade": "São Paulo",
                    "estado": "SP"
                },
                "tipo": "Apartment",
                "titulo": "High-End Apartment Itaim Bibi",
                "valores": {
                    "condominio": 2500,
                    "iptu": 9000,
                    "preco": 3200000
                }
            },
            "id": "imovel_006",
            "score": 0.862663209438324
        }
    ]
}
```

</details>
<br/>

## Files

- `mock_data.json`: Mock data file for testing.
- `init_db.py`: Script to initialize vector search index in MongoDB Atlas. Must be run before running the embeddings script as the index is required for vector search of embeddings for queries.
- `generate_listings_and_embeddings.py`: Script to generate listings and embeddings for properties and save them to MongoDB.
- `config.py`: MongoDB and OpenAI configurations.
- `app.py`: API for property search.

## Theory

<details>
<summary><h3 style="display: inline">Vector Search Index (Atlas Vector Search Index)</h3></summary>

The Vector Search Index (Atlas Vector Search Index) is a special type of index available only in MongoDB Atlas that allows similarity searches in vectors (embeddings).

### Create the index

To enable similarity searches in your data, you need to create a vector search index in the collection.

```python
from pymongo.operations import SearchIndexModel

# Create your index model, then create the search index
search_index_model = SearchIndexModel(
  definition = {
    "fields": [
      {
        "type": "vector",
        "path": "embedding",
        "similarity": "dotProduct",
         "numDimensions": 1536
      }
    ]
  },
  name="vector_index",
  type="vectorSearch",
)
collection.create_search_index(model=search_index_model)
```

The index should take about a minute to build. When it finishes building, you can start querying the data in your collection.

This code creates an index in the collection that specifies the embedding field as the vector type, the similarity function as dotProduct, and the number of dimensions as 1536.

- When we convert texts to embeddings, each property is represented by a 1536-dimensional vector
- To find similar properties, we need to calculate the similarity between these vectors
- The vector index optimizes this process, making searches fast even with thousands of properties

### How it works

1. Each property in the database has an associated embedding (vector)
2. When we perform a search:
   - The user's query is converted into a vector
   - The index finds the most similar vectors
   - Returns the corresponding properties

### Practical Example

When a user searches for "apartment with ocean view in Recife":
1. The search is converted into a vector using the same model
2. The index quickly finds the closest vectors
3. Returns properties ordered by similarity
</details>

<details>
<summary><h3 style="display: inline">Embeddings Generation</h3></summary>

### What are embeddings?
Embeddings are vector representations of texts, where words or phrases with similar meanings are close in vector space.

### How do we generate embeddings?
1. **Text Preparation**
   Each property is converted into a listing that combines all its characteristics:
   ```text
   Live with refinement and comfort in a 180m² apartment in the heart of Itaim Bibi, São Paulo. With 3 bedrooms, heated pool, spa and premium gym. For only R$3,200,000, your new luxury home awaits you. Schedule your visit today!
   ```
   This listing is generated from the property's characteristics and is used to create the embedding.

2. **Vector Generation**

   - The listing text is processed by OpenAI's `text-embedding-3-small` model
   - The model analyzes the semantic meaning of the text
   - Generates a 1536-dimensional vector that represents all characteristics
   - Similar characteristics generate vectors that are close in vector space

3. **When is the search embedding generated?**
   - The search embedding is generated at search time
   - The search embedding is compared with property embeddings using euclidean distance
   - The closest properties are returned as results

</details>

### Requirements
- MongoDB Atlas
- Cluster with Atlas Search support
- Connection string configured in `.env`

### Refs

Embeddings
https://www.mongodb.com/docs/atlas/atlas-vector-search/create-embeddings/

Dot product
https://en.wikipedia.org/wiki/Dot_product

</details> 