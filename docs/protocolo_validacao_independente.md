# Etapa 6 — Protocolo de validação científica independente

**Escopo:** estudo de caso GlobFire 24340828, Pantanal 2020.
**Estado:** auditoria interna automatizada; confrontação externa e decisão científica **pendentes**.

## Objetivo

Distinguir *consistência computacional* da *validade das inferências físicas*.
As geometrias são áreas queimadas acumuladas de GlobFire/MCD64A1 e
não são instantâneos observados de uma frente ativa.

### Escala de evidências

| Tipo | O que pode sustentar | O que não prova |
| --- | --- | --- |
| Verificação numérica interna | Fechamento de área e correspondência P1/P2 | Exatidão da área real no terreno |
| Sensibilidade geométrica | Influência de toque por vértice, limiar e desempate | Existência de conexões físicas durante a queima |
| Sensibilidade estatística | Robustez das quebras na curva de área acumulada | Causas ou mudanças reais no regime do fogo |
| Comparação TR/IGT | Concordância ou divergência entre descritores diferentes | Direção real da propagação |
| Evidência de sensor independente | Compatibilidade com cicatrizes e datas de queima | Causalidade sem dados ambientais adequados |

## Regras de validação

1. Manter o P1 original como camada principal; não resegmentar informalmente
   patches por contato de vértice. O ensaio vetorial por toque não equivale
   à conectividade raster de 8 vizinhos.
2. Distinguir crescimento da área total, incremento geométrico do P2 e
   incorporação ao P2 de área previamente queimada fora dele.
3. Usar a duração real do intervalo. As datas dos perímetros são marcas de
   detecção processada, não tempo exato da ignição ou da fusão física.
4. As três fases de regressão são **exploratórias**. O ajuste segmentado
   de área acumulada pode apresentar dependência serial e selecionar
   quebras que variam quando uma observação é retirada.
5. TR são os cinco feixes da metodologia de Priscila Backes de Oliveira;
   IGT descreve as partes acrescidas/reduzidas e suas direções de acordo
   com o estudo de Barbosa e Oliveira (2022).
6. Os azimutes resumidos IGT ponderados por área são uma **síntese deste
   projeto**, não uma equação atribuída ao estudo publicado.
7. Dados de satélite derivam de um produto com resolução nominal de 500 m.
   Tolerâncias numéricas de área usadas nas rotinas **não** são medidas
   da acurácia do MCD64A1. Pixels com 500 m de lado corresponderiam
   nominalmente a 0,25 km², sem fazer disso limiar rígido de detecção
   vetorial ou limite garantido de erro.

## Prioridades para revisar no QGIS

- **09→10/09/2020:** 42 patches na data final, cinco convergências
  classificadas no grafo e múltiplos surgimentos sem predecessor.
- **10→11/09/2020:** um grupo de 21 patches passa a estar relacionado a
  um único componente posterior; verificar a decomposição entre áreas já
  queimadas e áreas novas. A área principal pode aumentar mais que a
  área total do incêndio sem contradição.
- **22→24/09 e 05→09/10:** intervalos de múltiplos dias; a comparação
  exige lidar com incerteza temporal e ausência de observações intermediárias.
- **Casos-controle:** selecionar aleatoriamente intervalos sem picos ou
  convergências, documentando a regra de amostragem antes de inspecionar.
  Sem controles, validação de picos tem viés de seleção.

A camada revisão_qgis_<ID>.geojson (gerada na Etapa 6) apresenta
resultados geométricos *internos* de 09–11/09: P2 anterior/atual,
área previamente queimada incorporada, nova área do P2 e área nova
fora do P2. Não é imagem independente.

## Como fazer a confrontação externa

1. Localizar a mesma área do evento (não o Pantanal inteiro) com
   georreferenciamento consistente e selecionar cenas independentes de
   resolução superior em datas próximas, com metadados de aquisição,
   órbita, nuvens, sombras e processamento.
2. Obter a banda BurnDate, a banda de incerteza temporal da data de
   queima e QA do MCD64A1 de referência. Registrar pixels sem
   observação e critérios de máscara, sem supor um pixel como
   verdadeiro apenas por pertencer ao produto original.
3. Cruzar no QGIS as cicatrizes de queima das cenas e a geometria
   do P1/P2; quantificar omissões, comissões, deslocamentos
   de limites e casos temporais ambíguos.
4. Documentar intervalo de aquisição e incerteza temporal ao avaliar
   qualquer suposta fusão de frentes. Uma imagem em data isolada
   não comprova quando duas frentes se conectaram.
5. Só atribuir direcionamento a vento, relevo, rios, combustível,
   ações humanas ou meteorologia depois de cruzar fontes ambientais
   independentes da origem dos perímetros.

Cada amostra deve ter **ID, intervalo, fonte, data/hora, CRS,
qualidade, regra de comparação, resultado, incerteza e revisor**.

## Produtos automáticos

Executar depois das Etapas 1–5:

    python scripts/validar_cientificamente_etapa6.py --id 24340828 --saida resultados/etapa6

O script produz tabelas de sensibilidade de direções, fases e contatos,
quadro de evidências, relatório e camada para revisão no QGIS.
Não invoca serviços externos nem inventa imagens. As operações apenas
reavaliam dados já conhecidos, sem editar P1/P2.

## Fontes primárias sobre a base

- Catálogo oficial GlobFire/GEE:
  https://developers.google.com/earth-engine/datasets/catalog/JRC_GWIS_GlobFire_v2_DailyPerimeters
- Catálogo MCD64A1.061 e QA:
  https://developers.google.com/earth-engine/datasets/catalog/MODIS_061_MCD64A1
- GWIS: limites das datas dos incêndios e pós-processamento:
  https://gwis.jrc.ec.europa.eu/about-gwis/technical-background/burnt-areas
- Oliveira (2024), dissertação IME; Barbosa e Oliveira (2022), GEOINFO.
  Metodologias geoespaciais e de regiões móveis já documentadas nas etapas 4–5.

## Parecer que esta etapa pode entregar

**Implementação auditada internamente**, com sensibilidade e limitações
explicitadas. **Não** declarar validação física do evento, qualidade dos
perímetros independente, efeito comprovado de barreira de rio nem que
72 convergências sejam 72 fusões de frentes de fogo.

A revisão por orientador, novas cenas e amostra de controle continuam
no backlog, assim como teste empírico em segundo ID.
