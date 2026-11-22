# Etapa 8 — Triagem de imagens independentes para validar o estudo de caso

**Estado:** kit implementado; manifesto pré-registrado; **nenhuma cena Sentinel-2/Landsat processada ou interpretada até agora**. Não afirmar validação externa concluída.

## Objetivo

Confrontar a interpretação geométrica da área queimada acumulada no evento GlobFire 24340828 com observações de sensores diferentes. Distinguir aumento de P2, incorporação de manchas anteriormente queimadas e queima nova no evento.

A etapa não exige mais gráficos no artigo: preservar o núcleo da Etapa 7 (**1 gráfico principal, 1 mapa e 1 quadro comparativo**). O inventário de imagens é evidência rastreável e pertence ao material técnico.

## Amostra registrada antes de olhar imagens

Três transições sentinela da Etapa 7:

1. **10→11/09/2020:** maior incorporação ao P2 de área já queimada;
2. **31/08→01/09/2020:** maior avanço do extremo norte fora do caso anterior;
3. **11→12/08/2020:** menor concentração IGT entre transições diárias com pelo menos 10 km² de área nova em P2.

Dois controles exploratórios escolhidos entre transições de 1 dia, sem convergência no grafo e com aumento de área mapeada, mantendo ao menos 4 dias de distância dos sentinelas e entre controles. Os candidatos são ordenados pelo SHA256 da combinação ID/data, independentemente das imagens. No evento 24340828:

- **21→22/09/2020**;
- **01→02/10/2020**.

Os controles não são pareados por cobertura vegetal ou taxa de crescimento. Amostra intencional mais dois controles não representam estatisticamente todos os incêndios.

## Execução

**Parte A, sem conta do GEE:** a partir da raiz do repositório:

    python scripts/preparar_manifesto_etapa8.py --id 24340828 --saida resultados/etapa8
    python -m unittest discover -s tests -v

Os arquivos manifesto_cenas_24340828.csv e resumo_triagem_24340828.json registram datas, janelas, critérios e status pendente. As janelas cobrem 12 dias antes do início e 12 dias após o fim de cada transição, com fim exclusivo explicitado.

**Parte B, no Code Editor do Google Earth Engine:**

1. Abrir https://code.earthengine.google.com/ e copiar o código do arquivo gee/etapa8_triagem_satelites.js.
2. Alterar CASO_ATIVO entre os cinco casos do arquivo e testar SENSOR='S2' e SENSOR='L8' separadamente.
3. Examinar IDs, datas e fração da AOI observável em cada cena pré/pós. Verificar também a interseção observável do par.
4. Os mapas NBR e dNBR são **diagnósticos espectrais**, não máscaras de referência validadas. A cena selecionada automaticamente tem a maior fração de pixels válidos na área, mas não é necessariamente a melhor cena no tempo.
5. Em Tasks, executar a exportação CSV de metadados, quando desejada, e preservar o resultado. Nenhuma tarefa é executada em nome do pesquisador pelo repositório.
6. Se faltar imagem, houver nuvem no local-chave ou aquisição temporal excessivamente distante, registrar resultado como **indeterminado**, não como concordância.

Para 10→11/09, confrontar no QGIS com resultados/etapa6/revisao_qgis_24340828.geojson. Essa camada de P2 anterior/atual, área incorporada e área nova é **derivada do GlobFire**, não uma fonte independente.

## Ficha de avaliação que deve ser preenchida na revisão

Registrar: caso, grupo, ID, datas GlobFire, sensor, ID de cada imagem, datas/horas, órbita/tile, CRS, fração válida pré, pós e comum, nuvens/sombras/água, evidência de cicatriz, relação com incremento e incorporação, classe **compatível/incompatível/indeterminada**, justificativa, revisor e data.

Não aceitar dNBR limiarizado como "verdade-terreno" sem referência externa confiável, revisão visual e máscara de observabilidade. Quando for produzida máscara independente, calcular interseção e união, IoU, comissão e omissão com suporte espacial harmonizado e incerteza temporal declarada.

## Limites científicos

- Os recortes derivam do envelope dos GeoJSON do evento. Não definem um limite ecológico.
- A máscara Sentinel-2 usa SCL, incluindo a classe 2 (pixels escuros) e a classe 7 (não classificada), que requer revisão visual; classes 0, 1, 3 e 8 a 11 são excluídas.
- O Landsat 8 usa QA_PIXEL da Collection 2 e escala/offset oficiais. Landsat 9 **não** é adequado a 2020.
- Fração válida calculada com amostragem a 120 m é apenas triagem, não resolução da análise de queimadas nem garantia de cobertura do local específico.
- Pares separados por diversos dias podem conter queimas intermediárias; não atribuir a observação à data física do contato de patches.
- MODIS MCD64A1 tem resolução nominal de 500 m e informação de incerteza temporal; comparar contornos em escalas diferentes requer tolerância e avaliação da natureza do produto.
- Métricas de similaridade e evidências de causalidade ainda não foram calculadas.

## Referências oficiais

- https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_S2_SR_HARMONIZED
- https://developers.google.com/earth-engine/datasets/catalog/LANDSAT_LC08_C02_T1_L2
- https://developers.google.com/earth-engine/datasets/catalog/MODIS_061_MCD64A1

**Marco seguinte:** obter metadados e visualizar cenas, registrar o parecer de cada intervalo e só então executar comparação quantitativa com máscaras de referência verificadas.
