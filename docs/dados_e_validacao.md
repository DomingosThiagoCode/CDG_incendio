# Dados, versões e verificações — Pantanal 2020

## Proveniência

- Fonte: **JRC/GWIS GlobFire v2 — Daily Perimeters**, baseado no produto
  MODIS MCD64A1.
- Coleção utilizada no Earth Engine:
  `JRC/GWIS/GlobFire/v2/DailyPerimeters/2020`.
- Identificador do evento: `24340828`.
- Código que gera os produtos: `gee_globfire_componentes_regiao_movel.js`.
- Unidade de análise: **um único evento GlobFire**, e não todos os incêndios do
  Pantanal em 2020.

O código constrói polígonos de **área queimada acumulada** ao longo das datas
observadas. Esses polígonos não devem ser interpretados diretamente como a
posição instantânea de uma frente de fogo ativo.

## Produtos espaciais gerados pelo código atual

| Produto | Nome exportado pelo GEE | Unidade de cada feição |
| --- | --- | --- |
| P1 | `P1_componentes_<ID>.geojson` | Um componente espacial em uma data |
| P2 | `P2_regiao_movel_<ID>.geojson` | A região móvel rastreada em uma data |

No material de desenvolvimento também existem os arquivos
`P1_patches_24340828.geojson` e `P2_regiao_movel_24340828 (1).geojson`, com
nomes de atributos reorganizados. Eles representam as mesmas 57 datas e os
mesmos 978 registros componente-data (no P1), mas **não são os nomes de
exportação do código deste repositório**. Para uma cadeia reproduzível, as
transformações entre dados exportados e dados tratados precisam de script
próprio. Não se deve misturar os esquemas de colunas silenciosamente.

### Campos principais da versão diretamente exportada

**P1**

| Campo | Significado |
| --- | --- |
| `data` | Data da observação |
| `id_incendio` | Identificador do evento GlobFire |
| `rank` | Posição do componente por área **naquela data** |
| `area_km2` | Área do componente |
| `numero_componentes` | Quantidade de componentes naquela data |
| `area_total_km2` | Soma das áreas dos componentes da data |
| `proporcao_area_pct` | Participação do componente no total da data |

**P2** inclui os campos acima e também:

| Campo | Significado |
| --- | --- |
| `rank_global` | Rank do componente selecionado na data |
| `delta_area_km2` | Variação absoluta de área desde a observação anterior |
| `delta_area_pct` | Variação relativa de área desde a observação anterior |
| `delta_num_componentes` | Variação na contagem de componentes |
| `overlap_prev_pct` | Percentual da RM anterior contido na RM atual |
| `overlap_candidato_pct` | Percentual da RM atual explicado pela RM anterior |
| `distancia_prev_m` | Distância para a RM anterior (fallback) |
| `metodo_continuidade` | Seleção por sobreposição ou distância |

**Importante:** `rank` e `rank_global` não funcionam como identificadores
persistentes de um patch entre datas. A identidade temporal de cada componente
e suas relações de fusão ainda precisam ser reconstruídas geometricamente.

## Conferência inicial — evento 24340828

Os números abaixo foram obtidos comparando os arquivos GeoJSON e CSV reunidos
no histórico de desenvolvimento:

- 57 datas entre **2020-08-09** e **2020-10-09**;
- 978 feições componente-data em P1 e 57 feições em P2;
- 42 componentes em 2020-09-10 (máximo observado);
- área acumulada total na última observação: aproximadamente **984,61 km²**;
- área da região móvel na última observação: aproximadamente **954,56 km²**;
- a RM esteve no rank 1 em todas as 57 observações;
- três intervalos com lacunas de observação: 22–24/09 (2 dias), 29/09–01/10
  (2 dias) e 05–09/10 (4 dias). No total, cinco datas intermediárias não
  aparecem na série;
- em 11/09, `delta_area_km2` da RM foi aproximadamente **213,15 km²**, enquanto
  o número de componentes caiu de 42 para 25. Isso **sugere** fusões, mas a
  confirmação exige análise topológica de sobreposição entre componentes.

Na série acumulada, `distancia_prev_m` foi zero em todas as observações; fora a
primeira data, `overlap_prev_pct` ficou aproximadamente em 100%. Essas variáveis
têm baixo poder discriminativo **neste evento** devido à construção cumulativa
das geometrias. Não devem ser anunciadas como novos indicadores preditivos sem
testes em outros eventos.

## Validação automatizada disponível

O script `scripts/validar_produtos.py` verifica, sem dependências externas:

1. Estrutura GeoJSON e atributos esperados;
2. Correspondência de datas entre P1 e P2;
3. Ranks completos e sem duplicação por data no P1;
4. Consistência entre soma das áreas e `area_total_km2`;
5. Correspondência de áreas e ranks entre P2 e P1;
6. Monotonicidade das áreas acumuladas e deltas declarados;
7. Lacunas temporais da série.

Esse verificador **não mede** validade topológica, não identifica fusões, não
recalcula áreas na superfície terrestre e não avalia qualidade da detecção
remota. Essas são etapas distintas do plano de pesquisa.
