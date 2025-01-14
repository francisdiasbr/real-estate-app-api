import os
from pymongo import MongoClient
from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

# String de conexão com o MongoDB
MONGODB_CONNECTION_STRING = os.getenv("MONGODB_CONNECTION_STRING")
MONGODB_DATABASE = os.getenv("MONGODB_DATABASE")

# Conexão com o MongoDB
mongo_client = MongoClient(MONGODB_CONNECTION_STRING)
db = mongo_client[MONGODB_DATABASE]


# Função para obter uma coleção do MongoDB
def get_mongo_collection(name):
    collection = db[name]
    return collection

# Configuração da API do OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai_client = OpenAI(api_key=OPENAI_API_KEY)
