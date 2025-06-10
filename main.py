from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pytrends.request import TrendReq
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import pandas as pd
import json
import time
import hashlib
import random
import asyncio
from concurrent.futures import ThreadPoolExecutor
import logging
from collections import deque
from threading import Lock

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Google Trends API", version="3.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# User agents para rotação
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
]

# Cache em memória
cache = {}
cache_lock = Lock()

# Fila de requisições
request_queue = deque()
queue_lock = Lock()

# Circuit breaker
circuit_breaker = {
    "failures": 0,
    "last_failure": None,
    "is_open": False,
    "half_open_retry": None
}

# Configurações
CACHE_TTL = 3600  # 1 hora
MIN_DELAY = 5  # segundos mínimos entre requisições
MAX_DELAY = 15  # segundos máximos entre requisições
CIRCUIT_BREAKER_THRESHOLD = 3  # falhas antes de abrir
CIRCUIT_BREAKER_TIMEOUT = 300  # 5 minutos

# Mock data para desenvolvimento
MOCK_DATA = {
    "trending_searches": {
        "brazil": ["Copa do Brasil", "Black Friday", "iPhone 15", "ChatGPT", "Netflix", "WhatsApp Web", "Instagram", "YouTube", "Flamengo", "São Paulo"],
        "united_states": ["Taylor Swift", "NFL", "Donald Trump", "ChatGPT", "Netflix", "Amazon Prime", "Weather", "Facebook", "Gmail", "YouTube"]
    },
    "interest_over_time": {
        "Python": [65, 70, 68, 72, 75, 73, 78, 80, 82, 85, 83, 87, 90, 88, 92],
        "JavaScript": [80, 82, 81, 83, 85, 84, 86, 88, 87, 89, 90, 91, 93, 92, 94],
        "AI": [40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100, 98, 99]
    }
}

def get_random_delay():
    """Retorna um delay aleatório entre MIN_DELAY e MAX_DELAY"""
    return random.uniform(MIN_DELAY, MAX_DELAY)

def get_cache_key(endpoint: str, params: dict) -> str:
    """Gera uma chave única para o cache"""
    params_str = json.dumps(params, sort_keys=True)
    return f"{endpoint}:{hashlib.md5(params_str.encode()).hexdigest()}"

def get_from_cache(key: str) -> Optional[dict]:
    """Busca dados do cache"""
    with cache_lock:
        if key in cache:
            data, expiry = cache[key]
            if datetime.now() < expiry:
                return data
            else:
                del cache[key]
    return None

def save_to_cache(key: str, data: dict, ttl: int = CACHE_TTL):
    """Salva dados no cache"""
    with cache_lock:
        expiry = datetime.now() + timedelta(seconds=ttl)
        cache[key] = (data, expiry)

def check_circuit_breaker():
    """Verifica se o circuit breaker está aberto"""
    if circuit_breaker["is_open"]:
        if circuit_breaker["last_failure"]:
            time_since_failure = (datetime.now() - circuit_breaker["last_failure"]).seconds
            if time_since_failure > CIRCUIT_BREAKER_TIMEOUT:
                circuit_breaker["is_open"] = False
                circuit_breaker["failures"] = 0
                circuit_breaker["half_open_retry"] = datetime.now()
                return False
        return True
    return False

def record_failure():
    """Registra uma falha no circuit breaker"""
    circuit_breaker["failures"] += 1
    circuit_breaker["last_failure"] = datetime.now()
    
    if circuit_breaker["failures"] >= CIRCUIT_BREAKER_THRESHOLD:
        circuit_breaker["is_open"] = True
        logger.warning("Circuit breaker ABERTO - muitas falhas consecutivas")

def record_success():
    """Registra um sucesso no circuit breaker"""
    circuit_breaker["failures"] = 0
    circuit_breaker["is_open"] = False

def get_pytrends_safe():
    """Cria uma instância do pytrends com user agent aleatório"""
    try:
        # Seleciona user agent aleatório
        headers = {
            'User-Agent': random.choice(USER_AGENTS)
        }
        
        # Delay aleatório
        time.sleep(get_random_delay())
        
        # Cria instância com timeout maior
        pytrends = TrendReq(
            hl='pt-BR', 
            tz=360, 
            timeout=(30, 60),
            requests_args={'headers': headers}
        )
        
        return pytrends
    except Exception as e:
        logger.error(f"Erro ao criar pytrends: {e}")
        raise

async def get_mock_response(endpoint: str, params: dict) -> dict:
    """Retorna dados mock para desenvolvimento"""
    await asyncio.sleep(0.5)  # Simula latência
    
    if endpoint == "trending_searches":
        country = params.get("country", "brazil")
        searches = MOCK_DATA["trending_searches"].get(country, MOCK_DATA["trending_searches"]["brazil"])
        return {
            "country": country,
            "trending_searches": searches,
            "timestamp": datetime.now().isoformat(),
            "from_cache": False,
            "is_mock": True
        }
    
    elif endpoint == "interest_over_time":
        keywords = params.get("keywords", ["Python"])
        data = []
        dates = pd.date_range(end=datetime.now(), periods=15, freq='D')
        
        for date in dates:
            row = {"date": date.isoformat()}
            for keyword in keywords[:5]:
                if keyword in MOCK_DATA["interest_over_time"]:
                    values = MOCK_DATA["interest_over_time"][keyword]
                    row[keyword] = values[len(data) % len(values)] + random.randint(-5, 5)
                else:
                    row[keyword] = random.randint(20, 100)
            data.append(row)
        
        return {
            "keywords": keywords,
            "data": data,
            "timestamp": datetime.now().isoformat(),
            "from_cache": False,
            "is_mock": True
        }
    
    return {"error": "Mock não disponível para este endpoint", "is_mock": True}

@app.get("/")
async def root():
    return {
        "message": "Google Trends API v3.0",
        "features": [
            "Circuit breaker para proteção contra falhas",
            "User agents rotativos",
            "Delay inteligente entre requisições",
            "Cache em memória",
            "Mock data para desenvolvimento",
            "Health check endpoint"
        ],
        "endpoints": [
            "/trending-searches",
            "/interest-over-time",
            "/interest-by-region",
            "/related-queries",
            "/suggestions",
            "/health"
        ],
        "status": "operational"
    }

@app.get("/health")
async def health_check():
    """Endpoint de health check"""
    circuit_status = "open" if circuit_breaker["is_open"] else "closed"
    cache_size = len(cache)
    
    return {
        "status": "healthy" if not circuit_breaker["is_open"] else "degraded",
        "circuit_breaker": circuit_status,
        "cache_entries": cache_size,
        "failures": circuit_breaker["failures"],
        "timestamp": datetime.now().isoformat()
    }

@app.get("/trending-searches")
async def get_trending_searches(
    country: str = Query(default="brazil", description="País (brazil, united_states, etc)"),
    use_mock: bool = Query(default=False, description="Usar dados mock")
):
    # Verifica cache
    cache_key = get_cache_key("trending_searches", {"country": country})
    cached_data = get_from_cache(cache_key)
    if cached_data:
        cached_data["from_cache"] = True
        return cached_data
    
    # Se usar mock ou circuit breaker aberto
    if use_mock or check_circuit_breaker():
        return await get_mock_response("trending_searches", {"country": country})
    
    try:
        pytrends = get_pytrends_safe()
        trending = pytrends.trending_searches(pn=country)
        
        result = {
            "country": country,
            "trending_searches": trending[0].tolist() if not trending.empty else [],
            "timestamp": datetime.now().isoformat(),
            "from_cache": False,
            "is_mock": False
        }
        
        save_to_cache(cache_key, result)
        record_success()
        return result
        
    except Exception as e:
        record_failure()
        logger.error(f"Erro em trending_searches: {e}")
        
        # Retorna mock em caso de erro
        return await get_mock_response("trending_searches", {"country": country})

@app.get("/interest-over-time")
async def get_interest_over_time(
    keywords: str = Query(..., description="Palavras-chave separadas por vírgula"),
    timeframe: str = Query(default="today 3-m", description="Período de tempo"),
    geo: str = Query(default="", description="Código do país"),
    use_mock: bool = Query(default=False, description="Usar dados mock")
):
    keywords_list = [k.strip() for k in keywords.split(",")][:5]
    
    # Verifica cache
    cache_key = get_cache_key("interest_time", {
        "keywords": keywords_list,
        "timeframe": timeframe,
        "geo": geo
    })
    cached_data = get_from_cache(cache_key)
    if cached_data:
        cached_data["from_cache"] = True
        return cached_data
    
    # Se usar mock ou circuit breaker aberto
    if use_mock or check_circuit_breaker():
        return await get_mock_response("interest_over_time", {"keywords": keywords_list})
    
    try:
        pytrends = get_pytrends_safe()
        pytrends.build_payload(keywords_list, timeframe=timeframe, geo=geo)
        interest_df = pytrends.interest_over_time()
        
        if interest_df.empty:
            data = []
        else:
            interest_df = interest_df.drop(columns=['isPartial'], errors='ignore')
            data = interest_df.reset_index().to_dict(orient='records')
        
        result = {
            "keywords": keywords_list,
            "timeframe": timeframe,
            "geo": geo,
            "data": data,
            "timestamp": datetime.now().isoformat(),
            "from_cache": False,
            "is_mock": False
        }
        
        save_to_cache(cache_key, result)
        record_success()
        return result
        
    except Exception as e:
        record_failure()
        logger.error(f"Erro em interest_over_time: {e}")
        
        # Retorna mock em caso de erro
        return await get_mock_response("interest_over_time", {"keywords": keywords_list})

@app.get("/suggestions")
async def get_suggestions(
    keyword: str = Query(..., description="Palavra-chave para sugestões"),
    use_mock: bool = Query(default=False, description="Usar dados mock")
):
    # Mock data para sugestões
    if use_mock or check_circuit_breaker():
        mock_suggestions = [
            {"title": f"{keyword} tutorial", "type": "search"},
            {"title": f"{keyword} course", "type": "search"},
            {"title": f"{keyword} examples", "type": "search"},
            {"title": f"learn {keyword}", "type": "search"},
            {"title": f"{keyword} documentation", "type": "search"}
        ]
        return {
            "keyword": keyword,
            "suggestions": mock_suggestions,
            "timestamp": datetime.now().isoformat(),
            "is_mock": True
        }
    
    try:
        pytrends = get_pytrends_safe()
        suggestions = pytrends.suggestions(keyword=keyword)
        
        result = {
            "keyword": keyword,
            "suggestions": [
                {
                    "title": s.get("title", ""),
                    "type": s.get("type", "")
                }
                for s in suggestions
            ],
            "timestamp": datetime.now().isoformat(),
            "is_mock": False
        }
        
        record_success()
        return result
        
    except Exception as e:
        record_failure()
        logger.error(f"Erro em suggestions: {e}")
        
        # Retorna mock em caso de erro
        return {
            "keyword": keyword,
            "suggestions": [],
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
            "is_mock": True
        }

@app.get("/cache/clear")
async def clear_cache():
    """Limpa o cache"""
    with cache_lock:
        cache.clear()
    return {"message": "Cache limpo com sucesso", "timestamp": datetime.now().isoformat()}

@app.get("/cache/stats")
async def cache_stats():
    """Estatísticas do cache"""
    with cache_lock:
        total_entries = len(cache)
        valid_entries = sum(1 for _, (_, expiry) in cache.items() if datetime.now() < expiry)
    
    return {
        "total_entries": total_entries,
        "valid_entries": valid_entries,
        "cache_ttl_seconds": CACHE_TTL,
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    print("\n🚀 Iniciando Google Trends API v3.0")
    print("📊 Documentação: http://localhost:8000/docs")
    print("🏥 Health Check: http://localhost:8000/health")
    print("🔧 Modo Mock disponível: adicione ?use_mock=true aos endpoints")
    print("\n")
    uvicorn.run(app, host="0.0.0.0", port=8000)