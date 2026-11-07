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
- [x] Produzir uma tabela inicial de métricas diárias do P1 (material histórico).
- [x] Produzir CSV inicial com métricas de trajetória da RM segundo a
  implementação da metodologia da Major (material histórico).

## Etapa A — consistência e reprodutibilidade

- [ ] Executar e registrar a validação topológica dos polígonos.
- [ ] Consolidar a distinção entre arquivos exportados e versões tratadas.
- [ ] Tornar reproduzíveis os cálculos que originaram os CSVs históricos.
- [ ] Fixar unidades, sistema de referência, convenções e tolerâncias.

## Etapa B — métricas de paisagem (todos os componentes)

- [ ] Calcular perímetro e índice de forma com método e unidade explícitos.
- [ ] Selecionar medidas de dominância, fragmentação e conectividade que
  respondam a perguntas específicas.
- [ ] Reconstruir identidades de patches entre observações.
- [ ] Classificar surgimento, continuidade e fusão por operações espaciais.
- [ ] Interpretar mudanças expressivas, incluindo 10–12/09/2020.

## Etapa C — regiões móveis (patch rastreado)

- [ ] Reproduzir os resultados numéricos do método da Major a partir de código.
- [ ] Implementar a formulação definida para a metodologia do Coronel.
- [ ] Comparar deslocamentos, direções, extremos e mudanças de forma.
- [ ] Investigar a influência das lacunas temporais e da resolução dos dados.

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
3. Mapas, gráficos e relatório comparando as duas abordagens de região móvel;
4. Dataset experimental de atributos espaço-temporais para pesquisas em IA.

Nenhuma melhoria de desempenho preditivo é pressuposta antes da validação.
