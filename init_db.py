from pymongo.operations import SearchIndexModel
from config import get_mongo_collection
from generate_listings_and_embeddings import generate_mock_properties, generate_embeddings
import json

def init_vector_search():
    """
    Initializes vector search index in MongoDB Atlas
    """
    collection = get_mongo_collection("properties")
    
    # Creates collection if it doesn't exist by inserting a dummy document
    try:
        collection.insert_one({"_id": "dummy"})
        collection.delete_one({"_id": "dummy"})
    except Exception as e:
        print(f"Warning when creating collection: {e}")
    
    # Defines vector index model
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
        print("Search index created successfully!")
    except Exception as e:
        print(f"Error creating search index: {e}")

def init_database():
    """
    Initializes database with mock data and vector search index
    """
    # Generate mock properties
    mock_data = generate_mock_properties(100)
    
    # Save mock data to file
    with open('mock_data.json', 'w', encoding='utf-8') as f:
        json.dump(mock_data, f, ensure_ascii=False, indent=2)
    print("Mock data generated and saved to mock_data.json")
    
    # Initialize vector search index
    init_vector_search()
    print("Vector search index initialized")
    
    # Generate embeddings and save to MongoDB
    generate_embeddings(mock_data)
    print("Embeddings generated and saved to MongoDB")

if __name__ == "__main__":
    init_database() 