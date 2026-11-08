# Etapa 5 — Análise integrada de paisagem, linhagens e regiões móveis

**Estudo de caso:** Pantanal (GlobFire v2; ID 24340828), 09/08/2020 a 09/10/2020.

## Objetivo

Transformar os produtos computacionais das etapas anteriores numa interpretação
espaço-temporal auditável, cruzando três fenômenos **distintos**:

1. **Crescimento da área queimada acumulada no evento (P1):** nova área
   detectada entre observações, independentemente de qual patch a contém.
2. **Reorganização da conectividade (Etapa 3):** correspondências e
   convergências entre componentes geométricos do P1.
3. **Evolução da componente rastreada (P2):** suas trajetórias representativas
   (TR) e áreas de incremento (IGT), inclusive quando incorpora componentes
   que já estavam queimados antes.

O objetivo **não** é inferir velocidade, direção física instantânea de uma
frente ativa ou causalidade meteorológica a partir de polígonos acumulados.

## Descoberta central e identidade geométrica

Para geometrias de duas observações consecutivas, defina:

- T0, T1: **uniões de todos os patches P1** antes e depois;
- R0, R1: **região móvel P2** nas duas datas;
- J = R1 \ R0: novo espaço ocupado geometricamente pelo P2.

Separamos J em dois conjuntos disjuntos:

- **J_antigo = J ∩ T0**: área queimada que já estava no evento na observação
  anterior, mas não pertencia ao P2 anterior; é **incorporação de área
  previamente queimada**, frequentemente por convergência de componentes.
- **J_novo = J \ T0**: área de fato nova no evento e agora incluída no P2.
- Logo, **A(J) = A(J_antigo) + A(J_novo)**, salvo resíduos de precisão GEOS.

O crescimento do evento é **A(T1 \ T0)**, diferente da expansão geométrica
**A(R1 \ R0)**, inclusive em intervalos com fusões. Também calculamos
**A((T1 \ T0) \ R1)**, nova área do evento que está fora do P2 atual.

**Exemplo já conhecido:** de 10 a 11/09/2020, o total P1 cresceu
aproximadamente 107,824 km², enquanto o P2 ganhou 212,434 km². A
decomposição foi adicionada para **quantificar diretamente** a parte
previamente queimada, em vez de supô-la pela diferença das duas cifras.

Todas as operações de área são feitas em LAEA local/WGS84, como nas Etapas
1–4. Diferenças inferiores a 1 m² são diagnosticadas como potenciais
artefatos geométricos, **não resolução do sensor**.

## Fontes e cruzamentos

| Entrada | Origem | Uso |
|---|---|---|
| P1_componentes_<ID>.geojson | GEE / GlobFire | Patches e área total por data |
| P2_regiao_movel_<ID>.geojson | GEE / GlobFire | Componente principal rastreada |
| metricas_temporais_<ID>.csv | Etapa 2 | Área, dominância, forma, crescimento |
| resumo_transicoes_<ID>.csv | Etapa 3 | Convergências e surgimentos |
| incrementos_temporais_<ID>.csv | Etapa 4 / IGT | Área acrescentada, partes e direções |
| indicadores_regiao_<ID>.csv | Etapa 4 / TR | Deslocamento do centroide, forma, avanços |

**Contrato:** ID idêntico, datas e transições ordenadas, sem chaves
duplicadas; consistência de área P1, P2, Etapas 2–4 em tolerância numérica
máxima de 1e-5 km² para registros arredondados em CSV; fechamento
geométrico da decomposição dentro de 1 m².

## Execução

~~~bash
python -m pip install -r requirements-auditoria.txt
python scripts/integrar_etapa5.py --id 24340828 --saida resultados/etapa5
python -m unittest discover -s tests -v
~~~

O ID é um parâmetro. Para outros IDs é necessário, antes, produzir P1, P2
e as tabelas das Etapas 2–4 do mesmo ID. A extração GEE continua uma etapa
separada; a execução ponta-a-ponta por interface é um backlog futuro.

## Saídas

- série diária com área P1/P2, dominância, número de patches e fase exploratória;
- tabela por transição com decomposição entre área nova e já queimada
  incorporada ao P2, taxas médias por intervalo, convergências, TR e IGT;
- modelo de fases por regressão linear segmentada de área acumulada,
  até três segmentos, ao menos 7 observações/segmento, número selecionado por BIC;
- cinco gráficos temporais, quatro mapas estáticos de datas-chave;
- resumo JSON com hashes e checagens;
- relatório narrativo gerado dos dados, em
  docs/analise_integrada_24340828.md, versionado pelo GitHub Actions.

Os CSVs, JSONs, figuras e relatório serão gerados pela workflow
.github/workflows/etapa5-resultados.yml e versionados em resultados/etapa5.
A geração não modifica os dados de origem P1/P2.

## Interpretação científica: regras obrigatórias

- Contagem de patches vetoriais P1 **não é** segmentação raster 8 vizinhos.
- Convergências do grafo P1 são relacionamentos geométricos, não evidências
  suficientes para afirmar que focos ativos se encontraram naquele momento.
- O incremento da região móvel inclui áreas já queimadas e áreas novas.
- TR e IGT são indicadores diferentes; divergência angular não é erro.
- Fases segmentadas por BIC são descritivas e dependem da granularidade e do
  modelo de regressão; não demonstram regimes físicos de propagação.
- Intervalos maiores que um dia devem ser identificados explicitamente.
- Não atribuir causalidade a rios, barreiras, vento ou cobertura do solo
  sem dados independentes.

## Verificação

Os testes sintéticos incluem expansão simples, incremento em patch secundário,
incorporação de área antiga por ligação de dois patches, perda de área e
segmentação por três tendências. A regressão real compara as geometrias P1/P2
e o resultado anterior de 57 observações, 56 transições e 72 convergências.

**Entrega esperada:** o relatório quantitativo na main com resultados reais
e indicações objetivas sobre quais episódios precisam de interpretação com
o orientador. O dashboard fica para o backlog de generalização.
