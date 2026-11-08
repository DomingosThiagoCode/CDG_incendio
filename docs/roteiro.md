# Roteiro de evolução do projeto

Este roteiro separa os resultados **já produzidos** das etapas de cálculo,
validação e pesquisa ainda necessárias. O foco inicial permanece o evento
GlobFire `24340828`; a generalização para outros IDs é uma hipótese de
reutilização a testar.

## Etapas existentes

- [x] Selecionar evento por ID e detectar datas no Google Earth Engine.
- [x] Construir geometria acumulada e separar componentes em cada data (P1).
- [x] Rastrear a região móvel principal por continuidade espacial (P2).
- [x] Exportar GeoJSON dos produtos P1 e P2 para o estudo de caso.
- [x] Preservar no repositório os dois exports históricos usados na validação
  numérica inicial, com hashes e documentação de origem.
- [x] Produzir uma tabela inicial de métricas diárias do P1 (material histórico).
- [x] Produzir CSV inicial com métricas de trajetória da RM segundo a
  implementação da metodologia da Major (material histórico).

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
- [x] Implementar adaptação reprodutível dos cinco feixes de Oliveira e
  Barbosa (Major), com pontos, distâncias geodésicas, azimutes e projeções.
- [x] Calcular indicadores do polígono integral (Jaccard, área, forma,
  avanços cardeais) **como comparador interno não atribuído ao Coronel**.
- [x] Preservar lacunas temporais e registrar as diferenças de tolerância,
  projeção LAEA e desempate de extremos em relação ao SQL original.
- [ ] Comparar numericamente as saídas da adaptação com a execução
  histórica original da Major sobre os mesmos P2 (ainda não reproduzida).
- [ ] Obter do orientador uma formulação própria verificável do método
  do Coronel, implementá-la e realizar a comparação científica formal.
- [ ] Interpretar a resolução MODIS e as lacunas com apoio de validação externa.

## Etapa D — atributos para modelos de IA (extensão experimental)

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
3. Trajetórias para QGIS e relatório preliminar de P2; comparação formal
   Major × Coronel dependente de confirmação metodológica;
4. Dataset experimental de atributos espaço-temporais para pesquisas em IA.

Nenhuma melhoria de desempenho preditivo é pressuposta antes da validação.
