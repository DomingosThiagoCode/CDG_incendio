# Etapa 5 — Síntese integrada de áreas queimadas (ID 24340828)

**Gerado automaticamente dos P1/P2 e das saídas versionadas das Etapas 2–4.**
As observações são acumuladas e não representam frente ativa de fogo.

## Indicadores do estudo de caso

- Período: 2020-08-09 a 2020-10-09; 57 observações e 56 transições.
- Área final P1 em LAEA: 981.291 km².
- Área final P2 em LAEA: 951.341 km²; participação 96.95%.
- Convergências geométricas ao longo das transições: 72.
- Maior taxa média de área nova entre observações: 107.824 km²/dia no intervalo encerrado em 2020-09-11.
- Maior incorporação de área anteriormente queimada ao P2: 105.466 km² no intervalo encerrado em 2020-09-11.
- Lacunas temporais maiores que um dia: 3.

## Exemplo de 10 a 11/09/2020

- Área nova no evento: 107.824 km².
- P2, aumento geométrico: 212.434 km².
- Desse aumento, já queimada no evento anterior: 105.466 km².
- Nova área realmente detectada dentro do P2: 106.968 km².
- Convergências da Etapa 3 nessa transição: 1.

Este contraste é explicável pela incorporação ao P2 de áreas que já existiam em outros patches do evento.
Não é correto igualar todo o crescimento geométrico de P2 à nova área queimada.

## Fases matematicamente descritivas (exploratórias)

Foram ajustadas até três regressões lineares independentes da curva de área total P1
contra o número de dias desde a primeira observação. Os pontos de quebra foram
procurados exaustivamente, exigindo ao menos sete observações por segmento.
Escolha do número de segmentos por BIC: n ln(SSE/n) + (3m-1) ln(n), onde m
é o número de segmentos. **Não equivale a afirmar fases físicas ou causas.**

| Fase | Observações no período | Inclinação da área acumulada | Convergências |
|---|---|---:|---:|
| F1 | 2020-08-09 a 2020-09-03 | 17.17 km²/dia | 32 |
| F2 | 2020-09-04 a 2020-09-13 | 45.57 km²/dia | 23 |
| F3 | 2020-09-14 a 2020-10-09 | 1.94 km²/dia | 17 |

## Leitura conjunta da paisagem e das regiões móveis

- O P1 descreve a área acumulada do evento e seus componentes por data.
- O grafo temporal registra relações por sobreposição de área; não comprova
  que os focos físicos de incêndio se fundiram na mesma data.
- O P2 acompanha um componente de área queimada; pode ganhar área
  anteriormente queimada quando incorpora outros componentes.
- TR descreve trajetórias de pontos representativos e IGT identifica porções
  acrescentadas e suas direções. Discordância entre azimutes não demonstra erro.
- Direções de incremento com baixa concentração devem ser interpretadas com cautela.
- Frações subpixel, contatos de vértice e intervalos maiores que um dia não
  devem ser confundidos com movimentos físicos precisos do fogo.

## Produtos

- serie_diaria_integrada: valores e fases por data.
- transicoes_integradas: decomposição geométrica do crescimento e indicadores combinados.
- fases_descritivas: quebra e inclinação das fases exploratórias.
- Figuras 01–05: evolução de áreas, estrutura espacial, crescimento, incorporação e convergências.
- Mapas de datas-chave: contorno P2 e todos os patches P1, sem base externa.

## Limitações

A geometria é derivada do GlobFire/MODIS e registra **área queimada acumulada**.
As taxas são médias entre observações, não velocidades da frente do incêndio.
O período inclui lacunas temporais. As interpretações precisam de confronto com
imagens da fonte, hidrografia/relevo e orientação científica antes de serem
atribuídas a processos físicos específicos. A classificação automática de
fases é exploratória, sensível à janela e ao modelo ajustado.

## Execução e proveniência

Script: scripts/integrar_etapa5.py. CLI parametrizada por ID, exige P1/P2,
Etapa 2, Etapa 3 e Etapa 4 já processados para o evento.
Resultados não são calculados a partir dos CSVs históricos do Beryl.
As verificações usam equivalência geométrica P1/P2 e conservação de área,
sem modificar GeoJSON originais.
