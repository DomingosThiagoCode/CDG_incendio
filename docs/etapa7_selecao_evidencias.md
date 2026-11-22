# Etapa 7 — Seleção das evidências essenciais

## Por que reduzir os gráficos?

A observação do orientador é pertinente: produzir um gráfico para cada métrica
não demonstra que o indicador acrescenta conhecimento. O projeto deve distinguir
(a) pergunta científica, (b) informação necessária para responder, (c) figura
essencial para comunicá-la. Todas as métricas continuam disponíveis para
auditabilidade, mas não entram automaticamente no artigo ou apresentação.

**Pergunta-alvo:** em quais condições as trajetórias representativas (TR)
descrevem aspectos úteis da evolução geométrica de área queimada acumulada e
o que os incrementos geométricos temporais (IGT) acrescentam a essa leitura?

## Seleção editorial provisória

| Peça | Entra no núcleo? | Razão |
|---|---|---|
| Gráfico de área nova do evento versus incorporação ao P2 | Sim | Mostra por que crescimento de P2 não equivale a nova queima |
| Quadro de 3 intervalos sentinela | Sim | Mostra três mecanismos diferentes em poucos números |
| Um mapa com P2 anterior/atual, área nova e área incorporada (10-11/09) | Sim | Torna o mecanismo espacial verificável |
| Concordância angular × concentração IGT | Apenas se houver espaço | Serve para discutir redundância e ambiguidade, não validação independente |
| Rosáceas de cada trajetória | Suplemento | Muitas figuras com forte sobreposição informacional |
| Cinco trajetórias completas separadas | Suplemento | Mapas de detalhe são mais úteis para o argumento central |
| Todas as métricas de forma e séries por patch | Suplemento | Não respondem diretamente à pergunta central |
| Todas as fases BIC e sensibilidades | Suplemento/metodologia | Testes exploratórios necessários para cautela, não narrativas causais |

**Limite visual:** um gráfico principal, um mapa e um quadro. Um segundo
gráfico (concordância angular) é opcional para demonstrar a limitação das TR.

## Contrastes prioritários já identificados nos resultados

1. **10 para 11/09/2020:** P2 adicionou 212,434 km² à sua geometria,
   dos quais 105,466 km² já constavam como queimados no evento. A área
   realmente nova do evento nesse intervalo foi 107,824 km².
   Resultado essencial para não confundir incorporação com expansão física.
2. **31/08 para 01/09/2020:** o extremo norte de P2 avançou cerca de
   4,150 km. Um sinal de variação do envelope que a área total isolada
   não localiza, embora o extremo seja definido diretamente pela geometria.
3. **11 para 12/08/2020:** área nova de P2 de cerca de 27,380 km², mas
   concentração direcional IGT baixa (~0,155). A síntese por um único
   azimute pode ocultar expansão distribuída em múltiplas direções.

Os casos são selecionados por regras registradas no script (maior
incorporação, maior avanço norte e menor concentração em transições
diárias com pelo menos 10 km² novos em P2). Isso é **amostragem
direcionada para contraste**, não amostra estatística representativa.

## Qual contribuição pode ser defendida?

- **Só área (B0):** informa quanto e quando a área queimada cresceu.
- **Área + componentes (B1):** revela concentração/fragmentação, mas não
  identifica por si só onde ocorreram as adições.
- **B1 + trajetórias (B2):** resume mudanças de equilíbrio e limites
  cardeais, com possibilidade de saltos de extremos e redundância.
- **B2 + IGT decomposto (B3):** distingue área acrescentada à geometria de
  P2 da área nova no evento e de regiões anteriormente queimadas.

A concordância do deslocamento do centroide TR com a direção ponderada
de IGT não é validação independente. Ambas são funções dos mesmos
polígonos; em expansão acumulativa, a variação do centroide tem direção
matematicamente vinculada à distribuição da área acrescida.

O experimento **não** atribui percentuais fictícios de ganho científico
nem trata fusões do grafo como encontros reais de chamas. Uma prova de
validade física depende da confrontação posterior com imagens independentes.

## Como gerar o pacote mínimo

Na raiz do repositório:

    python -m pip install -r requirements-auditoria.txt
    python scripts/sintetizar_evidencias_etapa7.py --id 24340828 --saida resultados/etapa7

O script lê tabelas já existentes, recusa decomposições incoerentes,
escolhe três casos por critérios explícitos e produz:

- resumo_minimo_24340828.json
- casos_sentinela_24340828.csv
- relatorio_sintese_24340828.md
- figura_01_crescimento_incorporacao.png
- figura_02_concordancia_direcional.png

O segundo gráfico é **opcional na publicação**; gerá-lo não obriga
utilizá-lo. Para o mapa, usar a camada de revisão da Etapa 6.
Não há alteração nos GeoJSON originais, nem consulta a dados externos.

**Próxima necessidade científica:** testar estes contrastes sobre cenas
independentes e intervalos-controle. A Etapa 7 organiza as evidências do
estudo de caso e delimita o que ainda não foi validado.
