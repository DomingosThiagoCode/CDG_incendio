# Comparação: geometria original ou regularização?

**Resultado:** para os GeoJSON P1/P2 do evento `24340828`, recomenda-se
**preservar o original e projetar primeiro para uma projeção local apropriada**.
Na projeção LAEA local utilizada no experimento, todas as geometrias passaram
nos testes topológicos sem reparação prévia. A eventual regularização deve
ser **condicional, após a reprojeção**, e nunca sobrescrever os GeoJSON
originais. A recomendação vale para este evento e deve ser testada em outros.

## Protocolo reproduzível

- Entradas: P1 (978 feições) e P2 (57 feições) versionados no repositório.
- Métodos comparados: original projetado, `make_valid()` em longitude/latitude
  antes de projetar, `buffer(0)` antes de projetar, e `make_valid()` após a
  projeção local. Para as duas variantes reparadas antes, foi necessário
  aplicar um segundo `make_valid()` **após a projeção** em 51 registros de
  cada produto, a fim de obter geometria válida no CRS de análise.
- Sistema métrico: LAEA local centrado no evento, sobre WGS84. Para estudar a
  sensibilidade da validade à projeção, também foram avaliados UTM 21S
  (`EPSG:32721`) e projeção equivalente global (`EPSG:6933`).
- Métricas: validade OGC, área, perímetro, índice de forma
  `P/(2√(πA))`, centróide, número de partes e diferença em relação à área
  declarada pelo GEE, descontando o fator sistemático de modelo de área
  estimado nas feições válidas (somente para comparação interna).
- Nenhuma entrada foi modificada. O código e os números detalhados estão em
  `scripts/comparar_regularizacao.py` e
  `resultados/experimento_regularizacao_24340828.json`.

```bash
python -m pip install -r requirements-auditoria.txt
python scripts/comparar_regularizacao.py \
  dados/estudo_caso_24340828/P1_componentes_24340828.geojson \
  dados/estudo_caso_24340828/P2_regiao_movel_24340828.geojson \
  --saida-json resultados/experimento_regularizacao_24340828.json
python -m unittest discover -s tests -v
```

## Resultado 1 — validade depende do sistema e da ordem

| Projeção/interpretação do original | P1 inválidos | P2 inválidos |
| --- | ---: | ---: |
| Coordenadas geográficas interpretadas no plano | 172 | 55 |
| LAEA local (reprojeção antes de conferir validade) | **0** | **0** |
| UTM 21S (EPSG:32721) | **0** | **0** |
| Equivalente global (EPSG:6933) | 172 | 55 |

Isto demonstra **sensibilidade da topologia calculada à projeção de
vértices**, não uma garantia de que o traçado original seja fisicamente
correto ou que toda reprojeção resolva a questão. Coordenadas geográficas
devem ser projetadas antes de medidas planares; a escolha da projeção deve
ser documentada.

## Resultado 2 — efeito dos tratamentos nas partes poligonais

| Ordem de processamento | Partes P1 no conjunto de 57 datas | Partes P2 |
| --- | ---: | ---: |
| Projetar original diretamente para LAEA | **978** | **57** |
| `make_valid()` em lon/lat, projetar e reparar novamente se necessário | **1.333** | **412** |
| `buffer(0)` em lon/lat, projetar e reparar novamente se necessário | **978** | **57** |
| Projetar e só depois usar `make_valid()` | **978** | **57** |

O fluxo com `make_valid()` aplicado **antes e, quando necessário, depois**
da projeção representou 51 feições do P1 e 51 do P2 como multipolígonos,
resultando em 355 partes adicionais em cada produto. Essas partes podem
refletir contatos pontuais ou artefatos
de representação, e não devem ser automaticamente reclassificadas como
patches independentes. É indispensável fixar o critério de conectividade
para qualquer análise que conte componentes.

## Resultado 3 — área e forma praticamente não mudaram

- Entre as 172 feições P1 inválidas nas coordenadas geográficas, a maior
  variação absoluta de área com `make_valid()` antes de projetar foi de
  apenas **0,000196%** em relação ao original projetado.
- No P2, a maior variação equivalente foi de **0,000125%**.
- A variação de perímetro ficou abaixo da precisão numérica exibida nas
  estatísticas; o índice de forma também mudou desprezivelmente ao manter
  a feição inteira (sem separar suas partes).
- No P2, o deslocamento máximo do centróide causado por esse tratamento
  foi de **0,0049 m**.
- Após normalizar a diferença sistemática entre métodos de cálculo de área,
  todas as feições permaneceram com desvio relativo inferior a 1% frente
  ao atributo de área do GEE.
- As verificações de relação P1–P2, sobreposição entre componentes e
  candidatos a fusão feitas diretamente no original projetado em LAEA
  produziram os mesmos valores centrais da auditoria anterior:
  **57/57 correspondências**, **0 pares com sobreposição positiva de área**
  e **72 candidatos de fusão**. Os minúsculos resíduos temporais anteriores
  não reapareceram no cálculo direto sobre os polígonos projetados.

Não há ganho mensurável para **área, perímetro ou shape index por feição**
que justifique regularizar todos os registros antes da projeção. A alteração
importante é **topológica** (quantidade de partes), não métrica.

## Por que não adotar `buffer(0)` como reparo universal?

Embora as diferenças de área sejam desprezíveis no caso estudado,
`buffer(0)` não garante preservação de todas as partes em outros dados.
No teste sintético de um polígono tipo *bow-tie*, `make_valid()` preservou
duas partes, com área total 2, enquanto `buffer(0)` manteve apenas uma,
com área 1. Essa perda de **50%** torna o `buffer(0)` inadequado como
regra automática indiscriminada.

## Decisão recomendada para o pipeline

1. Conservar o GeoJSON original como fonte imutável e os IDs/feições que
   saíram do GEE.
2. Reprojetar em cópia de trabalho para CRS adequado ao evento (neste caso,
   LAEA local ou alternativa projetada justificada), sem explodir partes.
3. Verificar `is_valid` **após** a reprojeção e registrar contagens.
4. Apenas nos casos que continuarem inválidos, aplicar `make_valid()` em
   uma cópia e registrar eventuais mudanças de área/perímetro e partes.
5. Não usar automaticamente a quantidade de polígonos resultantes do
   reparo como novo número de patches. A identidade espacial e os eventos
   de fusão requerem critério de conectividade específico.
6. Repetir esse experimento para qualquer novo ID GlobFire antes de
   generalizar a recomendação.

**Limite científico:** a validade OGC pós-projeção e a estabilidade das
métricas são condições necessárias para operar no GIS, mas não provam
exatidão do contorno queimado, fidelidade aos pixels originais ou
correção dos métodos de regiões móveis.
