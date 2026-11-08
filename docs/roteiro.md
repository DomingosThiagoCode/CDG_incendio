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
