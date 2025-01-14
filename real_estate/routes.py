from flask import Blueprint, request, jsonify
from openai import OpenAI
from config import get_mongo_collection, openai_client as client
from typing import List, Dict


real_estate = Blueprint('real_estate', __name__)


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

def generate_summary(results: List[Dict], query: str) -> str:
    """
    Gera um resumo dos resultados da pesquisa usando a API da OpenAI
    """
    descriptions = [result['dados']['description'] for result in results]
    prompt = (
        f"Você é um agente de imóveis que apresenta os imóveis de forma concisa e atraente. "
        f"Foque na principal característica desejada pelo usuário, conforme a consulta: '{query}'. "
        f"Baseie-se nos imóveis apresentados para responder à pergunta do usuário, destacando as características que correspondem à consulta. "
        f"Importante: Não use markdown ou formatação especial na resposta, apenas texto puro. "
        f"{', '.join(descriptions)}"
    )
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Você é um agente de imóveis. Responda apenas com texto puro, sem markdown ou formatação especial."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=300,
        temperature=0.7
    )
    
    return response.choices[0].message.content.strip()

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
        
        # Define um limiar de pontuação para considerar um resultado satisfatório
        score_threshold = 0.7
        satisfactory_results = [r for r in results if r['score'] >= score_threshold]
        
        formatted_results = [{
            'id': r['_id'],
            'score': r['score'],
            'dados': r['dados'],
            'anuncio': r['anuncio']
        } for r in satisfactory_results]

        summary = generate_summary(formatted_results, query)

        return jsonify({
            'results': formatted_results,
            'summary': summary
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500 


@real_estate.route('/property/<property_id>', methods=['GET'])
def get_property(property_id: str):
    """
    Endpoint para buscar detalhes de um imóvel específico por ID
    """
    try:
        collection = get_mongo_collection("properties")
        property = collection.find_one({"_id": property_id})
        
        if not property:
            return jsonify({'error': 'Imóvel não encontrado'}), 404
            
        formatted_property = {
            'id': property['_id'],
            'score': property.get('score', 0),
            'dados': property['dados'],
            'anuncio': property['anuncio']
        }
        
        return jsonify(formatted_property)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500 