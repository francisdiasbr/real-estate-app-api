from openai import OpenAI
from config import get_mongo_collection
import json
import os
from typing import List, Dict
import random

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
    for idx, property in enumerate(batch):
        print(f"  Processing property {property['id']}...")
        try:
            anuncio = create_listing(property)
            print(f"    ✓ Anúncio gerado")
            
            embedding = get_embedding(client, anuncio)
            print(f"    ✓ Embedding gerado")
            
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
            print(f"    ✓ Salvo no MongoDB")
            
        except Exception as e:
            print(f"    ✗ Erro processando propriedade {property['id']}: {e}")

def generate_embeddings(mock_data: List[Dict], batch_size: int = 10) -> None:
    """
    Gera embeddings em lotes e salva no MongoDB
    """
    collection = get_mongo_collection("properties")
    client = OpenAI()
    
    total_batches = len(mock_data) // batch_size + (1 if len(mock_data) % batch_size > 0 else 0)
    print(f"Iniciando processamento de {len(mock_data)} propriedades em {total_batches} lotes")
    
    # Processa os dados em lotes
    for i in range(0, len(mock_data), batch_size):
        batch = mock_data[i:i + batch_size]
        print(f"\nProcessando lote {i//batch_size + 1} de {total_batches}")
        process_batch(client, batch, collection)

def generate_mock_properties(num_properties: int = 100) -> List[Dict]:
    """
    Generates mock property listings
    """
    property_types = [
        "Apartamento", "Casa", "Cobertura", "Studio", "Loft", "Garden",
        "Duplex", "Triplex", "Flat", "Vila", "Casa em Condomínio", "Mansão",
        "Kitnet", "Chalé", "Condomínio"
    ]
    
    neighborhoods = {
        "SP": [
            "Vila Mariana", "Pinheiros", "Itaim Bibi", "Jardins", "Vila Madalena",
            "Moema", "Brooklin", "Perdizes", "Paraíso", "Vila Olímpia",
            "Santana", "Tatuapé", "Morumbi", "Campo Belo", "Higienópolis",
            "Consolação", "Aclimação", "Saúde", "Jabaquara", "Butantã",
            "Lapa", "Pompeia", "Vila Leopoldina", "Santo Amaro", "Chácara Flora"
        ],
        "RJ": [
            "Copacabana", "Ipanema", "Leblon", "Botafogo", "Flamengo",
            "Barra da Tijuca", "Recreio", "Laranjeiras", "Tijuca", "Gávea",
            "Jardim Botânico", "Urca", "São Conrado", "Lagoa", "Humaitá",
            "Grajaú", "Vila Isabel", "Méier", "Maracanã", "Freguesia",
            "Pechincha", "Taquara", "Jardim Oceânico", "Joá", "Barra"
        ],
        "POA": [
            "Moinhos de Vento", "Bela Vista", "Menino Deus", "Petrópolis", "Rio Branco",
            "Cidade Baixa", "Auxiliadora", "Mont'Serrat", "Independência", "Boa Vista",
            "Três Figueiras", "Higienópolis", "Chácara das Pedras", "Vila Ipiranga", "Jardim Europa",
            "Tristeza", "Vila Assunção", "Ipanema", "Cavalhada", "Cristal"
        ],
        "CWB": [
            "Batel", "Água Verde", "Bigorrilho", "Centro", "Mercês",
            "Alto da XV", "Juvevê", "Cabral", "Hugo Lange", "Cristo Rei",
            "Jardim Social", "Ahú", "São Francisco", "Alto da Glória", "Rebouças"
        ],
        "BH": [
            "Savassi", "Lourdes", "Funcionários", "Serra", "Sion",
            "Luxemburgo", "Santo Agostinho", "Carmo", "São Pedro", "Cidade Jardim",
            "Belvedere", "Mangabeiras", "Santo Antônio", "Cruzeiro", "Anchieta"
        ]
    }
    
    amenities = [
        # Lazer
        "Piscina", "Piscina Aquecida", "Piscina Coberta", "Academia", "Academia 24h",
        "Salão de Festas", "Playground", "Brinquedoteca", "Quadra Poliesportiva",
        "Quadra de Tênis", "Quadra de Squash", "Campo de Futebol", "Pista de Corrida",
        
        # Bem-estar
        "Spa", "Sauna Seca", "Sauna Úmida", "Sala de Massagem", "Espaço Zen",
        "Estúdio de Yoga", "Sala de Meditação", "Jardim Zen",
        
        # Gastronomia
        "Terraço Gourmet", "Churrasqueira", "Forno de Pizza", "Adega Climatizada",
        "Espaço Gourmet", "Jardim de Cerveja", "Horta Comunitária", "Pomar",
        
        # Trabalho e Estudo
        "Espaço Coworking", "Centro Empresarial", "Sala de Reunião", "Biblioteca",
        "Sala de Estudos", "Internet Fibra Ótica", "Sala de Videoconferência",
        
        # Conveniência
        "Lavanderia", "Sala de Entregas", "Espaço Pet", "Pet Care", "Pet Wash",
        "Bicicletário", "Oficina de Bicicletas", "Lava Rápido", "Serviço de Manobrista",
        
        # Entretenimento
        "Cinema", "Sala de Games", "Sala de Jogos", "Lounge", "Espaço Musical",
        "Salão de Jogos", "Pub", "Bar Esportivo", "Karaokê",
        
        # Família
        "Espaço Kids", "Berçário", "Playground Coberto", "Brinquedoteca",
        "Sala de Artes", "Espaço Família", "Área de Piquenique",
        
        # Segurança e Serviços
        "Segurança 24h", "Portaria Blindada", "Circuito CFTV", "Gerador",
        "Concierge", "Serviço de Manobrista", "Depósito Privativo",
        
        # Sustentabilidade
        "Energia Solar", "Captação de Água da Chuva", "Coleta Seletiva",
        "Carregador para Carro Elétrico", "Composteira"
    ]
    
    cities = {
        "SP": "São Paulo",
        "RJ": "Rio de Janeiro",
        "POA": "Porto Alegre",
        "CWB": "Curitiba",
        "BH": "Belo Horizonte"
    }
    
    properties = []
    
    for i in range(num_properties):
        state = random.choice(list(cities.keys()))
        city = cities[state]
        
        area = random.randint(30, 500)
        bedrooms = random.randint(1, 5)
        suites = random.randint(0, bedrooms)
        parking_spots = random.randint(1, 4)
        bathrooms = random.randint(1, bedrooms + 2)
        
        # Seleciona o tipo de imóvel primeiro
        property_type = random.choice(property_types)
        
        base_price_sqm = {
            "SP": random.randint(8000, 15000),
            "RJ": random.randint(7000, 14000),
            "POA": random.randint(6000, 11000),
            "CWB": random.randint(5500, 10000),
            "BH": random.randint(5000, 9500)
        }
        
        base_price = area * base_price_sqm[state]
        
        property_data = {
            "id": f"property_{str(i+1).zfill(3)}",
            "title": f"{property_type} em {random.choice(neighborhoods[state])}",
            "type": property_type,
            "business_type": random.choice(["venda", "aluguel", "venda_aluguel"]),
            "description": generate_description({
                "type": property_type,
                "features": {
                    "area": area,
                    "bedrooms": bedrooms,
                    "suites": suites
                },
                "location": {
                    "neighborhood": random.choice(neighborhoods[state])
                }
            }),
            "features": {
                "area": area,
                "bedrooms": bedrooms,
                "suites": suites,
                "parking_spots": parking_spots,
                "bathrooms": bathrooms
            },
            "location": {
                "neighborhood": random.choice(neighborhoods[state]),
                "city": city,
                "state": state
            },
            "prices": {
                "condo_fee": random.randint(500, 3000),
                "property_tax": int(base_price * 0.02)
            },
            "amenities": random.sample(amenities, random.randint(4, 10))
        }
        
        if property_data["business_type"] in ["venda", "venda_aluguel"]:
            property_data["prices"]["sale_price"] = base_price
        if property_data["business_type"] in ["aluguel", "venda_aluguel"]:
            property_data["prices"]["rent_price"] = int(base_price * 0.004)
        
        properties.append(property_data)
    
    return properties

def generate_description(property_data: Dict) -> str:
    """
    Generates varied property descriptions from simple to luxurious
    """
    area = property_data['features']['area']
    bedrooms = property_data['features']['bedrooms']
    neighborhood = property_data['location']['neighborhood']
    property_type = property_data['type'].lower()
    
    descriptions = [
        # Descrições mais simples e diretas
        f"Ótimo {property_type} com {area}m², {bedrooms} quartos em {neighborhood}",
        f"{property_type} bem localizado, {bedrooms} dormitórios e infraestrutura completa",
        f"{property_type} aconchegante em região tranquila, próximo a comércios e transporte",
        f"Excelente {property_type} para moradia ou investimento em localização estratégica",
        f"{property_type} com boa distribuição dos ambientes e localização privilegiada",
        
        # Descrições intermediárias
        f"{property_type} em ótimo estado, com {bedrooms} quartos e área de lazer completa",
        f"Amplo {property_type} com {area}m² em região bem servida de comércio e serviços",
        f"{property_type} reformado com acabamento moderno e excelente área de convivência",
        f"Ótima oportunidade: {property_type} com {bedrooms} dormitórios em localização nobre",
        f"{property_type} com boa iluminação natural e vista livre em {neighborhood}",
        
        # Descrições mais elaboradas
        f"Lindo {property_type} com acabamento de alto padrão e total infraestrutura",
        f"Espetacular {property_type} com vista privilegiada em {neighborhood}",
        f"Exclusivo {property_type} em localização premium com {area}m² bem distribuídos",
        f"Moderno {property_type} com conceito aberto e ambientes integrados",
        f"Elegante {property_type} em região nobre com total privacidade"
    ]
    
    # Adiciona detalhes específicos para imóveis maiores ou de alto padrão
    if area > 200 or property_data['features']['suites'] > 2:
        premium_descriptions = [
            f"Magnífico {property_type} com projeto arquitetônico diferenciado e {area}m² de puro conforto",
            f"Sofisticado {property_type} em prédio novo com lazer completo e acabamento premium",
            f"Imponente {property_type} com {bedrooms} dormitórios e vista deslumbrante de {neighborhood}"
        ]
        descriptions.extend(premium_descriptions)
    
    # Adiciona detalhes específicos para imóveis compactos
    if area < 70:
        compact_descriptions = [
            f"{property_type} compacto e funcional, perfeito para solteiros ou casal",
            f"{property_type} prático com ótimo aproveitamento de espaço em {neighborhood}",
            f"Charmoso {property_type} com planta inteligente e localização privilegiada"
        ]
        descriptions.extend(compact_descriptions)
    
    return random.choice(descriptions)

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