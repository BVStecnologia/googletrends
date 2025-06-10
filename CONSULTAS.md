# 📊 Tipos de Consultas - Google Trends API

## 1. 🔥 Trending Searches (Pesquisas em Alta)
Mostra os termos mais pesquisados em tempo real por país.

```bash
# Exemplo: Brasil
GET /trending-searches?country=brazil

# Exemplo: Estados Unidos
GET /trending-searches?country=united_states

# Com mock data (sempre funciona)
GET /trending-searches?country=brazil&use_mock=true
```

**Países disponíveis**: argentina, australia, austria, belgium, brazil, canada, chile, colombia, czechia, denmark, egypt, finland, france, germany, greece, hong_kong, hungary, india, indonesia, ireland, israel, italy, japan, kenya, malaysia, mexico, netherlands, new_zealand, nigeria, norway, philippines, poland, portugal, romania, russia, saudi_arabia, singapore, south_africa, south_korea, spain, sweden, switzerland, taiwan, thailand, turkey, ukraine, united_kingdom, united_states, vietnam

## 2. 📈 Interest Over Time (Interesse ao Longo do Tempo)
Compara o interesse por até 5 palavras-chave ao longo do tempo.

```bash
# Comparar tecnologias
GET /interest-over-time?keywords=Python,JavaScript,Java&timeframe=today 3-m&geo=BR

# Análise de marcas
GET /interest-over-time?keywords=Netflix,Disney Plus,HBO Max&timeframe=today 12-m&geo=US

# Termos em português
GET /interest-over-time?keywords=futebol,basquete,volei&timeframe=2024-01-01 2024-12-31&geo=BR
```

**Parâmetros**:
- `keywords`: Até 5 termos separados por vírgula
- `timeframe`: 
  - `today 1-m` (último mês)
  - `today 3-m` (últimos 3 meses)
  - `today 12-m` (último ano)
  - `today 5-y` (últimos 5 anos)
  - `2023-01-01 2023-12-31` (período específico)
  - `all` (desde 2004)
- `geo`: Código do país (BR, US, JP, etc) ou vazio para mundial

## 3. 🗺️ Interest by Region (Interesse por Região)
Mostra a distribuição geográfica do interesse por uma palavra-chave.

```bash
# Por estados do Brasil
GET /interest-by-region?keyword=ChatGPT&geo=BR&resolution=REGION

# Por cidades dos EUA
GET /interest-by-region?keyword=artificial intelligence&geo=US&resolution=CITY

# Mundial por países
GET /interest-by-region?keyword=Python&resolution=COUNTRY
```

**Resoluções**:
- `COUNTRY`: Por país
- `REGION`: Por estado/região
- `CITY`: Por cidade
- `DMA`: Por área metropolitana (EUA)

## 4. 🔗 Related Queries (Consultas Relacionadas)
Encontra termos relacionados e em alta para uma palavra-chave.

```bash
# Tecnologia
GET /related-queries?keyword=machine learning&geo=US

# Entretenimento
GET /related-queries?keyword=Netflix&geo=BR

# Notícias
GET /related-queries?keyword=economia&geo=BR
```

**Retorna**:
- `top_queries`: Consultas mais populares
- `rising_queries`: Consultas em crescimento (com % de aumento)

## 5. 💡 Suggestions (Sugestões)
Obtém sugestões de termos relacionados (autocomplete do Google).

```bash
# Programação
GET /suggestions?keyword=python programming

# Marketing
GET /suggestions?keyword=digital marketing

# Negócios
GET /suggestions?keyword=startup
```

## 6. 📅 Historical Interest (Interesse Histórico)
Dados históricos detalhados por hora (premium).

```bash
GET /historical-interest?keyword=Bitcoin&year_start=2023&month_start=1&year_end=2023&month_end=12&geo=US
```

## 7. 🏥 Health Check
Verifica o status da API e circuit breaker.

```bash
GET /health
```

## 8. 💾 Cache
Gerencia o cache da aplicação.

```bash
# Estatísticas
GET /cache/stats

# Limpar cache
GET /cache/clear
```

## 📋 Exemplos de Uso Prático

### 1. Análise de Mercado
```bash
# Comparar concorrentes
GET /interest-over-time?keywords=Uber,99,Cabify&geo=BR&timeframe=today 12-m

# Interesse por região
GET /interest-by-region?keyword=Uber&geo=BR&resolution=REGION
```

### 2. Pesquisa de Tendências
```bash
# O que está em alta
GET /trending-searches?country=brazil

# Tópicos relacionados em crescimento
GET /related-queries?keyword=inteligência artificial&geo=BR
```

### 3. Análise de Produtos
```bash
# Lançamento iPhone
GET /interest-over-time?keywords=iPhone 15,iPhone 14&geo=US&timeframe=today 3-m

# Interesse mundial
GET /interest-by-region?keyword=iPhone 15&resolution=COUNTRY
```

### 4. Pesquisa de Palavras-chave SEO
```bash
# Sugestões para blog
GET /suggestions?keyword=como fazer

# Volume de busca
GET /interest-over-time?keywords=receita de bolo,receita de pão&geo=BR
```

### 5. Monitoramento de Marca
```bash
# Sentiment tracking
GET /interest-over-time?keywords=SuaMarca,MarcaConcorrente&geo=BR&timeframe=today 1-m

# Crises de reputação
GET /related-queries?keyword=SuaMarca&geo=BR
```

## 🚨 Limitações

1. **Rate Limiting**: Google limita requisições. Use delays entre chamadas.
2. **Dados Relativos**: Os valores são normalizados de 0-100, não são volumes absolutos.
3. **Disponibilidade**: Alguns dados podem não estar disponíveis para todas as regiões.
4. **Mock Data**: Use `&use_mock=true` para desenvolvimento/testes.

## 💡 Dicas

- Sempre use o parâmetro `use_mock=true` durante desenvolvimento
- Implemente cache no cliente para reduzir chamadas
- Use o health check para monitorar disponibilidade
- Combine múltiplos endpoints para análises completas