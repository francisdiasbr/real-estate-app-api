from openai import OpenAI
from config import get_mongo_collection
import json
import os
from typing import List, Dict

def create_listing(property: Dict) -> str:
    """
    Cria um anúncio criativo e envolvente para o imóvel usando a API da OpenAI
    """
    client = OpenAI()
    prompt = f"""
    Crie um anúncio imobiliário criativo e envolvente para o seguinte imóvel:
    - Tipo: {property['type']}
    - Área: {property['features']['area']}m²
    - Quartos: {property['features']['bedrooms']}
    - Localização: {property['location']['neighborhood']}, {property['location']['city']}
    - Preço: R$ {property['prices']['sale_price'] if 'sale_price' in property['prices'] else property['prices']['rent_price']}
    - Amenidades principais: {', '.join(property['amenities'][:3])}
    """
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Você é um especialista em marketing imobiliário."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=400,
        temperature=0.7
    )
    
    return response.choices[0].message.content.strip()

def get_embedding(client: OpenAI, text: str) -> List[float]:
    """
    Gera embedding usando o modelo text-embedding-3-small da OpenAI
    """
    response = client.embeddings.create(
        input=text,
        model="text-embedding-3-small",
        encoding_format="float"
    )
    return response.data[0].embedding

def process_batch(client: OpenAI, batch: List[Dict], collection) -> None:
    """
    Processa um lote de imóveis, gerando anúncios criativos, embeddings e salvando no MongoDB
    """
    for property in batch:
        anuncio = create_listing(property)
        embedding = get_embedding(client, anuncio)
        
        documento = {
            '_id': property['id'],
            'dados': property,
            'anuncio': anuncio,
            'embedding': embedding
        }
        
        collection.update_one(
            {'_id': property['id']},
            {'$set': documento},
            upsert=True
        )

def generate_embeddings(mock_data: List[Dict], batch_size: int = 10) -> None:
    """
    Gera embeddings em lotes e salva no MongoDB
    """
    collection = get_mongo_collection("properties")
    client = OpenAI()
    
    # Processa os dados em lotes
    for i in range(0, len(mock_data), batch_size):
        batch = mock_data[i:i + batch_size]
        process_batch(client, batch, collection)
        print(f"Processed batch {i//batch_size + 1} of {len(mock_data)//batch_size + 1}")

if __name__ == "__main__":
    # Carrega os dados do arquivo JSON
    try:
        with open('mock_data.json', 'r', encoding='utf-8') as f:
            mock_data = json.load(f)
    except FileNotFoundError:
        print("Arquivo mock_data.json não encontrado!")
        exit(1)
    
    # Gera os embeddings
    generate_embeddings(mock_data)
    print("Embeddings gerados e salvos com sucesso!") 