from openai import OpenAI
from config import get_mongo_collection
import json
import os
from typing import List, Dict

def criar_texto_para_embedding(imovel: Dict) -> str:
    """
    Cria texto estruturado para gerar embedding
    """
    texto = f"""
    {imovel['titulo']}
    
    Tipo: {imovel['tipo']}
    Descrição: {imovel['descricao']}
    
    Características:
    - Área: {imovel['caracteristicas']['area']}m²
    - Quartos: {imovel['caracteristicas']['quartos']}
    - Suítes: {imovel['caracteristicas']['suites']}
    - Vagas: {imovel['caracteristicas']['vagas']}
    - Banheiros: {imovel['caracteristicas']['banheiros']}
    
    Localização:
    {imovel['localizacao']['bairro']}, {imovel['localizacao']['cidade']} - {imovel['localizacao']['estado']}
    
    Valores:
    - Preço: R$ {imovel['valores']['preco']}
    - Condomínio: R$ {imovel['valores']['condominio']}
    - IPTU: R$ {imovel['valores']['iptu']}
    
    Amenidades: {', '.join(imovel['amenidades'])}
    """
    return texto.strip()

def get_embedding(client: OpenAI, texto: str) -> List[float]:
    """
    Gera embedding usando o modelo text-embedding-3-small da OpenAI
    """
    response = client.embeddings.create(
        input=texto,
        model="text-embedding-3-small",
        encoding_format="float"
    )
    return response.data[0].embedding

def processar_lote(client: OpenAI, lote: List[Dict], collection) -> None:
    """
    Processa um lote de imóveis, gerando embeddings e salvando no MongoDB
    """
    for imovel in lote:
        texto = criar_texto_para_embedding(imovel)
        embedding = get_embedding(client, texto)
        
        documento = {
            '_id': imovel['id'],
            'dados': imovel,
            'embedding': embedding,
            'texto_embedding': texto  # útil para debug e verificação
        }
        
        collection.update_one(
            {'_id': imovel['id']},
            {'$set': documento},
            upsert=True
        )

def gerar_embeddings(mock_data: List[Dict], tamanho_lote: int = 10) -> None:
    """
    Gera embeddings em lotes e salva no MongoDB
    """
    collection = get_mongo_collection("imoveis")
    client = OpenAI()
    
    # Processa os dados em lotes
    for i in range(0, len(mock_data), tamanho_lote):
        lote = mock_data[i:i + tamanho_lote]
        processar_lote(client, lote, collection)
        print(f"Processado lote {i//tamanho_lote + 1} de {len(mock_data)//tamanho_lote + 1}")

if __name__ == "__main__":
    # Carrega os dados do arquivo JSON
    try:
        with open('mock_data.json', 'r', encoding='utf-8') as f:
            mock_data = json.load(f)
    except FileNotFoundError:
        print("Arquivo mock_data.json não encontrado!")
        exit(1)
    
    # Gera os embeddings
    gerar_embeddings(mock_data)
    print("Embeddings gerados e salvos com sucesso!") 