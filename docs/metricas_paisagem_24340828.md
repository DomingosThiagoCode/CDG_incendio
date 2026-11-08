# Etapa 2 — métricas de paisagem e sensibilidade topológica

**Estudo de caso:** GlobFire v2, ID `24340828`, Pantanal, 09/08–09/10/2020.

**Estado:** cálculo reproduzível implementado sobre os 978 registros de
componente-data do P1, abrangendo 57 datas. Resultados exploratórios,
condicionados à definição vetorial de patch herdada dos dados exportados.
Os GeoJSON P1/P2 originais foram **preservados sem alteração**.

## Decisão metodológica

A análise **não recria os incêndios nem reaplica conectividade raster de
4/8 vizinhos**. O evento (ID) já foi identificado pelo GlobFire, cuja
metodologia usa associações espaciais e temporais entre áreas queimadas.
O pré-processamento do projeto produz P1 a partir de união geométrica dos
polígonos acumulados e separação de subgeometrias. Cada linha do P1 é um
**patch vetorial na data**, sem identidade persistente entre datas.

A decisão de preservar o P1 original é compatível com o experimento de
regularização da Etapa 1. As geometrias são reprojetadas diretamente para
uma projeção **Lambert Azimutal Equivalente (LAEA)** local, com centro
calculado automaticamente dos limites do evento, sobre WGS84. Depois da
reprojeção, a validade planar é verificada; `make_valid()` é aplicado
**somente se necessário**, em memória. Geometrias reparadas que não
permaneçam estritamente poligonais exigem revisão, em vez de perda silenciosa
de partes. Para este evento, **0/978** patches demandaram reparo.

**Atenção:** a decomposição geométrica de P1 não equivale à segmentação
raster sob vizinhança 4 nem 8. A contagem de patches pode depender do
tratamento de **contatos pontuais**. Por isso foi incluída uma comparação
de sensibilidade, em arquivo separado, sem substituir o conjunto de referência.

## Indicadores implementados

Todas as áreas métricas utilizam m² e todos os perímetros e distâncias m
na LAEA local, com conversão para km² e km nos CSVs. Seja `i` um patch e
`t` uma data observada:

| Indicador | Fórmula/critério | Uso e ressalva |
| --- | --- | --- |
| Área do patch | `Aᵢ(t)` | Área queimada acumulada da feição na LAEA; atributo original GEE mantido em coluna separada. |
| Perímetro | `Pᵢ(t)` | Comprimento de todas as bordas do polígono, inclusive anéis interiores. Sensível à resolução e à geometria original. |
| Índice de forma **vetorial** | `SIᵢ(t) = Pᵢ(t) / [2√(π Aᵢ(t))]` | Referência circular: 1 para círculo ideal; cresce com complexidade. **Não é o índice SHAPE raster padronizado por quadrado no FRAGSTATS.** |
| Distância ao patch mais próximo | `ENNᵢ(t) = minⱼ₌̸ᵢ dist(geomᵢ,geomⱼ)` | Distância mínima entre limites. Pode ser **zero** para patches distintos que se tocam em um vértice. |
| Número de patches | `N(t)` | Quantidade de feições no P1 por data; não significa quantidade de incêndios. |
| Área acumulada | `A(t) = Σᵢ Aᵢ(t)` | Soma de áreas LAEA; os testes de sobreposição são verificados separadamente. |
| Nova área no intervalo | `ΔA(t) = A(t) − A(t anterior)` | Diferença entre **observações disponíveis**, não necessariamente dias consecutivos. |
| Taxa média do intervalo | `r(t) = ΔA(t)/Δdias` | km²/dia no intervalo observado; **não** mede velocidade de propagação da frente ativa. |
| Área do maior patch | `Amax(t) = maxᵢ Aᵢ(t)` | Maior componente em LAEA; anomalias de ordem relativa ao rank original são registradas. |
| Área dos secundários | `Asec(t) = A(t) − Amax(t)` | Complemento do maior patch entre as áreas queimadas. |
| Dominância interna | `D(t) = 100 Amax(t)/A(t)` | Porcentagem da **área queimada** no maior patch; **não** é o LPI clássico que divide pela área total da paisagem. |
| Forma média ponderada | `SĪA(t) = Σᵢ Aᵢ(t)SIᵢ(t)/A(t)` | Complexidade geométrica da paisagem queimada, atribuindo maior influência a patches extensos. |
| Perímetro somado | `Σᵢ Pᵢ(t)` | Soma dos perímetros individuais, **não** necessariamente perímetro da união dissolvida. |

Não se adicionaram índice de compactação, razão perímetro/área, densidade
de patches ou `1−D` como métricas principais: seriam redundantes com as
medidas escolhidas ou precisariam de uma **área de referência fixa**, ainda
não delimitada. Não foram estimados velocidade física da frente, nova ignição,
identidade persistente, área nuclear (*core area*) ou fusão causal.

A primeira data serve de **linha de base**: seu `ΔA` e sua taxa ficam
**vazios**, porque não há observação anterior no produto. Datas ausentes não
são interpoladas.

## Resultados numéricos do ID 24340828

| Medida | Resultado |
| --- | ---: |
| Registros P1 analisados | **978** |
| Datas | **57** |
| Maior quantidade de patches numa data | **42** |
| Área acumulada final segundo o atributo GEE | **984,6145 km²** |
| Área acumulada final recalculada em LAEA | **981,2909 km²** |
| Desvio mediano relativo LAEA × GEE, calculado por data | **−0,3376%** |
| Maior taxa média de aumento entre observações | **107,8240 km²/dia**, intervalo encerrado em 11/09/2020 |
| Lacunas temporais de mais de um dia | **3** intervalos: encerrados em 24/09 (2 dias), 01/10 (2 dias) e 09/10 (4 dias) |
| Geometrias que precisaram de reparo pós-LAEA | **0** |
| Sobreposições de área maiores que 1 m² entre feições P1 no mesmo dia | **0** |

A divergência sistemática de aproximadamente −0,34% entre as áreas LAEA
reconstruídas e os atributos GEE **não comprova erro**: os referenciais
geométricos e modelos de cálculo não são exatamente os mesmos. A taxa
107,8240 km²/dia expressa crescimento de **área queimada acumulada
detectada**, e não um avanço instantâneo de fogo.

### Achado relevante: pontos de contato entre patches

A comparação topológica detectou, **somando os pares em todas as datas**:

- **657 pares de patches com contato apenas pontual**;
- **0 pares com contato por segmento de borda**;
- **0 pares com sobreposição espacial maior que 1 m²**.

Essa soma inclui observações repetidas de estruturas similares ao longo
do tempo; **657 não representa 657 contatos geográficos únicos**.

Como diagnóstico, o script forma, em cada data, grupos transitivos de
patches que se tocam geometricamente (por vértice ou borda), mas **não
altera** as geometrias nem os IDs dos patches originais. A comparação indica:

| Indicador | P1 original | Agrupamento vetorial apenas diagnóstico |
| --- | ---: | ---: |
| Soma de feições/grupos nas 57 datas | **978** | **369** |
| Datas cuja contagem se altera | — | **56 de 57** |
| Data 10/09/2020 | **42 patches** | **16 grupos** |
| Data final 09/10/2020 | **15 patches** | **3 grupos** |
| Dominância na data final | **96,95%** | **99,76%** |

Essa comparação é significativa. Entretanto, **não pode ser rotulada
como teste exato de “4 versus 8 vizinhos”**: os contornos analisados já
são polígonos processados e podem ter efeitos de vetorização. Seria
necessário reconstruir a segmentação na grade MODIS original para afirmar
equivalência raster.

A distância ao vizinho mais próximo resulta zero para aproximadamente
**72,9%** dos registros com vizinho nesta série, devido ao contato por
vértices. Consequentemente, **ENN não deve ser interpretada isoladamente
como distância real entre focos independentes**. O padrão de contatos
precisa constar da discussão metodológica antes de conclusões sobre
fragmentação.

**Encaminhamento científico:** manter a análise original como referência,
conforme a decisão do projeto; apresentar explicitamente a sensibilidade
por contato pontual. Não afirmar que a contagem representa componentes
desconectados em sentido topológico forte, nem inferir mudanças na
propagação do fogo sem verificação complementar.

## Reproduzir os resultados

Na raiz do repositório, em Python 3.12:

```bash
python -m pip install -r requirements-auditoria.txt
python scripts/validar_produtos.py \
  dados/estudo_caso_24340828/P1_componentes_24340828.geojson \
  dados/estudo_caso_24340828/P2_regiao_movel_24340828.geojson
python scripts/calcular_metricas_paisagem.py \
  dados/estudo_caso_24340828/P1_componentes_24340828.geojson \
  --saida resultados/etapa2
python -m unittest discover -s tests -v
```

O script é parametrizado pelo arquivo P1: **não possui ID nem datas
fixados no código**. A pasta de saída terá arquivos com o ID encontrado
nos metadados da entrada:

1. `metricas_patches_<ID>.csv`: uma linha por patch/data;
2. `metricas_temporais_<ID>.csv`: uma linha por data;
3. `sensibilidade_contato_<ID>.csv`: diagnóstico alternativo não normativo;
4. `resumo_metricas_<ID>.json`: projeção, hashes, qualidade e estatísticas.

O arquivo `resumo_metricas` preserva o SHA-256 da entrada para permitir
verificar exatamente qual export foi processado. Não há filtragem de
patches pequenos; estabelecer eventual limite mínimo exige argumento
científico adicional.

## Base científica e ressalvas de comparabilidade

1. Artés, T. et al. (2019). *A global wildfire dataset for the analysis
   of fire regimes and fire behaviour*. Scientific Data 6, 296.
   DOI: https://doi.org/10.1038/s41597-019-0312-2 — identificação dos
   eventos e polígonos GlobFire.
2. Zatelli, P. et al. (2019). *Relevance of the Cell Neighborhood Size in
   Landscape Metrics Evaluation and Free or Open Source Software
   Implementations*. ISPRS IJGI 8(12), 586.
   DOI: https://doi.org/10.3390/ijgi8120586 — 4 versus 8 vizinhos e
   necessidade de declarar a regra.
3. *FRY, a global database of fire patch functional traits derived from
   space-borne burned area products* (2018).
   https://pmc.ncbi.nlm.nih.gov/articles/PMC6038852/ — exemplos de área,
   perímetro, índices de forma e atributos temporais de patches queimados.
4. FRAGSTATS, documentação do **Largest Patch Index**:
   https://fragstats.org/index.php/fragstats-metrics/patch-based-metrics/area-and-edge-metrics/l2-largest-patch-index
   — o LPI clássico usa área total da **paisagem**, diferentemente da
   dominância interna das áreas queimadas calculada aqui.
5. *An Integrated Framework for Landscape Indices’ Calculation with
   Raster–Vector Integration and Its Application Based on QGIS* (2024).
   https://doi.org/10.3390/ijgi13070242 — normalização circular do
   índice de forma para dados vetoriais.

**Limitações:** resultados restritos ao evento analisado; não foi feita
comparação com mapas de referência de área queimada, avaliação de incerteza
pixel a pixel ou generalização a múltiplos IDs. O ganho principal desta
etapa é estabelecer uma linha de base métrica transparente e reproduzível.
