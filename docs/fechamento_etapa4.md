# Etapa 4 — fechamento científico e migração Python

**Data:** 08/11/2026. **Status:** Python canônico; SQL histórico arquivado.

## Fontes e método
BARBOSA, I.; OLIVEIRA, R. A. A. C. *Modeling the dynamics of moving regions for knowledge discovery*, XXIII GEOINFO, 2022, pp. 299–304, Seção 2 e Figura 3.
OLIVEIRA, Priscila Backes de. *Proposta de modelagem de trajetórias de regiões móveis empregando trajetórias representativas*. IME, 2024.
OLIVEIRA, P. B.; BARBOSA, I. *Proposta de modelagem de trajetórias de regiões móveis*. Revista Brasileira de Geomática, 13(1), 52–76, 2025. DOI https://doi.org/10.3895/rbgeo.v13n1.19241

A revisão da fonte de 2022 esclarece duas abordagens **complementares**, não mutuamente excludentes:

1. **TR, trajetórias representativas:** séries de centroide, extremos N/S/L/O, diferenças orientadas, distâncias e azimutes. Implementação canônica preexistente em Python.
2. **IGT, incrementos geométricos temporais (nome operacional):** áreas acrescentadas por diferença geométrica R(t+1) \ R(t) e reduzidas R(t) \ R(t+1). Azimute de **cada parte nova**: centroide da região anterior para centroide da parte nova. Azimute de **cada parte reduzida**: centroide da parte perdida para centroide anterior, conforme a Figura 3.

O cálculo de **média circular ponderada por área** dos azimutes IGT é uma **síntese adicional deste projeto**, não uma equação apresentada explicitamente no artigo de 2022. Mantemos as direções por componente e a concentração direcional para evitar mascarar expansões simultâneas em direções diferentes.

## Implementação Python

O novo orquestrador scripts/consolidar_tr_igt.py chama os módulos Python existentes de TR e IGT, lendo sempre P1/P2 originais, sem usar os CSVs históricos como entradas. Cruza todas as transições por evento e datas e calcula as componentes de redução que faltavam na saída anterior.

~~~bash
python -m pip install -r requirements-auditoria.txt
python scripts/consolidar_tr_igt.py \
  dados/estudo_caso_24340828/P1_componentes_24340828.geojson \
  dados/estudo_caso_24340828/P2_regiao_movel_24340828.geojson \
  --saida resultados/etapa4
python -m unittest discover -s tests -v
~~~

Saídas adicionais (a partir do ID):
- comparacao_tr_igt_<ID>.csv: uma linha por transição com deslocamento TR, área nova/perdida IGT, número de componentes, taxa por dia, direções e diferença angular de 0–180 graus.
- componentes_reducao_<ID>.csv: cada polígono reduzido, sua área e direção da parte reduzida para o centroide anterior.
- resumo_consolidado_tr_igt_<ID>.json: resultados integrados, hashes, lacunas e registro de limitações.

Os cinco feixes TR, polígonos de incremento IGT e tabelas anteriores continuam sendo produzidos. Não substituímos métodos científicos, apenas complementamos o cálculo e centralizamos a execução.

## Critérios automáticos

- Os módulos devem concordar em ID, pares de datas e intervalo real entre observações.
- As áreas acrescentadas e perdidas calculadas pelos dois caminhos não podem diferir mais que 1e-7 km² (0,1 m², tolerância numérica).
- A decomposição de cada diferença geométrica deve conservar a área até 1 m² de resíduo numérico.
- Lacunas temporais não são interpoladas; o crescimento médio é dividido pelo número real de dias.
- Azimutes indefinidos permanecem vazios, nunca são substituídos por zero.
- Casos sintéticos verificam acréscimo, redução, redução vazia, diferença angular cruzando 360 graus, datas e IDs incompatíveis.
- O teste real do repositório confere 57 observações, 56 transições, 57/57 ranks e aproximadamente 949,843489 km² de área nova.

**Limitação de execução:** seis testes sintéticos passaram no ambiente de desenvolvimento. A execução integral não estava disponível localmente porque os GeoJSON não foram montados nesta sessão. A integração automatizada do GitHub deverá atestar essa etapa antes de considerá-la validada.

## Linha de base existente, não nova medição

Os resultados previamente versionados para o ID 24340828 incluem 57 observações, 56 transições, 285 pontos TR, 280 segmentos TR, 34,072 km de soma dos deslocamentos do centroide, 949,843489 km² de acréscimos IGT, 0,000000526 km² de área reduzida total e 506 componentes incrementais. Nove dessas partes têm menos de 1 m².

Os fragmentos pequenos e suas direções devem ser tratados como sinais de sensibilidade numérica, e não como eventos físicos resolvidos por MODIS. A comparação TR versus IGT descreve mudanças geométricas da **área queimada acumulada**, não a velocidade da frente ativa do fogo. Diferentes azimutes TR/IGT não implicam erro de um método.

## Histórico SQL

Os três SQLs adaptados em sql/ foram **implementados, mas não executados em servidor PostGIS**. São arquivados como referência histórica para eventual conferência manual de fórmulas e resultados, e **não integram o pipeline principal**. A dissertação original usou SQL como ferramenta; não há exigência científica de preservá-lo como motor.

Ver também sql/ARQUIVADO.md e docs/comparacao_tr_igt_24340828.md.
