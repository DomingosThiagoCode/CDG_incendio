# CDG Incêndio — análise espaço-temporal de áreas queimadas

**Processamento principal: Python (Shapely/PyProj); GEE: extração P1/P2; QGIS: visualização.**

[**Fechamento da Etapa 4 e migração do SQL**](docs/fechamento_etapa4.md): base científica em Barbosa e Oliveira (2022), comparação TR × IGT e redução geométrica; SQL arquivado como referência não executada.

Projeto para análise espaço-temporal de grandes incêndios utilizando **Google Earth Engine**, **QGIS** e, posteriormente, ferramentas de análise espacial e métricas de paisagem.

A implementação atual utiliza os dados **JRC/GWIS GlobFire v2 – Daily Perimeters** para reconstruir a evolução acumulada de um incêndio ao longo do tempo, separar seus componentes espaciais e acompanhar automaticamente o componente principal como uma **região móvel**.

## Objetivo

O objetivo é estudar a evolução espacial de um grande incêndio a partir de duas escalas complementares:

1. análise de **todos os componentes desconectados** da área queimada;
2. rastreamento temporal do **componente principal**, tratado como uma região móvel.

Isso permite investigar crescimento, fragmentação, conectividade, surgimento de novos focos e fusões entre componentes.

## Estudo de caso atual

O evento utilizado inicialmente para desenvolvimento e validação do código é:

```text
GlobFire ID: 24340828
Ano: 2020
Região: Pantanal
```

O código, entretanto, foi desenvolvido para permitir a troca do evento sem utilizar datas específicas ou regras exclusivas para esse incêndio.

### Estado dos dados do estudo de caso

Uma conferência dos GeoJSON exportados para o ID `24340828` encontrou:

| Indicador | Resultado |
| --- | ---: |
| Período observado | 09/08/2020 a 09/10/2020 |
| Datas com registros | 57 |
| Registros componente-data (P1) | 978 |
| Registros da região móvel (P2) | 57 |
| Maior quantidade de componentes em uma data | 42 |
| Área acumulada do evento na última observação | 984,61 km² |
| Área da RM na última observação | 954,56 km² |

**Atenção:** os 978 registros do P1 não representam 978 incêndios ou 978
componentes com identidade permanente. São feições repetidas ao longo de datas
distintas. Neste estudo de caso, a RM permaneceu como o maior componente em
todas as 57 observações; isso não demonstra que a regra de continuidade terá o
mesmo comportamento em outros incêndios.

O inventário das versões dos produtos, limitações e resultados conferidos está
em [docs/dados_e_validacao.md](docs/dados_e_validacao.md).

Os GeoJSON desta versão do estudo de caso estão em
[`dados/estudo_caso_24340828/`](dados/estudo_caso_24340828/). São uma
**fotografia dos exports históricos**, não uma nova execução do GEE nem uma
validação científica final. O [registro de marcos](docs/marcos.md) documenta a
passagem dos protótipos à fase de testes e automações.

## Arquivo principal

```text
gee_globfire_componentes_regiao_movel.js
```

O script é executado no **Google Earth Engine Code Editor**.

## Como usar

No início do script, altere apenas:

```javascript
var anoDataset = 2020;
var idIncendio = 24340828;
```

Para analisar outro incêndio, substitua o ID:

```javascript
var anoDataset = 2020;
var idIncendio = OUTRO_ID;
```

Caso o evento pertença a outro ano, altere também `anoDataset`.

Depois:

1. cole ou abra o script no Google Earth Engine;
2. clique em **Run**;
3. confira os resultados no Console e no mapa;
4. abra a aba **Tasks**;
5. execute os dois exports.

### Conferir os GeoJSON exportados

Após baixar os dois produtos do GEE, rode a verificação de estrutura e
consistência numérica (Python 3, sem dependências externas):

```bash
python scripts/validar_produtos.py \
  dados/estudo_caso_24340828/P1_componentes_24340828.geojson \
  dados/estudo_caso_24340828/P2_regiao_movel_24340828.geojson
```

O script compara datas, ranks, áreas, quantidades de componentes e deltas. **Não
faz validação topológica** nem substitui uma verificação da metodologia
cartográfica.

### Auditoria espacial exploratória (etapa 1)

Uma auditoria geométrica **separada**, que não modifica P1/P2, pode ser
reproduzida com Python 3, Shapely e PyProj:

```bash
python -m pip install -r requirements-auditoria.txt
python scripts/auditar_espacial.py \
  dados/estudo_caso_24340828/P1_componentes_24340828.geojson \
  dados/estudo_caso_24340828/P2_regiao_movel_24340828.geojson \
  --saida-json resultados/auditoria_espacial_24340828.json
python -m unittest discover -s tests -v
```

Resultados, ressalvas e questões metodológicas estão em
[docs/auditoria_espacial_24340828.md](docs/auditoria_espacial_24340828.md).
A auditoria **projeta primeiro** os vértices originais para LAEA local, valida
nesse CRS e só utiliza reparos de geometria **em memória e condicionalmente**.
Para este estudo de caso, não houve geometrias inválidas após a reprojeção.
O [experimento de sensibilidade à regularização](docs/experimento_regularizacao_24340828.md)
compara o original, `make_valid()` e `buffer(0)`. Os GeoJSON originais permanecem
inalterados. A Etapa 1 está concluída.

### Métricas de paisagem (etapa 2)

O módulo vetorial calcula indicadores por patch e por data, sobre os
**mesmos P1 originais**, com área, perímetro e distâncias em projeção LAEA
local. Inclui área acumulada, crescimento entre observações, número de
patches, dominância, índice de forma vetorial e distância ao vizinho mais
próximo. Preserva separadamente as áreas declaradas pelo GEE para não
confundir os referenciais de cálculo.

```bash
python -m pip install -r requirements-auditoria.txt
python scripts/calcular_metricas_paisagem.py \
  dados/estudo_caso_24340828/P1_componentes_24340828.geojson \
  --saida resultados/etapa2
python -m unittest discover -s tests -v
```

Os resultados são gravados em `resultados/etapa2/` como CSVs por patch,
por data e diagnóstico de conectividade por contato, acompanhados por
um JSON de procedência e qualidade. O código usa o **ID lido do GeoJSON**,
sem fixar o estudo de caso no processamento.

**Ressalva científica importante:** a análise encontrou **657 pares
de contatos pontuais entre patches ao longo de 57 datas**. Um agrupamento
exploratório de feições por contato geométrico reduz a soma de 978
componentes-data para 369 grupos-data e modifica a contagem em 56/57 datas.
O experimento **não equivale diretamente à conectividade raster 8** e
**não altera** o P1/P2 original. Consulte os números, fórmulas,
limitações e referências em
[docs/metricas_paisagem_24340828.md](docs/metricas_paisagem_24340828.md).

### Continuidade temporal dos patches (etapa 3)

O módulo da Etapa 3 reconstrói um **grafo de interseções por área** entre
patches de observações consecutivas do P1. Classifica correspondências
1→1, convergências N→1, divisões 1→N, reorganizações e surgimentos sem
predecessor. Usa sobreposição de área maior que **1 m²** como tolerância
numérica; contatos apenas por vértice ou borda não definem vínculos.

```bash
python scripts/rastrear_linhagens_patches.py \
  dados/estudo_caso_24340828/P1_componentes_24340828.geojson \
  --saida resultados/etapa3
python -m unittest discover -s tests -v
```

As saídas em `resultados/etapa3/` incluem CSVs com linhagens conservadoras,
vínculos, eventos e resumo de transições, um JSON de procedência e um
**GeoJSON de convergências para conferência no QGIS**. Para o evento de
referência, foram encontrados **963 vínculos de área, 72 convergências
geométricas e 219 patches sem predecessor por área** entre as observações.
Na transição **10→11/09/2020**, 21 patches de 10/09 se relacionam por área
com um patch de 11/09. Esses números **não demonstram ignições ou fusões
físicas do fogo**. Consulte o relatório e as limitações em
[docs/linhagens_patches_24340828.md](docs/linhagens_patches_24340828.md).

## Funcionamento

O processamento realiza automaticamente as seguintes etapas:

```text
GlobFire
   ↓
Filtragem pelo ID
   ↓
Ordenação automática das datas
   ↓
Construção da área queimada acumulada
   ↓
Separação dos componentes desconectados
   ↓
┌───────────────────────┬─────────────────────────┐
│                       │                         │
▼                       ▼
P1                      P2
Todos os componentes    Região móvel principal
```

### Separação de componentes

Para cada data, a geometria acumulada é decomposta nas subgeometrias que
compõem o P1. Elas não se sobrepõem em área relevante neste estudo de caso,
mas **podem compartilhar vértices**; portanto, não devem ser descritas
indiscriminadamente como desconectadas em qualquer convenção topológica.

Cada componente possui atributos como:

```text
data
rank
area_km2
numero_componentes
area_total_km2
proporcao_area_pct
```

O `rank` é calculado pela área:

```text
rank = 1 → maior componente da data
rank = 2 → segundo maior componente
...
rank = N → componente N
```

O número de componentes não é fixo. O código trata automaticamente qualquer quantidade `N`.

## Produto 1: componentes

O primeiro produto exportado é:

```text
P1_componentes_<ID>
```

Exemplo:

```text
P1_componentes_24340828
```

Ele contém **todos os componentes de todas as datas**.

Cada linha corresponde a uma feição poligonal independente em determinado instante.

Esse produto é destinado principalmente à análise de métricas de paisagem, como:

- número de patches;
- área individual;
- área total;
- área do maior patch;
- proporção da área concentrada no maior patch;
- perímetro;
- índice de forma;
- elongação;
- fragmentação;
- conectividade;
- surgimento de componentes;
- possíveis fusões.

## Produto 2: região móvel

O segundo produto é:

```text
P2_regiao_movel_<ID>
```

Exemplo:

```text
P2_regiao_movel_24340828
```

Ele contém **uma geometria por data**, correspondente à região móvel rastreada ao longo do incêndio.

A região móvel é escolhida da seguinte forma:

### Primeira data

Na primeira observação, o maior componente é escolhido como região móvel inicial.

### Datas seguintes

A partir daí, o componente não é escolhido novamente apenas pelo tamanho.

O código compara todos os componentes da nova data com a região móvel anterior e seleciona aquele que possui **maior continuidade espacial por sobreposição**.

Assim, o `rank` não representa a identidade da região móvel.

É possível, por exemplo, que a região móvel seja temporariamente o segundo maior componente e continue sendo rastreada normalmente.

## Fusões

Quando o componente rastreado se conecta a outro patch, o novo polígono resultante passa a representar a região móvel.

Isso permite acompanhar situações como:

```text
t1

A ← região móvel
B
C


t2

A cresce
B cresce


t3

A + B → novo componente conectado
```

A fusão é incorporada automaticamente à trajetória da região móvel.

## Detecção automática do maior salto

O código não utiliza uma data previamente escolhida para procurar mudanças importantes.

Para cada transição é calculado:

```text
ΔA = área atual da RM - área anterior da RM
```

A maior variação positiva é identificada automaticamente.

O script também determina:

```text
data anterior
data do maior salto
data posterior
```

permitindo inspecionar visualmente a transformação.

## Indicadores armazenados no P2

Entre os principais campos estão:

```text
area_km2
area_total_km2
numero_componentes

delta_area_km2
delta_area_pct
delta_area_total_km2

delta_num_componentes

rank_global
rm_eh_maior

overlap_prev_km2
overlap_prev_pct
overlap_candidato_pct

distancia_prev_m

metodo_continuidade
```

### `overlap_prev_pct`

Indica quanto da região móvel anterior está contido no componente atual.

Como a análise utiliza área queimada acumulada, valores próximos de `100%` são esperados enquanto houver continuidade espacial.

### `overlap_candidato_pct`

Indica quanto da geometria atual já pertencia à região móvel anterior.

Valores menores podem indicar forte crescimento ou incorporação de novas áreas.

### `delta_num_componentes`

Representa a variação da quantidade de componentes entre duas datas.

Exemplo:

```text
20 componentes → 17 componentes

delta_num_componentes = -3
```

Quando a área aumenta e o número de componentes diminui, o intervalo pode indicar conexão ou fusão entre patches e deve ser investigado espacialmente.

## Validação no QGIS

Os produtos podem ser carregados diretamente no QGIS.

Para analisar uma única data do P1, aplique um filtro no campo `data` ou `data_millis`.

Depois utilize simbologia categorizada pelo campo:

```text
rank
```

Assim cada componente pode ser visualizado separadamente.

É importante diferenciar:

- **componentes desconectados**: polígonos independentes;
- **buracos internos**: áreas vazias dentro de um mesmo componente.

Buracos não são contabilizados como novos componentes.

## Etapa 4: trajetórias da região móvel (P2)

O script [`scripts/analisar_regiao_movel.py`](scripts/analisar_regiao_movel.py)
reexecuta em Python a regra de continuidade do P2 a partir dos componentes
do P1, extrai **cinco trajetórias representativas** (N, S, L, O, centroide),
e calcula distância, azimute, avanços cardeais e métricas do **polígono
integral** (área, Jaccard e índice de forma). Ele também produz as cinco
linhas GeoJSON para visualizar no QGIS.

No evento `24340828`, a seleção reproduziu **57/57 ranks do P2**.
Foram gerados **285 pontos, 280 segmentos e 56 transições espaciais**,
preservando os arquivos originais. A soma das mudanças entre centroides é
**34,072 km**, um descritor da mudança da geometria acumulada — **não**
o percurso da frente de fogo.

```bash
python scripts/analisar_regiao_movel.py \
  dados/estudo_caso_24340828/P1_componentes_24340828.geojson \
  dados/estudo_caso_24340828/P2_regiao_movel_24340828.geojson \
  --saida resultados/etapa4
```

**Terminologia atual:** **TR — Trajetórias Representativas**, adaptada de
Oliveira e Barbosa (2025); **IGT — Incrementos Geométricos Temporais**,
definida operacionalmente por diferença `R(t+1) \ R(t)` no organograma.
Os apelidos militares anteriores ficam apenas no histórico de proveniência.
O diagnóstico do polígono inteiro desta primeira implementação não é, por
si, a definição de IGT. Veja o [relatório da Etapa 4](docs/regioes_moveis_24340828.md).

### SQLs generalizados e comparação TR × IGT

Em [`sql/`](sql/) estão os novos SQLs **PostGIS 3+**, independentes de ID,
com views para as cinco trajetórias, diferença geométrica por transição,
componentes do incremento e comparação conjunta. O
[`sql/README.md`](sql/README.md) especifica o formato da tabela de entrada,
os comandos e a rastreabilidade das **três fontes SQL originais** de Priscila.
O método não depende de tabelas do furacão Beryl ou de projeção Web Mercator.

Para **testar IGT de forma independente** com os GeoJSON reais do Pantanal:

```bash
python scripts/analisar_incrementos_geometricos.py \
  dados/estudo_caso_24340828/P1_componentes_24340828.geojson \
  dados/estudo_caso_24340828/P2_regiao_movel_24340828.geojson \
  --saida resultados/etapa4
python -m unittest discover -s tests -v
```

O ID `24340828` resultou em **56 transições, 949,843489 km² de área
incremental total e 506 partes geométricas** (incluindo fragmentos menores
que 1 m²). O teste espacial independente foi executado; **as views SQL
precisam ser executadas e confrontadas em um servidor PostGIS real**.
Números, definições, limites e pontos para discussão estão em
[`docs/comparacao_tr_igt_24340828.md`](docs/comparacao_tr_igt_24340828.md).


## Etapa 5 — síntese integrada do incêndio

O novo script [integrar_etapa5.py](scripts/integrar_etapa5.py) cruza a
evolução total do P1, os eventos geométricos entre patches, os indicadores
TR e os incrementos IGT do P2, usando sempre as mesmas datas e projeção LAEA.

**Novidade analítica:** separa, em cada transição, a área nova de fato no
evento e a área **já queimada anteriormente** que foi incorporada ao P2.
Isso impede interpretar fusões de patches como se todo o aumento do P2
representasse novas queimadas.

O script gera séries temporais, CSVs comparativos, gráficos, mapas
e relatório interpretativo, sem alterar os GeoJSON originais:

~~~bash
python -m pip install -r requirements-auditoria.txt
python scripts/integrar_etapa5.py --id 24340828 --saida resultados/etapa5
~~~

Os insumos são os P1/P2 e os CSVs já produzidos nas Etapas 2–4 do mesmo ID.
O processamento para outro ID exige primeiro gerar seus dados; a aquisição
automática via interface é uma extensão futura.

**Documentação:** [metodologia e critérios](docs/etapa5_metodologia.md);
[relatório de resultados](docs/analise_integrada_24340828.md);
[produtos versionados](resultados/etapa5/). A análise de fases pela curva
acumulada é descritiva e não infere causalidade física do incêndio.

## Etapa 5: síntese integrada do incêndio

A implementação principal está em [`scripts/integrar_etapa5.py`](scripts/integrar_etapa5.py), com
[metodologia](docs/etapa5_metodologia.md) e
[relatório do Pantanal](docs/analise_integrada_24340828.md).
Ela combina as métricas P1, os eventos topológicos da Etapa 3 e os
descritores de P2: **TR (cinco trajetórias de Priscila Backes de Oliveira)**
e **IGT (diferenças geométricas, seguindo o trabalho de Barbosa e Oliveira, 2022)**.
A implementação não substitui os conceitos científicos desses métodos.

O incremento geométrico do P2 é decomposto entre área antes queimada fora da
componente principal e área realmente nova do evento, evitando confundir fusões
com crescimento inédito da área detectada.

```bash
python -m pip install -r requirements-auditoria.txt
python scripts/integrar_etapa5.py --id 24340828 --saida resultados/etapa5
python -m unittest discover -s tests -v
```

Os CSVs, mapas, gráficos e um relatório são versionados em
[`resultados/etapa5/`](resultados/etapa5/). A segmentação temporal em
fases é **exploratória**, não validação causal do comportamento do fogo.

## Etapa 6: auditoria científica interna e validação externa planejada

A [metodologia da Etapa 6](docs/protocolo_validacao_independente.md)
estabelece níveis de evidência, protocolo de comparação do GlobFire com
imagens de sensores independentes e testes de sensibilidade:
fragmentação por contatos pontuais, fases estatísticas e direções TR × IGT.

~~~bash
python scripts/validar_cientificamente_etapa6.py --id 24340828 --saida resultados/etapa6
python -m unittest discover -s tests -v
~~~

Produz CSVs, resumo JSON, relatório e camada de revisão QGIS.
**Auditoria interna não equivale a validação externa da área queimada
nem demonstra causas físicas do incêndio.** As imagens independentes,
revisão do orientador e ensaio de outro evento continuam pendentes.

## Próximas etapas

**Etapa 4 (Python):** executar a rotina integrada e conferir as saídas de comparação TR × IGT. A validação de um segundo ID e a análise científica integrada continuam no backlog. PostGIS não é mais dependência.


O desenvolvimento previsto inclui (itens ainda não finalizados ou não
reproduzidos integralmente neste repositório):

- validar cientificamente os critérios de identidade e as convergências
  geométricas junto ao orientador;
- avaliar indicadores adicionais de fragmentação/conectividade que não sejam
  redundantes e que respeitem a escala da fonte;
- comparar a execução **PostGIS** dos SQLs generalizados com o Python e
  com o SQL histórico de Oliveira/Barbosa, registrando projeção/desempate;
- obter o PDF do INPE, conferir a equivalência entre a formulação descrita
  e o **IGT** operacional, antes de qualquer atribuição autoral formal;
- integrar as duas escalas de análise em mapas, gráficos e interpretação;
- consolidar um pipeline executável unificado em Python; manter SQL somente como arquivo histórico para auditoria opcional.

O estudo de caso também já possui, fora deste repositório, uma tabela de
métricas diárias do P1 e um CSV de análise de trajetórias do P2. O procedimento
que gerou todas essas tabelas ainda precisa ser consolidado e documentado para
que terceiros possam reproduzi-lo.

Veja o [roteiro de desenvolvimento](docs/roteiro.md), incluindo a frente
experimental de atributos destinados a modelos de aprendizado de máquina.

## Estrutura atual do repositório

```text
CDG_incendio/
│
├── gee_globfire_componentes_regiao_movel.js
├── scripts/
│   ├── validar_produtos.py
│   ├── calcular_metricas_paisagem.py
│   ├── rastrear_linhagens_patches.py
│   ├── analisar_regiao_movel.py
│   └── analisar_incrementos_geometricos.py
├── sql/
│   ├── 01_trajetorias_representativas.sql
│   ├── 02_incrementos_geometricos_temporais.sql
│   ├── 03_comparacao.sql
│   └── README.md
├── docs/
│   ├── dados_e_validacao.md
│   ├── roteiro.md
│   ├── metricas_paisagem_24340828.md
│   ├── linhagens_patches_24340828.md
│   ├── regioes_moveis_24340828.md
│   └── comparacao_tr_igt_24340828.md
├── resultados/
│   ├── etapa2/
│   ├── etapa3/
│   └── etapa4/
└── README.md
```

O script do GEE foi mantido na raiz para preservar o caminho utilizado até agora.
Os dados volumosos e os arquivos históricos de experimentação não são
incorporados automaticamente ao repositório: antes de publicar um conjunto de
dados, é necessário documentar sua origem, licença, versão e método de geração.

## Tecnologias

- Google Earth Engine
- JavaScript
- JRC/GWIS GlobFire v2
- QGIS
- PostgreSQL/PostGIS
- Git/GitHub

## Status

Em desenvolvimento.

A etapa atual já possui:

- seleção de incêndio por ID;
- datas detectadas automaticamente;
- área acumulada;
- tratamento de `N` componentes;
- separação dos patches;
- rastreamento da região móvel por continuidade;
- detecção automática do maior salto;
- geração dos produtos P1 e P2;
- validação inicial no QGIS;
- métricas vetoriais reproduzíveis e sensibilidade de contato (Etapa 2);
- grafo de sobreposição temporal e diagnóstico de convergências (Etapa 3);
- cinco feixes de trajetórias e indicadores integrais de P2, com reprodução
  independente da seleção por continuidade (Etapa 4, núcleo computacional).
