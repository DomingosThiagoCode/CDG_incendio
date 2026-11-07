# Etapa 1 — auditoria espacial dos produtos P1/P2

**Objeto:** evento GlobFire v2 `24340828`, Pantanal, 09/08 a 09/10/2020.

**Status:** Etapa 1 concluída para este estudo de caso, após experimento de
sensibilidade à regularização e revisão do validador. Os testes verificam a
integridade dos produtos, **não** certificam a exatidão dos pixels queimados,
da extração no GEE ou dos métodos científicos de regiões móveis.

## Método e reprodutibilidade

Os dois arquivos GeoJSON versionados em `dados/estudo_caso_24340828/` foram
mantidos sem alteração. A estrutura de atributos, datas, ranks e áreas
declaradas foi previamente conferida por `scripts/validar_produtos.py`.

A auditoria espacial foi executada usando `scripts/auditar_espacial.py` com
Shapely 2.2.0 e PyProj 3.8.0. São registrados separadamente os diagnósticos
de validade na interpretação planar dos vértices em longitude/latitude e
**após a reprojeção dos vértices originais** para Lambert Azimutal Equivalente
(LAEA) local, sobre WGS84. **Somente se uma geometria permanecer inválida
após a reprojeção** o validador aplica `make_valid()` em memória, registrando
o reparo. As áreas e interseções são calculadas na projeção local. Nenhum
GeoJSON de entrada é alterado.

Para reproduzir na raiz do repositório:

```bash
python -m pip install -r requirements-auditoria.txt
python scripts/validar_produtos.py \
  dados/estudo_caso_24340828/P1_componentes_24340828.geojson \
  dados/estudo_caso_24340828/P2_regiao_movel_24340828.geojson
python scripts/auditar_espacial.py \
  dados/estudo_caso_24340828/P1_componentes_24340828.geojson \
  dados/estudo_caso_24340828/P2_regiao_movel_24340828.geojson \
  --saida-json resultados/auditoria_espacial_24340828.json
python -m unittest discover -s tests -v
```

O diagnóstico detalhado, incluindo datas e feições para investigar, está
preservado em `resultados/auditoria_espacial_24340828.json`.
O experimento comparativo que fundamenta a ordem das operações está em
[`experimento_regularizacao_24340828.md`](experimento_regularizacao_24340828.md).

## Resultados principais

| Verificação | Resultado | Interpretação |
| --- | ---: | --- |
| Feições P1 / P2 | 978 / 57 | Mesmas 57 datas no estudo de caso |
| Geometrias P1 inválidas se lon/lat forem tratados como coordenadas planas | **172** (17,6%) | Autointerseções nessa interpretação |
| Geometrias P2 inválidas se lon/lat forem tratados como coordenadas planas | **55** (96,5%) | Autointerseções nessa interpretação |
| Geometrias inválidas **depois da reprojeção LAEA** | **0** em P1 e **0** em P2 | Nenhum reparo necessário no CRS adotado |
| P2 geometricamente equivalente ao P1 da mesma data/rank | **57/57** | Diferença relativa máxima ~`1,3 × 10⁻¹³` |
| Pares de componentes P1 com sobreposição de área no mesmo dia | **0** | Não determina conectividade por ponto/borda |
| Desvio mediano de área no P1 (LAEA × atributo GEE) | **−0,3375%** | Diferença sistemática de modelos de área, não erro comprovado |
| Feições com desvio de área acima de 1% | **0** | Comparação apenas diagnóstica entre modelos de área |
| Intervalos com resíduos de área acumulada acima de 1 m² | **0/56** | Resíduo de área observado: **0 m²** |
| Candidatos a fusão por sobreposição | **72** | Hipóteses, não eventos comprovados de propagação física |

### Por que o diagnóstico de validade mudou?

A biblioteca interpreta segmentos como retas no plano do CRS usado. Quando
avaliamos diretamente o GeoJSON em longitude/latitude, surgem 172/55
geometrias inválidas; depois de projetar **primeiro** os vértices originais
para LAEA local ou UTM 21S, todas ficam válidas. Esse resultado não se
generaliza a qualquer projeção (EPSG:6933 preservou 172/55 invalidezes), nem
prova que a vetorização original seja geograficamente exata.

O experimento adicional comparou `make_valid()`, `buffer(0)` e a preservação
dos originais. Reparar antes de projetar, e novamente quando necessário,
resultou em 355 partes poligonais adicionais no conjunto P1 e também no P2,
embora a variação máxima de área tenha sido inferior a 0,0002%. Esse efeito
topológico não representa automaticamente novos patches. **Decisão:**
preservar P1/P2 originais, projetar primeiro, validar no CRS adotado e reparar
**condicionalmente** apenas as geometrias ainda inválidas.

### Comparação P1 × P2

Os atributos já concordavam numericamente. Agora também foi verificado que
a geometria do P2 é praticamente idêntica à do componente correspondente no
P1 após reprojeção sem reparo. A equivalência é robusta mesmo quando
a ordem dos vértices nos dois GeoJSON é diferente. **Isso não comprova que
o algoritmo de continuidade escolheria corretamente a RM em outros eventos.**

### Evolução temporal e possível fusão em setembro

As áreas acumuladas são espacialmente não decrescentes na comparação das
datas consecutivas sob o novo procedimento. **Nenhum dos 56 intervalos**
do evento completo ou da RM apresentou resíduo de área maior que 1 m².
Os pequenos resíduos antes descritos decorriam do processamento que reparava
as coordenadas geográficas antes da reprojeção.

Na transição **10/09 → 11/09**, a quantidade de componentes passou de **42
para 25**. A componente de rank 1 em 11/09 apresentou interseção de área
maior que 1 m² com **21 componentes** observadas em 10/09. Esse é um
**candidato relevante de fusão**, mas exige avaliação dos critérios de
conectividade antes de receber essa
classificação como resultado científico.

### Comparação de modelos de área

O desvio mediano próximo de −0,34% entre áreas reconstruídas em LAEA/WGS84
e atributos declarados é sistemático. É **compatível com diferenças de
modelo de superfície ou cálculo de área**, mas a auditoria não identifica
por si só a causa exata. O resultado não justifica sobrescrever os valores
exportados pelo GEE. Na fase de métricas será necessário fixar a convenção
de cálculo e comparar as alternativas.

## Questões científicas para decidir antes do módulo de métricas

1. **Conectividade:** componentes que se tocam apenas em um vértice devem
   ser consideradas um único patch (conectividade por vértice) ou patches
   separados (conectividade por borda)? A decisão deve ser compatível com a
   construção raster/vetorial de origem e a pergunta de pesquisa.
2. **Geometrias e projeções:** manter a ordem acordada (original → projetar →
   validar → reparar somente quando necessário) e repetir o diagnóstico para
   novos IDs e outras áreas geográficas.
3. **Área/perímetro:** qual referencial geométrico e projeção serão usados
   nos indicadores, e como distinguir diferenças sistemáticas de cálculo
   de erros materiais de processamento?
4. **Fusões:** qual relação espacial e qual limiar distinguem fusão de
   componentes de coincidências numéricas decorrentes da vetorização?

## Limites desta etapa

- O limiar de **1 m²** foi escolhido apenas para tornar visíveis pequenas
  interseções/resíduos; **100 m²** é um corte diagnóstico de leitura, não
  uma tolerância aprovada pelo orientador.
- `make_valid()` pode mudar a topologia e separar anéis ou contatos pontuais;
  **neste evento nenhuma geometria precisou dele após a projeção LAEA**.
- Não foi validado o perímetro original do GlobFire contra imagens raster,
  mapas de referência ou dados de campo.
- O algoritmo do GEE **não foi reexecutado** nesta auditoria; foram usados
  os exports históricos versionados e seus hashes de referência.
- Os candidatos a fusão não representam medições diretas de dinâmica da
  frente ativa do incêndio, pois a fonte contém área queimada acumulada.

## Encaminhamento recomendado

**Etapa 2:** escrever testes sintéticos para as duas convenções de
conectividade, congelar as fórmulas e a projeção de análise para as métricas
de paisagem e executar esses indicadores sobre todo o P1, preservando o
dado bruto. A comparação de regularização já foi realizada e documentada.
