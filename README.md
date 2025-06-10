# googletrends

API REST para Google Trends com FastAPI

## Recursos

- Trending searches por país
- Análise de interesse ao longo do tempo
- Interesse por região geográfica
- Consultas relacionadas
- Sugestões de termos
- Sistema de cache
- Circuit breaker para proteção
- Mock data para desenvolvimento

## Como Usar a API em Outros Sistemas

### URL Base
```
https://google-trends-api-steven.fly.dev
```

### Documentação Interativa
```
https://google-trends-api-steven.fly.dev/docs
```

### Exemplos de Uso

#### 1. JavaScript/Node.js

```javascript
// Usando fetch (Node.js 18+)
async function getTrendingSearches() {
  const response = await fetch('https://google-trends-api-steven.fly.dev/trending-searches?country=brazil&use_mock=true');
  const data = await response.json();
  console.log(data.trending_searches);
}

// Comparar interesse entre termos
async function compareTerms() {
  const params = new URLSearchParams({
    keywords: 'Python,JavaScript,React',
    timeframe: 'today 3-m',
    geo: 'BR',
    use_mock: 'true'
  });
  
  const response = await fetch(`https://google-trends-api-steven.fly.dev/interest-over-time?${params}`);
  const data = await response.json();
  return data;
}
```

#### 2. Python

```python
import requests

# Buscar trending topics
def get_trending_searches(country="brazil"):
    url = "https://google-trends-api-steven.fly.dev/trending-searches"
    params = {"country": country, "use_mock": "true"}
    response = requests.get(url, params=params)
    return response.json()

# Analisar interesse ao longo do tempo
def analyze_interest(keywords):
    url = "https://google-trends-api-steven.fly.dev/interest-over-time"
    params = {
        "keywords": ",".join(keywords),
        "timeframe": "today 3-m",
        "geo": "BR",
        "use_mock": "true"
    }
    response = requests.get(url, params=params)
    return response.json()

# Exemplo de uso
trending = get_trending_searches()
print(f"Top trending: {trending['trending_searches'][:5]}")

interest = analyze_interest(["Python", "JavaScript", "AI"])
for item in interest['data'][:3]:
    print(f"Date: {item['date']}, Python: {item.get('Python', 0)}")
```

#### 3. cURL (Terminal)

```bash
# Trending searches
curl "https://google-trends-api-steven.fly.dev/trending-searches?country=brazil&use_mock=true"

# Interest over time
curl "https://google-trends-api-steven.fly.dev/interest-over-time?keywords=Python,JavaScript&geo=BR&use_mock=true"

# Health check
curl "https://google-trends-api-steven.fly.dev/health"
```

#### 4. React/Frontend

```jsx
import { useState, useEffect } from 'react';

function TrendingTopics() {
  const [trends, setTrends] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('https://google-trends-api-steven.fly.dev/trending-searches?country=brazil&use_mock=true')
      .then(res => res.json())
      .then(data => {
        setTrends(data.trending_searches);
        setLoading(false);
      });
  }, []);

  if (loading) return <div>Carregando...</div>;

  return (
    <div>
      <h2>Trending no Brasil</h2>
      <ul>
        {trends.map((trend, index) => (
          <li key={index}>{trend}</li>
        ))}
      </ul>
    </div>
  );
}
```

#### 5. PHP

```php
<?php
// Trending searches
$url = "https://google-trends-api-steven.fly.dev/trending-searches?country=brazil&use_mock=true";
$response = file_get_contents($url);
$data = json_decode($response, true);

echo "Top trending no Brasil:\n";
foreach (array_slice($data['trending_searches'], 0, 5) as $trend) {
    echo "- " . $trend . "\n";
}

// Interest over time
$params = http_build_query([
    'keywords' => 'PHP,Python,JavaScript',
    'geo' => 'BR',
    'use_mock' => 'true'
]);
$url = "https://google-trends-api-steven.fly.dev/interest-over-time?" . $params;
$data = json_decode(file_get_contents($url), true);
?>
```

### Endpoints Principais

| Endpoint | Descrição | Parâmetros |
|----------|-----------|------------|
| `GET /trending-searches` | Pesquisas em alta | `country`, `use_mock` |
| `GET /interest-over-time` | Interesse ao longo do tempo | `keywords`, `timeframe`, `geo`, `use_mock` |
| `GET /interest-by-region` | Interesse por região | `keyword`, `geo`, `resolution`, `use_mock` |
| `GET /related-queries` | Consultas relacionadas | `keyword`, `geo`, `use_mock` |
| `GET /suggestions` | Sugestões de termos | `keyword`, `use_mock` |
| `GET /health` | Status da API | - |
| `GET /cache/stats` | Estatísticas do cache | - |

### Parâmetros Importantes

- **`use_mock=true`**: Sempre retorna dados de exemplo (útil para desenvolvimento)
- **`geo`**: Código do país (BR, US, JP, etc)
- **`timeframe`**: 
  - `today 1-m` (último mês)
  - `today 3-m` (últimos 3 meses)
  - `today 12-m` (último ano)
  - `2023-01-01 2023-12-31` (período específico)

### Rate Limiting

A API tem proteção contra excesso de requisições:
- Use `use_mock=true` durante desenvolvimento
- Aguarde 5-15 segundos entre requisições reais
- O circuit breaker protege contra falhas consecutivas
- Cache de 1 hora para requisições idênticas

### Tratamento de Erros

```javascript
// JavaScript
try {
  const response = await fetch('https://google-trends-api-steven.fly.dev/trending-searches');
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  const data = await response.json();
  console.log(data);
} catch (error) {
  console.error('Erro:', error);
}
```

```python
# Python
import requests

try:
    response = requests.get('https://google-trends-api-steven.fly.dev/trending-searches')
    response.raise_for_status()
    data = response.json()
except requests.exceptions.RequestException as e:
    print(f"Erro na requisição: {e}")
```

## Instalação Local

```bash
pip install -r requirements.txt
python main.py
```

Documentação local: http://localhost:8000/docs

## Deploy

Hospedado no Fly.io com auto-scaling e pay-as-you-go.