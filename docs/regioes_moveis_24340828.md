# Etapa 4 — trajetórias representativas e diagnóstico da região móvel

**Evento:** GlobFire v2, `24340828` (Pantanal, 2020).

**Período:** 09/08 a 09/10/2020, **57 observações** e **56 transições**.
**Estado:** implementação e testes da parte computacional concluídos;
**comparação formal Major × Coronel ainda condicionada à especificação do
método do Coronel**.

## Objetivo e limites de atribuição

Esta etapa trabalha somente com a região móvel **P2**, uma geometria por
observação, rastreada dentro das componentes **P1**. Há três análises distintas:

1. **Reprodução independente da regra do GEE para P2:** primeiro maior patch;
   nas observações seguintes, candidato com maior interseção em área com o
   selecionado anterior; se não houver interseção, candidato mais próximo.
   Essa regra está no arquivo `gee_globfire_componentes_regiao_movel.js`.
2. **Adaptação computacional da metodologia de Oliveira e Barbosa (Major):**
   cinco feixes de trajetórias, obtidos do centroide e dos extremos Norte,
   Sul, Leste e Oeste de cada região. Calculam-se distâncias geodésicas,
   azimutes e diferenças orientadas em coordenadas métricas.
3. **Diagnóstico da geometria integral do P2:** área, interseção/união,
   contorno, forma e avanços do envelope espacial, para estudar o que os
   cinco pontos resumem ou deixam de mostrar.

**A análise (3) é um comparador geométrico construído neste projeto. Não é
rotulada como “método do Coronel”.** O material de que dispomos descreve o
Coronel principalmente em termos de **identidade e continuidade do patch**,
mas não contém uma segunda formulação com equações e indicadores inequívocos.
Esse protocolo deve ser obtido/confirmado com o orientador antes de atribuir
resultados científicos à comparação entre autores.

## 1. Base espacial e invariantes

- A fonte é o par **P1/P2 original**, em WGS84, guardado em
  `dados/estudo_caso_24340828/`; os hashes SHA-256 aparecem no resumo JSON.
- P1 e P2 devem ter os mesmos dias e ID. Cada P2 deve ter exatamente um
  patch, existir no P1 sob o rank declarado e ter geometria equivalente.
- Como o GEE exporta coordenadas em ponto flutuante, a equivalência entre
  a feição P2 e o P1 correspondente é verificada por **diferença simétrica
  de área na LAEA**, com tolerância de `max(1 m², 10⁻⁸ × área_P1)`.
  No caso estudado, a maior diferença foi **0,0000418 m²**.
- A projeção **LAEA local/WGS84** é calculada usando a extensão do P1,
  idêntica à das Etapas 2 e 3; vértices e geometrias originais são
  preservados. O centroide é **centroide de área em LAEA**, mais apropriado
  às distâncias métricas que o centroide calculado em graus.
- Distâncias entre pontos: geodésicas sobre o elipsoide WGS84 (`Geod.inv`).
  Azimutes: norte = 0°, leste = 90°, sul = 180°, oeste = 270°.
  Deslocamentos X/Y e amplitudes: coordenadas LAEA em quilômetros.
- Extremos N/S/E/O: escolhidos **entre os vértices exteriores de P2 WGS84**
  pelo maior/menor valor de latitude ou longitude, como na proposta original.
  Empates são resolvidos deterministicamente: vértice mais próximo da
  coordenada ortogonal do centroide; persistindo empate, coordenada menor.
  Isso melhora a reprodutibilidade em relação a `FIRST_VALUE` sem desempate
  secundário no SQL histórico, mas pode mudar o ponto escolhido.

## 2. Indicadores e sua interpretação

### Cinco trajetórias (Major, adaptação)

Para cada ponto representativo `p` e duas observações `tᵢ` e `tⱼ`:

- `distancia_geodesica_km`: distância geodésica entre `pᵢ` e `pⱼ`;
- `azimute_geodesico_graus`: direção de `pᵢ` para `pⱼ`;
- `delta_x_laea_km`, `delta_y_laea_km`: diferenças de coordenadas;
- `delta_eixo_orientado_km`: `Δy` (N), `−Δy` (S), `Δx` (E), `−Δx` (O).
  **Positivo significa avanço no sentido cardinal correspondente**, sem
  implicar movimentação física da frente do fogo. Não se aplica ao centroide;
- `distancia_media_km_dia`: distância da transição dividida pelos **dias
  efetivamente transcorridos**. Não é velocidade instantânea de incêndio.

As cinco linhas de trajetória ligam os pontos observados em ordem temporal,
**sem interpolar** os dias faltantes. Um vértice extremo em `tⱼ` não precisa
ser o mesmo ponto material de `tᵢ`: um grande salto pode ocorrer quando o
vértice mais extremo muda, mesmo que o polígono não sofra translação rígida.

### Polígono integral (comparador interno, sem atribuição ao Coronel)

Para as geometrias LAEA `A` (anterior) e `B` (atual):

- **Jaccard geométrico:** `área(A ∩ B) / área(A ∪ B)` (entre 0 e 1);
- **Retenção da área anterior:** `100 × área(A ∩ B) / área(A)`;
- **Área detectada nova no P2:** `área(B \ A)`; área não retida `área(A \ B)`;
- **Incremento líquido:** `área(B) − área(A)`;
- **Índice de forma vetorial:** `P / (2 √(π A))`, sem equiparação ao SHAPE
  de software de análise raster;
- **Avanço cardinal do envelope LAEA:** diferenças entre `maxY`, `minY`,
  `maxX`, `minX`, orientadas para fora em cada eixo. `Δamplitude_NS` e
  `Δamplitude_LO` são as somas dos avanços em cada eixo.

**Atenção:** os avanços do *envelope projetado* e o deslocamento dos *vértices
extremos escolhidos em WGS84* são indicadores distintos, embora relacionados.
Não devem ser tratados como a mesma variável. Valores de Jaccard menores
podem simplesmente refletir crescimento de área queimada acumulada.

## 3. Resultados conferidos do evento 24340828

| Resultado | Quantidade ou valor |
| --- | ---: |
| Pontos de observação gerados (57 × 5) | **285** |
| Segmentos entre observações (56 × 5) | **280** |
| Trajetórias GeoJSON para QGIS | **5** |
| Datas cujo rank foi reproduzido a partir de P1 | **57/57** |
| Seleções após a primeira por interseção de área | **56/56** |
| Casos reais que exigiram fallback por proximidade | **0** |
| Empates no melhor escore de rastreamento | **0** |
| Mudanças do rank P2 em relação ao maior patch | **0** |
| Lacunas maiores que 1 dia | **3** |
| Área LAEA inicial → final do P2 | **1,4975 → 951,3410 km²** |
| Soma das distâncias entre centroides consecutivos | **34,072 km** |
| Soma dos deslocamentos do extremo N | **46,474 km** |
| Soma dos deslocamentos do extremo S | **65,182 km** |
| Soma dos deslocamentos do extremo E | **89,518 km** |
| Soma dos deslocamentos do extremo O | **12,742 km** |

Essas somas são os comprimentos de **trajetórias de descritores geométricos**;
não representam quilometragem percorrida por um incêndio, distância da
frente de fogo nem velocidade de propagação.

A maior distância do centroide entre duas observações foi **6,582 km**, na
transição **10→11/09/2020**, quando a Etapa 3 identificou convergência
geométrica de **21 patches anteriores em 1 posterior**. Nessa transição,
o crescimento líquido da área acumulada do P2 foi de aproximadamente
**212,434 km²**. Assim, o deslocamento do centroide está associado a uma
grande incorporação de área e **não autoriza interpretar uma translação
física de 6,582 km**.

O índice de forma do P2 passou aproximadamente de **1,5194** (primeira
observação) a **11,5063** (última). Esse aumento descreve maior extensão
do perímetro relativa à área na geometria acumulada; não identifica,
isoladamente, uma barreira geográfica nem a causa do formato.

As lacunas são **22→24/09 (2 dias), 29/09→01/10 (2 dias) e 05→09/10
(4 dias)**. O código guarda `dias_intervalo` em todas as tabelas para não
tratar uma mudança de quatro dias como movimento diário.

**Importante para a validade externa:** os 57 ranks coincidem, mas neste
evento o patch rastreado também é o de rank 1 em todas as observações.
Portanto, este caso **não demonstra empiricamente** a vantagem do
rastreamento por continuidade sobre escolher sempre o maior; isso é
verificado apenas em um teste sintético que troca a ordem dos ranks.

## 4. Arquivos e conferência no QGIS

Todos os resultados ficam em `resultados/etapa4/`:

| Arquivo | Granularidade | Uso principal |
| --- | --- | --- |
| `pontos_representativos_<ID>.csv` | 285 linhas | Posições N/S/E/O/centroide (WGS84 e LAEA) |
| `segmentos_trajetorias_<ID>.csv` | 280 linhas | Distância, azimute e diferenças métricas |
| `indicadores_regiao_<ID>.csv` | 56 linhas | Métricas da geometria integral P2 por transição |
| `verificacao_rastreamento_<ID>.csv` | 57 linhas | Auditoria independente do rank escolhido |
| `cinco_trajetorias_<ID>.geojson` | 5 linhas | Visualização da trajetória de cada ponto no QGIS |
| `resumo_regiao_movel_<ID>.json` | 1 objeto | Hashes, projeção, contagens, ressalvas |

No QGIS, carregar o GeoJSON e categorizar `ponto` (cinco categorias).
As linhas estão em coordenadas WGS84; sua exibição pode ser sobreposta
à camada original P2 filtrada por `data`. Para análise de uma transição,
usar `data_anterior` e `data_atual` nos CSVs; não há linha de transição
no primeiro dia, pois ele não possui observação anterior.

## 5. Execução, testes e casos de erro

```bash
python -m pip install -r requirements-auditoria.txt
python scripts/analisar_regiao_movel.py \
  dados/estudo_caso_24340828/P1_componentes_24340828.geojson \
  dados/estudo_caso_24340828/P2_regiao_movel_24340828.geojson \
  --saida resultados/etapa4
python -m unittest discover -s tests -v
```

O código não depende de `24340828` internamente: usa o ID encontrado no
P1/P2. O reuso com outros incêndios **ainda exige validação externa**.

| Entrada/caso | Resultado esperado | Tolerância/critério |
| --- | --- | --- |
| P1 e P2 reais | 57 datas; mesmos ranks | igualdade das contagens e ranks |
| Geometrias P1/P2 quase iguais | aceitar variação de exportação | `max(1 m², 10⁻⁸ × área)` |
| Geometria P2 diferente | abortar; não gerar conclusão | diferença simétrica acima da tolerância |
| Primeiro patch e continuidade | reproduzir rank e critério | rank exato; desempate registrado |
| Sem sobreposição | testar candidato mais próximo | distância geométrica mínima |
| Dois candidatos empatados | declarar empate; rank menor na auditoria | escores iguais dentro de `1e-10` relativo |
| Geometrias com área negativa/nula | abortar | área e geometria válidas |
| Intervalos temporais faltantes | preservar diferença real entre datas | `dias_intervalo > 1` |
| Polígono se expande sem translação | Jaccard reduz, avanços positivos | casos geométricos analíticos |
| Dados originais | não alterar P1/P2 | hash SHA-256 antes/depois |

## 6. Decisões científicas a confirmar com o orientador

1. **Qual é a referência/definição formal da metodologia do Coronel?**
   Solicitar equações, regras de identidade e indicadores esperados. Sem
   essa definição, comparar o comparador interno com a Major **não pode**
   ser apresentado como validação dos dois métodos.
2. A semântica de “região móvel” é adequada para **área queimada acumulada**?
   O centroide pode mudar por crescimento unilateral sem translação.
3. Como tratar **fusão geométrica de patches** e a perda de identidade de
   componentes: apenas como evento espacial (Etapa 3), ou com regras de
   rastreamento adicionais?
4. Quais **tolerâncias espaciais** fazem sentido perante a resolução de
   origem MODIS, especialmente antes de classificar avanço/recuo?
5. Quais métricas e gráficos comparar definitivamente: comprimentos dos
   feixes, orientação, incrementos cardeais, Jaccard, forma e eventos de
   convergência? A seleção deve corresponder à pergunta científica.

## Referências e procedência

- OLIVEIRA, P. B.; BARBOSA, I. **Proposta de modelagem de trajetórias de
  regiões móveis**. *Revista Brasileira de Geomática*, v. 13, n. 1,
  p. 52–76, 2025. DOI: https://doi.org/10.3895/rbgeo.v13n1.19241 .
  Original da editora: https://periodicos.utfpr.edu.br/rbgeo/article/view/19241 .
- OLIVEIRA, P. B. **Proposta de modelagem de trajetórias de regiões móveis
  empregando trajetórias representativas**. Dissertação, IME, 2024,
  especialmente Capítulo 3.
- Scripts históricos do caso Beryl: `20240822 vertices.sql`,
  `20240823criatraj.sql`, `20240823 metricas.sql` (materiais de referência
  fornecidos pelo projeto). A escolha determinística de empates e o uso da
  LAEA são adaptações explicitadas, **não reprodução literal das saídas
  numéricas do SQL em EPSG:3857**.
- Pré-processamento do estudo de caso: `gee_globfire_componentes_regiao_movel.js`.

**Fronteira de conclusão:** foi reproduzida a seleção do P2 e obtido um
conjunto de indicadores reprodutíveis da abordagem dos cinco feixes.
Não foi demonstrada a equivalência integral de todas as regras do SQL
histórico, nem implementada uma metodologia formal autônoma atribuível
ao Coronel, por falta de especificação disponível.
