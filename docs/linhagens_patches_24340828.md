# Etapa 3 — continuidade temporal e convergências de patches

**Estudo de caso:** GlobFire v2, incêndio `24340828` (Pantanal, 2020).
**Base:** o P1 vetorial da Etapa 1, **inalterado**, com 978 registros de
patch por data e 57 observações entre 09/08 e 09/10/2020.

## Pergunta respondida

Como cada componente espacial do P1 se relaciona com os componentes da
**observação seguinte**, considerando que os perímetros são de **área
queimada acumulada**?

Esta etapa estabelece um **grafo de sobreposições entre datas**, não
reconstitui trajetórias de frentes ativas, ignições ou fusões físicas do fogo.
Também não refaz a conectividade raster de 4 ou 8 vizinhos: a unidade de
análise continua sendo o patch vetorial que já existe em P1.

## Regra de associação

1. Carregar e validar os P1 usando o mesmo leitor da Etapa 2, sem alterar
   geometrias de origem.
2. Reprojetar cada polígono para LAEA local sobre WGS84 (o mesmo centro
   calculado a partir dos limites do evento). Verificar validade plana e
   aplicar reparo apenas quando necessário; neste evento foram **0** reparos.
3. Para cada par de datas observadas consecutivas, criar uma aresta entre o
   patch `i` anterior e `j` atual se:

   `área(geom_i_anterior ∩ geom_j_atual) > 1 m²`.

   O limiar de 1 m² é **tolerância numérica**, muito inferior à escala da
   grade MODIS. Não é distância mínima física entre incêndios.
   Arestas com contato apenas pontual ou linear **não** são criadas.
4. Formar componentes conexas do **grafo bipartido de arestas por área**.
   A classificação corresponde ao formato desse grafo, por transição:

   | Configuração | Nome na saída | Interpretação limitada |
   | --- | --- | --- |
   | 1 patch anterior, 1 atual | `continuacao` | Correspondência geométrica 1→1. |
   | N anteriores, 1 atual, N>1 | `convergencia` | Patches anteriores aparecem associados ao mesmo atual. |
   | 1 anterior, N atuais, N>1 | `divergencia` | Um patch anterior se relaciona com vários posteriores. |
   | N anteriores, M atuais, ambos >1 | `reorganizacao` | Associação muitos-para-muitos. |
   | 0 anteriores, 1 atual | `surgimento_sem_sobreposicao` | Área detectada sem predecessor por área. **Não comprova ignição**. |
   | 1 anterior, 0 atuais | `sem_sucessor` | Não foi encontrado sucessor: requer auditoria. **Não comprova extinção**. |

5. Dar a cada linha do P1 um identificador estável **de patch-data**
   (`AAAA-MM-DD_rNNN`) e, adicionalmente, uma **linhagem conservadora**.
   O identificador `Lxxxxxx` é mantido somente em correspondências 1→1;
   quando ocorre convergência, divisão ou reorganização, novas linhagens
   começam e as origens ficam registradas em colunas separadas. Isso evita
   escolher arbitrariamente qual linhagem "venceu" uma convergência.

A percentagem de área anterior vinculada é a **soma das áreas de interseção
dividida pela soma das áreas anteriores**. A área atual com predecessor usa
o denominador da data atual. O código rejeita somas de interseções que
superem a área do próprio patch além da tolerância numérica: esse quadro
denunciaria sobreposição indevida entre patches de uma mesma data.

**Sem interpolação:** o procedimento liga observações disponíveis, mesmo
quando há lacunas de dois ou quatro dias. A interpretação é, portanto,
"entre observações", e não "no dia seguinte" de forma irrestrita.

## Resultados do caso 24340828

| Indicador | Resultado |
| --- | ---: |
| Registros P1 processados | **978** |
| Datas observadas | **57** |
| Transições observadas | **56** |
| Vínculos por interseção de área | **963** |
| Eventos topológicos do grafo | **976** |
| Correspondências 1→1 | **685** |
| Eventos de convergência N→1 | **72** |
| Surgimentos sem sobreposição anterior | **219** |
| Divisões, reorganizações ou patches sem sucessor | **0** neste caso |
| Linhagens conservadoras identificadas | **293** |
| Retenção mínima de área anterior entre transições | **>99,9999999%** |
| Contatos somente pontuais **entre datas** (pares somados) | **1.147** |

O número de linhagens é um **resultado da regra conservadora**, não o
número de incêndios: existem 2 na primeira observação; as 219 detecções
sem predecessor e 72 convergências iniciam outras linhagens. Os 1.147
contatos pontuais entre datas são **diferentes** dos 657 pares de contato
pontual **dentro da mesma data** registrados na Etapa 2. Ambos somam
pares em diferentes datas e não são contagens de ocorrências independentes
na paisagem.

O resultado não mudou ao variar **somente o limiar absoluto** da interseção
entre `0`, `1`, `10`, `100` e `1.000 m²` (963 vínculos e mesmas categorias
em todos os casos). Esse teste apoia a estabilidade **numérica** deste
caso específico, mas não valida uma hipótese física de fusão.

### Intervalo central: 9 a 12 de setembro

| Transição | Patches antes → depois | Convergências | Surgimentos sem predecessor | Crescimento líquido detectado |
| --- | ---: | ---: | ---: | ---: |
| 09→10/09 | 34 → 42 | 5 | 17 | 43,8525 km² |
| **10→11/09** | **42 → 25** | **1** | 3 | **107,8240 km²** |
| 11→12/09 | 25 → 18 | 2 | 3 | 37,0106 km² |

Na passagem de **10 para 11/09**, há uma convergência particularmente
expressiva: **21 patches anteriores** correspondem por interseção a **um
único patch atual** (`20200910_20200911_E001`). A área somada desses 21
patches era aproximadamente **740,19 km²** e o patch posterior abrangia
**847,16 km²**. A diferença do grupo é **106,97 km²**, equivalente a
cerca de **99,2% do crescimento líquido da área queimada acumulada** no
intervalo. Não significa que 21 focos fisicamente se encontraram nesse dia:
os dados mostram a configuração **detectada em perímetros acumulados**.

Entre 11 e 12/09, ocorre um grupo de convergência **10→1** e outro **2→1**.
Isso indica que a redução na contagem de patches tem forte relação com a
associação espacial de áreas previamente separadas, sob a regra adotada.

### Limitações que devem constar do relatório

- A geometria vetorial e a resolução nominal de origem (MODIS MCD64A1,
  aproximadamente 500 m) limitam qualquer interpretação de conectividade
  fina. O limiar de 1 m² é um **critério computacional**, não uma resolução
  de medição do satélite.
- `surgimento_sem_sobreposicao` significa apenas que **não há interseção de
  área acima do limiar** com patches da observação anterior. Pode refletir
  detecção tardia, limite de observação ou novo trecho queimado.
- `convergencia` é evento do **grafo de sobreposição**. O surgimento de uma
  ponte de pixels queimados pode explicar sua geometria, mas inferir ligação
  física entre frentes exige outras fontes.
- No período há três intervalos sem observação diária consecutiva:
  **22→24/09 (2 dias), 29/09→01/10 (2 dias), 05→09/10 (4 dias)**.
- Não foi aplicada distância mínima nem *buffer* para vincular patches.
  Contatos pontuais não bastam para herdar identidade.
- O resultado é específico do **ID 24340828**. O script aceita outros
  IDs/datas, mas sua generalização científica ainda não foi testada.

## Entregáveis e conferência no QGIS

Na pasta `resultados/etapa3/`:

1. `linhagens_patches_<ID>.csv` — uma linha por patch e data (978 linhas),
   com identificador estável, linhagem, pais, sucessores e tipo de transição.
2. `vinculos_temporais_<ID>.csv` — uma linha por aresta de área entre
   observações (963 linhas), com áreas e proporções de sobreposição.
3. `eventos_topologicos_<ID>.csv` — uma linha por grupo de correspondência
   no grafo, inclusive surgimentos sem predecessor (976 linhas).
4. `resumo_transicoes_<ID>.csv` — uma linha por uma das 56 transições, com
   contagens, cobertura da área anterior e área acumulada.
5. `convergencias_para_qgis_<ID>.geojson` — **72 feições originais WGS84**
   dos patches atuais envolvidos em convergências, com atributos do evento
   para filtro, simbologia e inspeção espacial. Não substitui P1.
6. `resumo_linhagens_<ID>.json` — parâmetros, procedência, hash SHA-256 do
   P1, projeção e contagens.

Para inspecionar o caso de 10→11/09 no QGIS, carregar a camada de
convergências e filtrar:

`"data_anterior" = '2020-09-10' AND "data_atual" = '2020-09-11'`.

Para verificar os 21 patches anteriores, carregar o P1 original na mesma
visualização, filtrar `data = '2020-09-10'` e usar a lista
`ranks_anteriores` do evento. A geometria do GeoJSON diagnóstico é copiada
**sem alterações** do próprio P1, em longitude/latitude WGS84.

## Reprodução

```bash
python -m pip install -r requirements-auditoria.txt
python scripts/rastrear_linhagens_patches.py \
  dados/estudo_caso_24340828/P1_componentes_24340828.geojson \
  --saida resultados/etapa3 \
  --area-minima-sobreposicao-m2 1
python -m unittest discover -s tests -v
```

Os resultados exploratórios **não mudam os produtos P1/P2** nem definem
automaticamente a abordagem da Major ou do Coronel. As decisões sobre
interpretação de fusões aparentes, área de referência para fragmentação e
validação externa permanecem temas para a orientação.

Referências de base: Artés et al. (2019), *Scientific Data* 6, 296,
https://doi.org/10.1038/s41597-019-0312-2 (GlobFire); Zatelli et al.
(2019), *ISPRS IJGI* 8, 586, https://doi.org/10.3390/ijgi8120586
(sensibilidade à conectividade raster). Ver também o relatório da
[Etapa 2](metricas_paisagem_24340828.md) para distinções entre as métricas.
