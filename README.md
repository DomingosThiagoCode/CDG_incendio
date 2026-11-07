# CDG Incêndio — análise espaço-temporal de áreas queimadas

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
A auditoria usa reparos de geometria apenas **em memória**, para fins
diagnósticos; os GeoJSON originais permanecem inalterados.

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

Para cada data, a geometria acumulada é dividida em seus componentes espacialmente desconectados.

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

## Próximas etapas

O desenvolvimento previsto inclui (itens ainda não finalizados ou não
reproduzidos integralmente neste repositório):

- identificação persistente dos patches ao longo do tempo;
- classificação de nascimento, continuidade e fusão;
- métricas de paisagem por componente;
- análise da conectividade;
- cálculo de perímetro e fator de forma;
- integração com QGIS;
- processamento das trajetórias representativas;
- análise dos extremos Norte, Sul, Leste e Oeste;
- trajetória do centroide;
- métricas de deslocamento, direção e deformação;
- integração com PostgreSQL/PostGIS.

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
│   └── validar_produtos.py
├── docs/
│   ├── dados_e_validacao.md
│   └── roteiro.md
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
- validação inicial no QGIS.
