# Etapa 6: auditoria científica interna (evento 24340828)

**Não é validação empírica independente**. São testes de consistência e
sensibilidade sobre produtos derivados do mesmo GlobFire/MCD64A1.

## Quadro de achados

- 57 observações, 56 transições;
  3 intervalos com mais de um dia.
- 56 das 57 datas mudam de
  contagem sob agrupamento por contato vetorial; 657
  pares de contato pontual somados entre observações.
- Diferença máxima de dominância por agrupamento:
  11.46 pontos percentuais.
- Incrementos geométricos P2 somados: 949.843 km²;
  incorporação de áreas anteriormente queimadas: 195.958
  km² (20.6% desses incrementos).
  Não confundir com área queimada nova no evento.
- Em 10–11/09, P2 incorporou 105.466
  km² anteriormente queimados, segundo os mesmos dados de entrada.

## Sensibilidade das fases da Etapa 5

Cenários determinísticos: diferentes observações mínimas, máximo de segmentos
e exclusão individual de datas críticas; **não são intervalos de confiança**.
7/13 cenários alteram os
inícios das fases em relação à base. A série usa área acumulada e tem
dependência serial; BIC não comprova regimes físicos de fogo.

| Cenário | Fases | Inícios |
|---|---:|---|
| base | 3 | 2020-08-09;2020-09-04;2020-09-14 |
| min_obs_5 | 3 | 2020-08-09;2020-09-04;2020-09-14 |
| min_obs_9 | 3 | 2020-08-09;2020-09-04;2020-09-14 |
| min_obs_11 | 3 | 2020-08-09;2020-09-03;2020-09-14 |
| maximo_duas_fases | 2 | 2020-08-09;2020-09-11 |
| remover_2020-09-03 | 3 | 2020-08-09;2020-09-01;2020-09-14 |
| remover_2020-09-04 | 3 | 2020-08-09;2020-09-05;2020-09-14 |
| remover_2020-09-10 | 3 | 2020-08-09;2020-09-04;2020-09-13 |
| remover_2020-09-11 | 3 | 2020-08-09;2020-09-04;2020-09-12 |
| remover_2020-09-13 | 3 | 2020-08-09;2020-09-04;2020-09-14 |
| remover_2020-09-14 | 3 | 2020-08-09;2020-09-04;2020-09-15 |
| remover_2020-09-24 | 3 | 2020-08-09;2020-09-04;2020-09-14 |
| remover_2020-10-09 | 3 | 2020-08-09;2020-09-04;2020-09-14 |

## Sensibilidade das direções TR e IGT

TR: centroide e N/S/E/O de Priscila Backes de Oliveira.
IGT: diferenças geométricas conforme Barbosa e Oliveira (2022). O azimute
médio ponderado é **síntese nossa**, e não equação literal do artigo.

| Concentração mínima IGT | N de comparações definidas | Mediana da diferença angular |
|---:|---:|---:|
| 0 | 55 | 1.1422186460000034 |
| 0.3 | 54 | 1.1202765314999965 |
| 0.5 | 51 | 1.0983344169999896 |
| 0.7 | 34 | 0.6818339529999946 |
| 0.9 | 24 | 0.6285866494999937 |

Mudanças de direções entre descritores não são erros de método. A dispersão
pode tornar uma direção média pouco representativa.

## Validação externa: pendências obrigatórias

Fonte: GlobFire v2 é baseado no MCD64A1; este informa data de queima
aproximada, incerteza temporal e QA em grade nominal de 500 m. A qualidade
da interseção geométrica até 1 m² **não corresponde à acurácia de imagem**.

**Revisão recomendada para 09–11/09:** no QGIS, sobrepor a camada produzida
de P2 anterior e atual, área anteriormente queimada incorporada, área nova
P2 e nova área fora do P2. É apenas uma decomposição **interna**, não
uma fonte de validação independente.

Protocolo a ser aplicado com o orientador:
1. Selecionar cenas independentes, de resolução superior e datas próximas,
   registrar nuvens, sensor, processamento e ajuste geométrico;
2. Confrontar com BurnDate, Uncertainty e QA do MCD64A1, verificando as
   diferenças de datas e pontos não mapeados;
3. Registrar amostra com acertos, omissões, falsas detecções, casos ambíguos,
   **sem assumir que uma única imagem prova a data física da fusão**;
4. Só atribuir influência de vento, rios, topografia ou combustível após
   evidência ambiental externa e revisão científica.

Fontes de documentação do produto:
- https://developers.google.com/earth-engine/datasets/catalog/JRC_GWIS_GlobFire_v2_DailyPerimeters
- https://developers.google.com/earth-engine/datasets/catalog/MODIS_061_MCD64A1
- https://gwis.jrc.ec.europa.eu/about-gwis/technical-background/burnt-areas

## Questões para o orientador

1. Preservar patches P1 originais e manter contatos pontuais como sensibilidade?
2. Quais evidências externas sustentam os eventos de convergência?
3. Como apresentar fases BIC sem interpretações causais indevidas?
4. Quais indicadores TR e IGT são suficientes para a pergunta científica?
5. Qual amostragem de imagens independentes e quais critérios de incerteza
   podemos executar no prazo da pesquisa?

**Estado:** auditoria interna documentada. Validação externa e aprovação
científica pelo orientador ainda pendentes.
