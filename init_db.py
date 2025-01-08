from pymongo.operations import SearchIndexModel
from config import get_mongo_collection

def init_vector_search():
    """
    Inicializa o índice de busca vetorial no MongoDB Atlas
    """
    collection = get_mongo_collection("imoveis")
    
    # Cria a coleção se ela não existir inserindo um documento dummy
    try:
        collection.insert_one({"_id": "dummy"})
        collection.delete_one({"_id": "dummy"})
    except Exception as e:
        print(f"Aviso ao criar coleção: {e}")
    
    # Define o modelo do índice vetorial
    search_index_model = SearchIndexModel(
        definition = {
            "fields": [
                {
                    "type": "vector",
                    "path": "embedding",
                    "similarity": "dotProduct",
                    "numDimensions": 1536,
                }
            ]
        },
        name="vector_index",
        type="vectorSearch"
    )
    
    try:
        collection.create_search_index(model = search_index_model)
        print("Índice de busca criado com sucesso!")
    except Exception as e:
        print(f"Erro ao criar índice de busca: {e}")

if __name__ == "__main__":
    init_vector_search() 