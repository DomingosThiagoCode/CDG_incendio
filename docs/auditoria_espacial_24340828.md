# Etapa 1 — auditoria espacial dos produtos P1/P2

**Objeto:** evento GlobFire v2 `24340828`, Pantanal, 09/08 a 09/10/2020.

**Status:** auditoria exploratória reproduzível, concluída; **não** equivale à
certificação científica da extração no Google Earth Engine (GEE), dos dados
de sensoriamento remoto ou dos métodos de regiões móveis.

## Método e reprodutibilidade

Os dois arquivos GeoJSON versionados em `dados/estudo_caso_24340828/` foram
mantidos sem alteração. A estrutura de atributos, datas, ranks e áreas
declaradas foi previamente conferida por `scripts/validar_produtos.py`.

A auditoria espacial foi executada usando `scripts/auditar_espacial.py` com
Shapely 2.2.0 e PyProj 3.8.0. A geometria original é analisada quanto à
validade; para realizar operações topológicas em geometrias inválidas,
`make_valid()` é aplicado **somente em memória**. As operações de área e
interseção são feitas em projeção equivalente azimutal de Lambert (LAEA),
com centro calculado a partir dos limites do evento, sobre WGS84.

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

## Resultados principais

| Verificação | Resultado | Interpretação |
| --- | ---: | --- |
| Feições P1 / P2 | 978 / 57 | Mesmas 57 datas no estudo de caso |
| Geometrias inválidas em P1 | **172** (17,6%) | Todas com autointerseção segundo Shapely |
| Geometrias inválidas em P2 | **55** (96,5%) | Também com autointerseção |
| Reparos em memória que resultaram em multipolígonos | **51** em P1 e **51** em P2 | Até **12 partes** numa feição de P1 |
| P2 geometricamente equivalente ao P1 da mesma data/rank após reparo diagnóstico | **57/57** | Diferença relativa máxima ~`2 × 10⁻¹³` |
| Pares de componentes P1 com sobreposição de área no mesmo dia | **0** | Medido após reparo diagnóstico; não garante conectividade correta por ponto/borda |
| Desvio mediano de área (feições válidas) | **−0,3374%** | Área LAEA/WGS84 em relação ao atributo do GEE |
| Feições com desvio de área acima de 1%, após reparo em memória | **0** | Comparação apenas diagnóstica entre modelos de área |
| Intervalos com resíduos de área acumulada acima de 100 m² | **0/56** | Maior resíduo observado: **33,2 m²** |
| Candidatos a fusão por sobreposição | **72** | Hipóteses, não eventos comprovados de propagação física |

### Por que as autointerseções importam?

Várias geometrias são aceitas nos produtos originais, mas não são polígonos
válidos segundo as regras topológicas usadas pela biblioteca GIS. Em 51
feições do P1, o reparo diagnóstico produz mais de uma parte poligonal, até
12 em um único registro. Isso pode alterar a interpretação de **patch**,
perímetro, conectividade e shape index.

Portanto, **não recomendamos substituir automaticamente os GeoJSON por versões
reparadas** antes de definir o conceito de conexão dos componentes e as
regras de tratamento de autointerseções. A análise de métricas de paisagem
deve declarar qual geometria será usada e registrar o impacto de eventuais
tratamentos.

### Comparação P1 × P2

Os atributos já concordavam numericamente. Agora também foi verificado que
a geometria do P2 é praticamente idêntica à do componente correspondente no
P1 após um reparo diagnóstico comum. A equivalência é robusta mesmo quando
a ordem dos vértices nos dois GeoJSON é diferente. **Isso não comprova que
o algoritmo de continuidade escolheria corretamente a RM em outros eventos.**

### Evolução temporal e possível fusão em setembro

As áreas acumuladas apresentam pequenos resíduos geométricos entre datas,
mesmo quando os atributos de área são monotônicos. Com o procedimento
diagnóstico, 22 intervalos do evento completo e 18 da RM tiveram resíduos
maiores que 1 m², porém **nenhum ultrapassou 100 m²**. Esses valores são
resíduos geométricos muito pequenos, não evidências de redução material da
área queimada.

Na transição **10/09 → 11/09**, a quantidade de componentes passou de **42
para 25**. A componente de rank 1 em 11/09 apresentou interseção de área
maior que 1 m² com **21 componentes** observadas em 10/09. Esse é um
**candidato relevante de fusão**, mas exige avaliação dos critérios de
conectividade e das consequências de `make_valid()` antes de receber essa
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
2. **Tratamento de geometrias inválidas:** medir sobre a geometria original
   quando possível, reparar para as operações, ou redefinir os componentes?
   É necessário quantificar o efeito da escolha sobre perímetro e forma.
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
  as estatísticas de overlay são derivadas de **geometrias reparadas em memória**.
- Não foi validado o perímetro original do GlobFire contra imagens raster,
  mapas de referência ou dados de campo.
- O algoritmo do GEE **não foi reexecutado** nesta auditoria; foram usados
  os exports históricos versionados e seus hashes de referência.
- Os candidatos a fusão não representam medições diretas de dinâmica da
  frente ativa do incêndio, pois a fonte contém área queimada acumulada.

## Encaminhamento recomendado

**Etapa 2:** escrever testes sintéticos para as duas convenções de
conectividade, avaliar um conjunto limitado de opções de regularização e
quantificar diferenças de área/perímetro/forma, preservando o dado bruto.
Somente depois congelar as fórmulas e executar as métricas sobre todo o P1.
