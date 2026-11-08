# Roteiro de evolução do projeto

Este roteiro separa os resultados **já produzidos** das etapas de cálculo,
validação e pesquisa ainda necessárias. O foco inicial permanece o evento
GlobFire `24340828`; a generalização para outros IDs é uma hipótese de
reutilização a testar.


> **Atualização metodológica, 08/11/2026.** A Etapa 4 passou a utilizar
> **Python como implementação canônica**. O artigo de Barbosa e Oliveira
> (2022), disponível integralmente no projeto, foi lido: ele contempla
> trajetórias representativas e diferenças geométricas entre regiões,
> incluindo áreas acrescentadas e reduzidas. A nova rotina Python
> [consolidar_tr_igt.py](../scripts/consolidar_tr_igt.py) centraliza a
> execução, compara resultados TR/IGT e produz componentes de redução.
> Os SQLs ficam **arquivados como referência**, sem dependência operacional
> nem afirmação de que foram executados no PostGIS. Consulte
> [fechamento da Etapa 4](fechamento_etapa4.md).

## Etapas existentes

- [x] Selecionar evento por ID e detectar datas no Google Earth Engine.
- [x] Construir geometria acumulada e separar componentes em cada data (P1).
- [x] Rastrear a região móvel principal por continuidade espacial (P2).
- [x] Exportar GeoJSON dos produtos P1 e P2 para o estudo de caso.
- [x] Preservar no repositório os dois exports históricos usados na validação
  numérica inicial, com hashes e documentação de origem.
- [x] Produzir uma tabela inicial de métricas diárias do P1 (material histórico).
- [x] Produzir CSV inicial com métricas de trajetória da RM segundo a
  abordagem de Trajetórias Representativas (material histórico).

## Etapa A — consistência e reprodutibilidade

- [x] Automatizar uma primeira verificação estrutural/numérica de P1 e P2.
- [x] Especificar testes espaciais com casos sintéticos e limites diagnósticos.
- [x] Executar e registrar auditoria topológica dos polígonos em LAEA local.
- [x] Consolidar a distinção entre arquivos exportados e geometrias de trabalho.
- [ ] Tornar reproduzíveis os cálculos que originaram os CSVs históricos.
- [x] Fixar unidades e referencial LAEA para a linha de base das métricas;
  limiares científicos para identificação de eventos ainda dependem de validação.

## Etapa B — métricas de paisagem (todos os componentes)

- [x] Calcular perímetro e índice de forma vetorial com método e unidade explícitos.
- [x] Produzir série temporal de área, incremento, taxa média, contagem,
  dominância e forma média ponderada, com resultados por patch.
- [x] Diagnosticar efeitos dos contatos por vértice na contagem de patches,
  preservando o P1 original; não equiparar diretamente a 8 vizinhos raster.
- [ ] Delimitar indicadores adicionais de fragmentação/conectividade e avaliar
  a interpretação da distância ao vizinho em presença de contatos pontuais.
- [x] Reconstruir **linhagens conservadoras** entre observações por
  interseção de área, sem substituir a identidade local dos patches no P1.
- [x] Classificar correspondências 1→1, convergências, divergências,
  reorganizações e surgimentos sem sobreposição em grafo bipartido.
- [x] Investigar 10–12/09/2020: identificada convergência 21→1 na
  transição 10→11/09, com saídas e camada específica para revisão no QGIS.
- [ ] Obter interpretação científica externa dos eventos geométricos,
  sobretudo quando coincidirem com contatos pontuais e novas detecções.

## Etapa C — regiões móveis (patch rastreado)

- [x] Reproduzir de forma independente a regra de rastreamento GEE do P2
  a partir de P1, inclusive testes sintéticos com rank diferente de 1.
- [x] Implementar adaptação reprodutível das Trajetórias Representativas
  (TR) de Oliveira e Barbosa, com distâncias, azimutes e projeções.
- [x] Calcular indicadores do polígono integral (Jaccard, área, forma,
  avanços cardeais) como diagnósticos internos adicionais.
- [x] Preservar lacunas temporais e registrar as diferenças de tolerância,
  projeção LAEA e desempate de extremos em relação ao SQL original.
- [x] Implementar **Incrementos Geométricos Temporais (IGT)** conforme
  diferença de regiões do organograma `R(t+1) \\ R(t)`, testar em Python no
  ID `24340828` e versionar SQLs genéricos TR × IGT.
- [x] Documentar o arquivamento dos SQLs adaptados e a primazia da execução Python; a execução no PostGIS não ocorreu e não é dependência.
- [ ] Auditoria SQL × Python permanece **opcional**, caso surja infraestrutura para executar os SQLs históricos.
- [x] Ler integralmente Barbosa e Oliveira (2022), GEOINFO, p. 299–304, incluindo a diferença geométrica de áreas acrescentadas e reduzidas.
- [ ] Discutir com orientador a interpretação física e os limiares de sensibilidade para MODIS.
- [ ] Interpretar a resolução MODIS e as lacunas com apoio de validação externa.


## Etapa 5 — integração P1 + linhagens + TR/IGT

- [x] Definir contrato por ID, data, escala espacial, unidades e verificações cruzadas.
- [x] Implementar decomposição da expansão P2 em área já queimada incorporada
  e área realmente nova no evento.
- [x] Criar código para cruzar etapas 2–4 e exportar série integrada, gráficos,
  mapas e relatório interpretativo.
- [x] Executar e versionar os resultados reais da Etapa 5 após testes no CI.
- [ ] Revisar fases descritivas e eventos geométricos com o orientador,
  confrontando sensores, lacunas e dados ambientais independentes.
- [ ] Após consolidação, estender a outros IDs e futuramente criar interface.
- Referência: [metodologia](etapa5_metodologia.md).

## Etapa D — validação científica e generalização futura

- [x] Integrar numericamente indicadores P1, linhagens e TR/IGT em Python.
- [x] Produzir os gráficos, mapas e o relatório exploratório do estudo de caso.
- [ ] Revisar interpretações, fases, escalas e incertezas com o orientador.
- [ ] Confrontar casos de convergência com imagem e variáveis ambientais independentes.
- [ ] Testar outro ID para avaliar a generalização.
- [ ] Integrar a aquisição GEE ao pipeline Python e, futuramente, interface temporal.

## Etapa E — atributos para modelos de IA (extensão experimental)

- [ ] Definir uma pergunta operacional clara (por exemplo, crescimento de área
  queimada **na próxima observação**), distinguindo-a de detecção de fogo ativo.
- [ ] Definir atributos disponíveis no instante de previsão e evitar vazamento
  temporal de informações futuras.
- [ ] Integrar covariáveis ambientais, caso justificado, com origem e período
  documentados.
- [ ] Montar uma linha por unidade espacial/data, com rótulo e metadados.
- [ ] Ampliar a amostra para outros incêndios e separar treino/teste por evento
  ou período, evitando dependência temporal entre conjuntos.
- [ ] Comparar modelos basais com e sem os novos atributos e registrar métricas
  de desempenho e incertezas.

## Produtos esperados

1. Código reproduzível de extração, validação e análise espacial;
2. GeoJSONs e tabelas com dicionário de dados e procedência;
3. Trajetórias TR e componentes de diferenças geométricas IGT, incluindo direção, com base em Barbosa e Oliveira (2022);
4. Dataset experimental de atributos espaço-temporais para pesquisas em IA.

Nenhuma melhoria de desempenho preditivo é pressuposta antes da validação.
