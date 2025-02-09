from flask import Flask, jsonify
from real_estate.routes import real_estate
from flask_cors import CORS
import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

@app.route('/')
def home():
    return jsonify({
        "status": "ok",
        "name": "Real Estate Search API",
        "version": "1.0",
        "endpoints": {
            "POST /api/search": {
                "description": "Busca imóveis com base em texto",
                "parameters": {
                    "query": "string - texto para busca",
                    "limit": "integer (opcional) - número máximo de resultados"
                },
                "example": {
                    "request": {
                        "query": "apartamento com piscina em Copacabana",
                        "limit": 5
                    }
                }
            },
            "GET /api/property/<id>": {
                "description": "Retorna detalhes de um imóvel específico",
                "parameters": {
                    "id": "string - identificador do imóvel"
                }
            }
        }
    }), 200  # Adicionado código de status explícito

# Registra o blueprint
app.register_blueprint(real_estate, url_prefix='/api')

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8000))  # Mudado para getenv e porta padrão 8000
    app.run(host='0.0.0.0', port=port)