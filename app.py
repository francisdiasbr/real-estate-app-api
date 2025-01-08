from flask import Flask
from real_estate.routes import real_estate
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Registra o blueprint
app.register_blueprint(real_estate, url_prefix='/api')

if __name__ == '__main__':
    app.run(debug=True) 