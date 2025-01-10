# 🏠Real Estate App



## Descrição

Este projeto tem como objetivo criar uma API para busca de imóveis com base em embeddings e busca vetorial.

Os imóveis são armazenados em um banco de dados MongoDB Atlas e os embeddings são gerados usando o modelo `text-embedding-3-small` da OpenAI.

<br/>

<details>
<summary><h2 style="display: inline">Instalação</h2></summary>

### Criar ambiente virtual
```bash 
python3 -m venv venv
```

### Ativar o ambiente virtual
```bash
source venv/bin/activate
```

### Instalar as dependências
```bash
pip install -r requirements.txt
```
</details>
<br/>

<details>
<summary><h2 style="display: inline">Preparar o ambiente (inicializar o índice de busca vetorial, gerar embeddings e anúncios) e executar a API</h2></summary>

### Inicializar o índice de busca vetorial
```bash
python3 init_db.py
```

### Gerar embeddings e anúncios

```bash
python3 generate_listings_and_embeddings.py
```


## Executar a API

```bash
python3 app.py
```

## Executar a busca

```bash
curl --location 'http://localhost:5000/api/search' \
--header 'Content-Type: application/json' \
--data '{
    "query": "apartamento luxuoso com piscina em São Paulo",
    "limit": 1
}'
```
</details>
<br/>

<details>
<summary><h2 style="display: inline">Response</h2></summary>

```json
{
    "results": [
        {
            "anuncio": "\"Viva com requinte e conforto em um apartamento de 180m² no coração do Itaim Bibi, São Paulo. Com 3 quartos, piscina aquecida, spa e academia premium. Por apenas R$3.200.000, seu novo lar de luxo espera por você. Agende sua visita hoje!\"",
            "dados": {
                "amenidades": [
                    "Piscina Aquecida",
                    "Spa",
                    "Academia Premium",
                    "Wine Cellar"
                ],
                "caracteristicas": {
                    "area": 180,
                    "banheiros": 4,
                    "quartos": 3,
                    "suites": 3,
                    "vagas": 3
                },
                "descricao": "Apartamento sofisticado em prédio novo com lazer completo.",
                "id": "imovel_006",
                "localizacao": {
                    "bairro": "Itaim Bibi",
                    "cidade": "São Paulo",
                    "estado": "SP"
                },
                "tipo": "Apartamento",
                "titulo": "Apartamento Alto Padrão Itaim Bibi",
                "valores": {
                    "condominio": 2500,
                    "iptu": 9000,
                    "preco": 3200000
                }
            },
            "id": "imovel_006",
            "score": 0.862663209438324
        }
    ]
}
```

</details>
<br/>

## Arquivos

- `mock_data.json`: Arquivo com dados mock para teste.
- `init_db.py`: Script para inicializar o índice de busca vetorial no MongoDB Atlas. Necessário rodar antes de rodar o script de embeddings pois o índice é necessário para a busca vetorial de embeddings para queries.
- `generate_listings_and_embeddings.py`: Script para gerar anúncio e embeddings dos imóveis e salvar no MongoDB.
- `config.py`: Configurações do MongoDB e OpenAI.
- `app.py`: API para busca de imóveis.


## Teoria

<details>
<summary><h3 style="display: inline">Índice de busca vetorial - Vector Search Index (Atlas Vector Search Index)</h3></summary>

O índice de busca vetorial (Atlas Vector Search Index) é um tipo especial de índice disponível apenas no MongoDB Atlas e que permite realizar buscas por similaridade em vetores (embeddings).

### Criar o índice

Para habilitar buscas por similaridade em seus dados, é preciso criar um índice de busca vetorial na coleção.

```python
from pymongo.operations import SearchIndexModel

# Create your index model, then create the search index
search_index_model = SearchIndexModel(
  definition = {
    "fields": [
      {
        "type": "vector",
        "path": "embedding",
        "similarity": "dotProduct",
         "numDimensions": 1536
      }
    ]
  },
  name="vector_index",
  type="vectorSearch",
)
collection.create_search_index(model=search_index_model)
```

O índice deve levar cerca de um minuto para ser construído. Quando ele terminar de ser construído, você pode começar a consultar os dados em sua coleção.

Este código cria um índice na coleção que especifica o campo de embedding como o tipo de vetor, a função de similaridade como dotProduct e o número de dimensões como 1536.

- Quando convertemos textos em embeddings, cada imóvel é representado por um vetor de 1536 dimensões
- Para encontrar imóveis similares, precisamos calcular a similaridade entre estes vetores
- O índice vetorial otimiza este processo, tornando as buscas rápidas mesmo com milhares de imóveis

### Como funciona

1. Cada imóvel no banco tem um embedding (vetor) associado
2. Quando fazemos uma busca:
   - A query do usuário é convertida em um vetor
   - O índice encontra os vetores mais similares
   - Retorna os imóveis correspondentes

### Exemplo Prático

Quando um usuário busca "apartamento com vista para o mar em Recife":
1. A busca é convertida em um vetor usando o mesmo modelo
2. O índice encontra rapidamente os vetores mais próximos
3. Retorna os imóveis ordenados por similaridade
</details>

<details>
<summary><h3 style="display: inline">Geração de Embeddings</h3></summary>

### O que são embeddings?
Embeddings são representações vetoriais de textos, onde palavras ou frases com significados semelhantes ficam próximas no espaço vetorial.

### Como geramos os embeddings?
1. **Preparação do Texto**
   Cada imóvel é convertido em um anúncio que combina todas suas características:
   ```text
   Viva com requinte e conforto em um apartamento de 180m² no coração do Itaim Bibi, São Paulo. Com 3 quartos, piscina aquecida, spa e academia premium. Por apenas R$3.200.000, seu novo lar de luxo espera por você. Agende sua visita hoje!
   ```
   Este anúncio é gerado a partir das características do imóvel e é usado para criar o embedding.

2. **Geração do Vetor**

   - O texto do anúncio é processado pelo modelo `text-embedding-3-small` da OpenAI
   - O modelo analisa o significado semântico do texto
   - Gera um vetor de 1536 dimensões que representa todas as características
   - Características similares geram vetores próximos no espaço vetorial

3. **Em que momento o embedding da busca é gerado?**
   - O embedding da busca é gerado no momento da busca
   - O embedding da busca é comparado com os embeddings dos imóveis usando a distância euclidiana
   - Os imóveis mais próximos são retornados como resultado

</details>


### Requisitos
- MongoDB Atlas
- Cluster com suporte a Atlas Search
- String de conexão configurada no `.env`

### Refs

Embeddings
https://www.mongodb.com/docs/atlas/atlas-vector-search/create-embeddings/

Produto escalar (dot product)
https://pt.wikipedia.org/wiki/Produto_escalar