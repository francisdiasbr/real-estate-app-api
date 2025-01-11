from flask import Flask
from real_estate.routes import real_estate
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Registra o blueprint
app.register_blueprint(real_estate, url_prefix='/api')

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, port=port, host='0.0.0.0')