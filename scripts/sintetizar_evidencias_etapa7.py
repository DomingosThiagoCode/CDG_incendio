#!/usr/bin/env python3
"""Etapa 7: selecao minima de evidencias, sem afirmar validacao externa.

Le exclusivamente resultados ja versionados das etapas 4 e 5.
Produz 2 figuras, 1 quadro de casos e 1 parecer interpretativo.
Nao altera P1/P2 nem infere velocidade da frente de fogo.
"""
from __future__ import annotations

import argparse
import csv
from datetime import date
import json
from pathlib import Path
from statistics import median

BASE = Path(__file__).resolve().parents[1]
LIMIAR_AREA_CASO_DISPERSO_KM2 = 10.0


def ler_csv(caminho: Path) -> list[dict]:
    with caminho.open(encoding="utf-8-sig", newline="") as arquivo:
        return list(csv.DictReader(arquivo))


def numero(linha: dict, campo: str, *, opcional: bool = False) -> float | None:
    valor = linha.get(campo, "")
    if valor is None or valor == "":
        if opcional:
            return None
        raise ValueError(f"Campo ausente: {campo}")
    return float(valor)


def angulo_circular(a: float | None, b: float | None) -> float | None:
    if a is None or b is None:
        return None
    return abs((a - b + 180) % 360 - 180)


def sintetizar(raiz: Path, evento: int) -> tuple[dict, list[dict], list[dict]]:
    t = ler_csv(raiz / f"resultados/etapa5/transicoes_integradas_{evento}.csv")
    s = ler_csv(raiz / f"resultados/etapa4/segmentos_trajetorias_{evento}.csv")
    i = ler_csv(raiz / f"resultados/etapa4/incrementos_temporais_{evento}.csv")
    d = ler_csv(raiz / f"resultados/etapa5/serie_diaria_integrada_{evento}.csv")
    if not t or len(d) != len(t) + 1:
        raise ValueError("Séries diária e de transições incompatíveis")
    if {x["id_incendio"] for x in t + s + i + d} != {str(evento)}:
        raise ValueError("ID de incendio inconsistente")
    pares = [(x["data_anterior"], x["data_atual"]) for x in t]
    if len(set(pares)) != len(pares) or pares != sorted(pares):
        raise ValueError("Transições duplicadas ou fora de ordem")
    mapa_igt = {(x["data_anterior"], x["data_atual"]): x for x in i}
    mapa_seg = {}
    for x in s:
        key = (x["data_anterior"], x["data_atual"], x["ponto"])
        if key in mapa_seg:
            raise ValueError(f"Segmento duplicado: {key}")
        mapa_seg[key] = x
    if set(mapa_igt) != set(pares):
        raise ValueError("IGT e integração possuem transições diferentes")
    if len(mapa_seg) != 5 * len(pares):
        raise ValueError("Esperados cinco segmentos TR por transição")

    linhas = []
    for x in t:
        key = (x["data_anterior"], x["data_atual"])
        r_igt = mapa_igt[key]
        nova = numero(x, "area_nova_evento_km2")
        incorporada = numero(x, "p2_incremento_ja_queimado_km2")
        nova_p2 = numero(x, "p2_incremento_nova_area_evento_km2")
        fora = numero(x, "nova_area_fora_p2_km2")
        acrescimo_p2 = numero(x, "p2_incremento_geometrico_km2")
        if abs(nova - nova_p2 - fora) > 1e-5:
            raise ValueError(f"Não fecha área nova do evento: {key}")
        if abs(acrescimo_p2 - nova_p2 - incorporada) > 1e-5:
            raise ValueError(f"Não fecha decomposição de P2: {key}")
        if abs(acrescimo_p2 - numero(r_igt, "area_nova_km2")) > 1e-5:
            raise ValueError(f"IGT não corresponde ao incremento de P2: {key}")
        extremos = {
            p: numero(mapa_seg[(*key, p)], "delta_eixo_orientado_km")
            for p in ("norte", "sul", "leste", "oeste")
        }
        azi_tr = numero(x, "tr_azimute_centroide_graus", opcional=True)
        azi_igt = numero(x, "igt_azimute_ponderado_graus", opcional=True)
        linhas.append({
            "data_anterior": key[0],
            "data_atual": key[1],
            "dias": int(x["dias_intervalo"]),
            "area_nova_evento_km2": nova,
            "area_nova_p2_km2": nova_p2,
            "area_nova_fora_p2_km2": fora,
            "incorporacao_p2_km2": incorporada,
            "incremento_p2_km2": acrescimo_p2,
            "n_patches_antes": int(x["numero_patches_anterior"]),
            "n_patches_depois": int(x["numero_patches_atual"]),
            "convergencias_grafo": int(x["eventos_convergencia"]),
            "distancia_centroide_km": numero(x, "tr_deslocamento_centroide_km"),
            "azimute_centroide_tr_graus": azi_tr,
            "azimute_igt_graus": azi_igt,
            "concentracao_igt": numero(x, "igt_concentracao_direcional", opcional=True),
            "diferenca_angular_graus": angulo_circular(azi_tr, azi_igt),
            "avanco_norte_km": extremos["norte"],
            "avanco_sul_km": extremos["sul"],
            "avanco_leste_km": extremos["leste"],
            "avanco_oeste_km": extremos["oeste"],
        })
    if any(x["dias"] <= 0 for x in linhas):
        raise ValueError("Intervalo temporal inválido")
    def seleciona(criterio, candidatos: list[dict], chave, reverso=False):
        disponiveis = [x for x in candidatos if x["data_atual"] not in usados]
        if not disponiveis:
            raise ValueError("Sem transições distintas para todos os casos")
        item = sorted(disponiveis, key=chave, reverse=reverso)[0]
        usados.add(item["data_atual"])
        return {"criterio": criterio, **item}

    usados = set()
    casos = [seleciona("maior_incorporacao_p2", linhas,
                       lambda x: (x["incorporacao_p2_km2"], x["data_atual"]),
                       True)]
    casos.append(seleciona("maior_avanco_extremo_norte", linhas,
                           lambda x: (x["avanco_norte_km"], x["data_atual"]),
                           True))
    candidatos = [
        x for x in linhas
        if x["dias"] == 1 and x["area_nova_p2_km2"] >= LIMIAR_AREA_CASO_DISPERSO_KM2
        and x["concentracao_igt"] is not None
    ]
    casos.append(seleciona("expansao_mais_dispersiva_na_amostra", candidatos,
                           lambda x: (x["concentracao_igt"], x["data_atual"])))
    angulos = [x["diferenca_angular_graus"] for x in linhas
               if x["diferenca_angular_graus"] is not None]
    total_nova = sum(x["area_nova_evento_km2"] for x in linhas)
    total_incorporada = sum(x["incorporacao_p2_km2"] for x in linhas)
    total_incremento_p2 = sum(x["incremento_p2_km2"] for x in linhas)
    resumo = {
        "id_incendio": evento,
        "datas": len(d),
        "transicoes": len(linhas),
        "lacunas_maiores_um_dia": sum(x["dias"] > 1 for x in linhas),
        "nova_area_evento_entre_datas_km2": total_nova,
        "nova_area_em_p2_km2": sum(x["area_nova_p2_km2"] for x in linhas),
        "nova_area_fora_p2_km2": sum(x["area_nova_fora_p2_km2"] for x in linhas),
        "incremento_geometrico_p2_km2": total_incremento_p2,
        "incorporacao_area_ja_queimada_p2_km2": total_incorporada,
        "fracao_incorporacao_no_incremento_p2_pct": 100 * total_incorporada / total_incremento_p2,
        "mediana_diferenca_angular_tr_igt_graus": median(angulos) if angulos else None,
        "comparacoes_direcionais": len(angulos),
        "casos": [{k: c[k] for k in (
            "criterio", "data_anterior", "data_atual", "area_nova_evento_km2",
            "incorporacao_p2_km2", "avanco_norte_km", "concentracao_igt",
            "diferenca_angular_graus")} for c in casos],
        "escopo": "comparacao descritiva interna sem validação empírica independente",
        "limite": "concordancia TR x IGT deriva da mesma geometria; não comprova ganho informacional",
    }
    return resumo, linhas, casos


def criar_figuras(linhas: list[dict], casos: list[dict], saida: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    datas = [date.fromisoformat(x["data_atual"]) for x in linhas]
    fig, ax = plt.subplots(figsize=(11, 4.4))
    ax.bar(datas, [x["area_nova_evento_km2"] for x in linhas],
           width=0.85, color="#31688e", label="Área nova no evento (P1)")
    ax.plot(datas, [x["incorporacao_p2_km2"] for x in linhas],
            color="#e47a36", marker=".", linewidth=1.3,
            label="Área previamente queimada incorporada ao P2")
    ax.set_ylabel("Área por transição (km²)")
    ax.set_title("Crescimento novo e reorganização do componente dominante")
    ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d/%m"))
    ax.grid(axis="y", alpha=0.22)
    ax.legend(loc="upper left", fontsize=9)
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(saida / "figura_01_crescimento_incorporacao.png", dpi=180)
    plt.close(fig)

    definido = [x for x in linhas if x["diferenca_angular_graus"] is not None
                and x["concentracao_igt"] is not None]
    fig, ax = plt.subplots(figsize=(9, 4.8))
    ax.scatter([x["concentracao_igt"] for x in definido],
               [x["diferenca_angular_graus"] for x in definido],
               s=[18 + 2 * min(40, x["area_nova_p2_km2"]) for x in definido],
               c="#31688e", alpha=0.65, edgecolors="none")
    for c in casos:
        if c["diferenca_angular_graus"] is not None and c["concentracao_igt"] is not None:
            ax.annotate(c["data_atual"][5:],
                        (c["concentracao_igt"], c["diferenca_angular_graus"]),
                        xytext=(5, 5), textcoords="offset points", fontsize=8)
    ax.set_xlim(0, 1.04)
    ax.set_ylim(bottom=0)
    ax.set_xlabel("Concentração do vetor IGT (0 a 1)")
    ax.set_ylabel("Diferença angular TR × IGT (graus)")
    ax.set_title("Concordância geométrica descritiva, não validação independente")
    ax.grid(alpha=0.22)
    fig.tight_layout()
    fig.savefig(saida / "figura_02_concordancia_direcional.png", dpi=180)
    plt.close(fig)


def relatorio(resumo: dict, casos: list[dict]) -> str:
    t = ["| Caso | Intervalo | Área nova no evento | Incorporada ao P2 | Avanço norte | Concentração IGT |",
         "|---|---|---:|---:|---:|---:|"]
    for c in casos:
        t.append(f"| {c['criterio']} | {c['data_anterior']} a {c['data_atual']} | "
                 f"{c['area_nova_evento_km2']:.2f} km² | "
                 f"{c['incorporacao_p2_km2']:.2f} km² | "
                 f"{c['avanco_norte_km']:.2f} km | "
                 f"{c['concentracao_igt']:.3f} |")
    return f"""# Etapa 7: síntese mínima para a pergunta científica

**Estudo de caso:** GlobFire {resumo['id_incendio']}; **escopo:** descrição geométrica interna.
**Estado:** triagem de evidências; não validação externa e não comprovação de propagação física.

## Pergunta

As trajetórias representativas (TR) acrescentam descrição útil à evolução
da área queimada acumulada, além da área, dos componentes e do IGT?

## Três casos sentinela selecionados por regras explícitas

- Maior incorporação ao P2 de área já queimada no evento.
- Maior avanço positivo do extremo norte (TR), excluído caso anterior.
- Menor concentração do IGT entre transições diárias com >=10 km² de área
  nova em P2, excluídos casos anteriores. O limiar é operacional/exploratório.

{chr(10).join(t)}

## Quadro de informação incremental, sem escore inventado

| Conjunto mínimo | Responde | Não responde sozinho |
|---|---|---|
| B0: área total + incremento | Quando e quanto a área mapeada cresceu | Conectividade, direção, incorporação ao P2 |
| B1: B0 + número de componentes/dominância | Fragmentação e organização espacial resumida | Localização e geometria da área acrescida |
| B2: B1 + TR (centroide/extremos) | Reequilíbrio e limites cardeais do envelope | Distribuição das novas áreas e fusões vs. queima nova |
| B3: B2 + IGT decomposto | Onde se acresceu geometria ao P2 e quanto já estava queimado | Propagação real, causalidade ou validação independente |

## Quantificação observada

- {resumo['datas']} observações e {resumo['transicoes']} transições, com {resumo['lacunas_maiores_um_dia']} lacunas maiores que um dia.
- Área nova mapeada no evento entre observações: {resumo['nova_area_evento_entre_datas_km2']:.3f} km².
- Incremento geométrico acumulado em P2: {resumo['incremento_geometrico_p2_km2']:.3f} km².
- Parte de P2 que já estava queimada no evento: {resumo['incorporacao_area_ja_queimada_p2_km2']:.3f} km²
  ({resumo['fracao_incorporacao_no_incremento_p2_pct']:.1f}% do incremento P2).
- Diferença angular mediana TR × IGT: {resumo['mediana_diferenca_angular_tr_igt_graus']:.2f}°,
  em {resumo['comparacoes_direcionais']} transições definidas.

**Atenção metodológica:** ambos os azimutes derivam da mesma geometria
acumulada, e o vetor do centroide relaciona-se algebricamente ao centroide
da área acrescentada quando não há perda. Não tratar concordância angular
como validação independente ou como desempenho preditivo.

## Material principal vs. suplemento

**Corpo do artigo/apresentação:**
1. Figura 1: área realmente nova no evento versus incorporação de área já
   queimada ao P2, sem somar as duas como se fossem queima nova.
2. Figura 2: diferença angular TR × IGT versus concentração direcional,
   apenas para expor concordâncias e limitações.
3. Quadro de três intervalos sentinela (acima).
4. Um mapa QGIS da transição crítica 10/09 a 11/09, usando a camada
   já existente em resultados/etapa6/revisao_qgis_{resumo['id_incendio']}.geojson.

**Suplemento técnico:** rosáceas individuais, 5 linhas de trajetórias,
séries exaustivas de indicadores e todos os cenários de sensibilidade.
As figuras da etapa 7 são uma proposta de seleção, não resultado editorial
final aprovado pelo orientador.

## Limitações e próximo teste independente

Esta etapa não quantifica um "ganho de conhecimento" causal ou estatístico:
define quais perguntas cada conjunto de indicadores responde. Falta um
referencial externo (Sentinel-2 ou Landsat 8 de 2020, com controle temporal
e de qualidade) e casos sem convergência selecionados antes da inspeção.
Repetir o protocolo em outro evento antes de generalizar os achados.
"""


def executar(raiz: Path, evento: int, saida: Path, *, sem_figuras=False) -> dict:
    resumo, linhas, casos = sintetizar(raiz, evento)
    saida.mkdir(parents=True, exist_ok=True)
    (saida / f"resumo_minimo_{evento}.json").write_text(
        json.dumps(resumo, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (saida / f"relatorio_sintese_{evento}.md").write_text(
        relatorio(resumo, casos), encoding="utf-8"
    )
    with (saida / f"casos_sentincela_{evento}.csv").open(
        "w", encoding="utf-8", newline=""
    ) as arquivo:
        campos = list(casos[0])
        writer = csv.DictWriter(arquivo, fieldnames=campos)
        writer.writeheader()
        writer.writerows(casos)
    if not sem_figuras:
        criar_figuras(linhas, casos, saida)
    return resumo


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--id", type=int, default=24340828)
    parser.add_argument("--raiz", type=Path, default=BASE)
    parser.add_argument("--saida", type=Path, default=BASE / "resultados/etapa7")
    parser.add_argument("--sem-figuras", action="store_true")
    args = parser.parse_args()
    print(json.dumps(
        executar(args.raiz, args.id, args.saida, sem_figuras=args.sem_figuras),
        ensure_ascii=False, indent=2
    ))


if __name__ == "__main__":
    main()
