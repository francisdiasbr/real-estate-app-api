from flask import Blueprint, request, jsonify
from openai import OpenAI
from config import get_mongo_collection
from typing import List, Dict

real_estate = Blueprint('real_estate', __name__)
client = OpenAI()

def get_search_embedding(query: str) -> List[float]:
    """
    Gera embedding para o texto de busca
    """
    response = client.embeddings.create(
        input=query,
        model="text-embedding-3-small",
        encoding_format="float"
    )
    return response.data[0].embedding

@real_estate.route('/search', methods=['POST'])
def search():
    """
    Endpoint para busca vetorial de imóveis
    """
    data = request.get_json()
    query = data.get('query', '')
    limit = data.get('limit', 5)

    if not query:
        return jsonify({'error': 'Query não fornecida'}), 400

    try:
        query_embedding = get_search_embedding(query)
        
        collection = get_mongo_collection("properties")
        # print(f"Buscando por: {query}")
        # print(f"Total de documentos na coleção: {collection.count_documents({})}")
        
        pipeline = [
            {
                "$vectorSearch": {
                    "index": "vector_index",
                    "path": "embedding",
                    "queryVector": query_embedding,
                    "numCandidates": limit * 10,
                    "limit": limit
                }
            },
            {
                "$project": {
                    "_id": 1,
                    "score": {"$meta": "vectorSearchScore"},
                    "dados": 1,
                    "anuncio": 1
                }
            }
        ]

        results = list(collection.aggregate(pipeline))
        # print(f"Resultados encontrados: {len(results)}")
        
        formatted_results = [{
            'id': r['_id'],
            'score': r['score'],
            'dados': r['dados'],
            'anuncio': r['anuncio']
        } for r in results]

        return jsonify({
            'results': formatted_results
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500 