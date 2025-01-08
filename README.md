# 🏠Real Estate App



## Descrição

Este projeto tem como objetivo criar uma API para busca de imóveis com base em embeddings e busca vetorial.

Os imóveis são armazenados em um banco de dados MongoDB Atlas e os embeddings são gerados usando o modelo `text-embedding-3-small` da OpenAI.


## Instalação

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

## Execução

Primeiro rodar o script de inicialização do índice de busca vetorial:

```bash
python3 init_db.py
```

Depois rodar o script de geração de embeddings:

```bash
python3 real_estate_embeddings.py
```

## Resultado

O resultado será salvo em um arquivo JSON chamado `embeddings_imoveis.json`.

## Dependências

- `sentence-transformers`: Para gerar embeddings.
- `numpy`: Para manipulação de arrays.
- `faker`: Para gerar dados mock.


## Arquivos

- `mock_data.json`: Arquivo com dados mock para teste.
- `init_db.py`: Script para inicializar o índice de busca vetorial no MongoDB Atlas. Necessário rodar antes de rodar o script de embeddings pois o índice é necessário para a busca vetorial de embeddings para queries.
- `real_estate_embeddings.py`: Script para gerar embeddings e salvar no MongoDB.
- `config.py`: Configurações do MongoDB e OpenAI.


Com Flask:
- Pesquisar, com auto completion, um imóvel para mim, enviando um termo em NLP, e retornando as sugestões já vetorizadas, que correspondam à pesquisa.


# Teoria

## Geração de Embeddings

### O que são embeddings?
Embeddings são representações vetoriais de textos, onde palavras ou frases com significados semelhantes ficam próximas no espaço vetorial.

### Como geramos os embeddings?
1. **Preparação do Texto**
   Cada imóvel é convertido em um texto estruturado que combina todas suas características:
   ```text
   Apartamento Luxuoso com Vista para o Mar

   Tipo: Apartamento
   Descrição: Lindo apartamento com acabamento de alto padrão...

   Características:
   - Área: 120m²
   - Quartos: 3
   - Suítes: 1
   ...

   Localização:
   Boa Viagem, Recife - PE

   Valores:
   - Preço: R$ 850000
   ...

   Amenidades: Piscina, Academia, Salão de Festas...
   ```

2. **Geração do Vetor**
   - O texto é processado pelo modelo `text-embedding-3-small` da OpenAI
   - O modelo analisa o significado semântico do texto
   - Gera um vetor de 1536 dimensões que representa todas as características
   - Características similares geram vetores próximos no espaço vetorial

3. **Vantagens desta Abordagem**
   - Mantém consistência entre os imóveis
   - Destaca características importantes
   - Permite que o modelo entenda o contexto
   - Facilita buscas semânticas naturais

## Índice de Busca Vetorial (Vector Search Index)

### O que é?
O índice de busca vetorial é uma estrutura especial no MongoDB Atlas que permite realizar buscas eficientes por similaridade entre vetores (embeddings). 

### Por que precisamos?
- Quando convertemos textos em embeddings, cada imóvel é representado por um vetor de 1536 dimensões
- Para encontrar imóveis similares, precisamos calcular a similaridade entre estes vetores
- O índice vetorial otimiza este processo, tornando as buscas rápidas mesmo com milhares de imóveis

### Como funciona?
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

### Configuração do Índice
O arquivo `init_db.py` configura:
```python
{
    "fields": [{
        "type": "vector",        # Tipo do índice
        "path": "embedding",     # Campo que contém o vetor
        "numDimensions": 1536,   # Tamanho do vetor
        "similarity": "dotProduct"  # Método de cálculo de similaridade
    }]
}
```

### Requisitos
- MongoDB Atlas (não funciona com MongoDB local)
- Cluster com suporte a Atlas Search
- String de conexão configurada no `.env`