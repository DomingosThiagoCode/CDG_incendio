#!/usr/bin/env python3
"""Etapa 8: manifesto pré-registrado de cenas, sentinelas e controles.

Não baixa imagens nem declara validação externa. As janelas são candidatos
de observação, NÃO janelas de datas físicas de propagação.
"""
from __future__ import annotations

import argparse
import csv
from datetime import date, timedelta
from hashlib import sha256
import json
from pathlib import Path
import sys

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "scripts"))
from sintetizar_evidencias_etapa7 import sintetizar

COLUNAS = (
    "id_incendio", "tipo", "criterio", "codigo", "data_anterior", "data_atual",
    "janela_pre_inicio", "janela_pre_fim_exclusivo",
    "janela_pos_inicio", "janela_pos_fim_exclusivo",
    "distancia_minima_casos_dias", "convergencias_grafo",
    "area_nova_evento_km2", "incorporacao_p2_km2",
    "sensor_prioritario", "sensor_alternativo", "status"
)


def distancia(a: str, b: str) -> int:
    return abs((date.fromisoformat(a) - date.fromisoformat(b)).days)


def selecionar_controles(linhas: list[dict], alvos: list[dict],
                        evento: int, n: int = 2, espacamento: int = 4) -> list[dict]:
    """Sorteio determinístico entre intervalos sem convergência, sem lacuna.

    Critério fixado antes de consultar Sentinel/Landsat. Não pareia sazonalidade
    ou paisagem e não substitui amostragem estatística representativa.
    """
    dias_alvo = [x["data_atual"] for x in alvos]
    disponiveis = [
        x for x in linhas if x["dias"] == 1
        and x["convergencias_grafo"] == 0
        and x["area_nova_evento_km2"] > 0
        and all(distancia(x["data_atual"], d) >= espacamento for d in dias_alvo)
    ]
    disponiveis.sort(key=lambda x: (
        sha256(f"{evento}|{x['data_atual']}".encode()).hexdigest(),
        x["data_atual"]
    ))
    escolhidos = []
    for x in disponiveis:
        if all(distancia(x["data_atual"], y["data_atual"]) >= espacamento for y in escolhidos):
            escolhidos.append(x)
        if len(escolhidos) == n:
            break
    if len(escolhidos) != n:
        raise ValueError(f"Sem {n} intervalos-controle válidos")
    return escolhidos


def manifesto(raiz: Path, evento: int = 24340828, *,
              controles: int = 2, semi_janela: int = 12) -> tuple[list[dict], dict]:
    if semi_janela < 1:
        raise ValueError("Semi-janela em dias deve ser positiva")
    _, transicoes, casos = sintetizar(raiz, evento)
    selecao = []
    for c in casos:
        selecao.append(("sentinela", c["criterio"], c))
    for idx, c in enumerate(selecionar_controles(transicoes, casos, evento, n=controles), 1):
        selecao.append(("controle", f"controle_sem_convergencia_{idx}", c))
    linhas = []
    for tipo, criterio, c in selecao:
        a = date.fromisoformat(c["data_anterior"])
        b = date.fromisoformat(c["data_atual"])
        if b <= a:
            raise ValueError("Datas fora de ordem")
        code = criterio.replace(" ", "_")
        linhas.append({
            "id_incendio": evento,
            "tipo": tipo,
            "criterio": criterio,
            "codigo": code,
            "data_anterior": a.isoformat(),
            "data_atual": b.isoformat(),
            "janela_pre_inicio": (a - timedelta(days=semi_janela)).isoformat(),
            "janela_pre_fim_exclusivo": (a + timedelta(days=1)).isoformat(),
            "janela_pos_inicio": b.isoformat(),
            "janela_pos_fim_exclusivo": (b + timedelta(days=semi_janela + 1)).isoformat(),
            "distancia_minima_casos_dias": min(distancia(str(b), x["data_atual"]) for x in casos)
                 if tipo == "controle" else 0,
            "convergencias_grafo": c["convergencias_grafo"],
            "area_nova_evento_km2": round(c["area_nova_evento_km2"], 9),
            "incorporacao_p2_km2": round(c["incorporacao_p2_km2"], 9),
            "sensor_prioritario": "COPERNICUS/S2_SR_HARMONIZED",
            "sensor_alternativo": "LANDSAT/LC08/C02/T1_L2",
            "status": "imagem_pendente"
        })
    datas = [x["data_atual"] for x in linhas]
    if len(set(datas)) != len(datas):
        raise ValueError("Duplicação de transições")
    meta = {
        "id_incendio": evento,
        "sentinelas": len(casos),
        "controles": controles,
        "total": len(linhas),
        "semente": f"sha256({evento}|YYYY-MM-DD)",
        "semi_janela_dias": semi_janela,
        "criterio_controle": "1 dia, convergencias=0, área nova>0, >=4 dias dos sentinelas e entre controles",
        "cenas_confirmadas": 0,
        "validacao_externa_concluida": False,
        "advertencia": "janela de aquisição não equivale à data real da queima; dNBR não é verdade-terreno"
    }
    return linhas, meta


def executar(raiz: Path, evento: int, pasta: Path, controles: int = 2,
             semi_janela: int = 12) -> dict:
    linhas, meta = manifesto(raiz, evento, controles=controles, semi_janela=semi_janela)
    pasta.mkdir(parents=True, exist_ok=True)
    with (pasta / f"manifesto_cenas_{evento}.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLUNAS)
        w.writeheader()
        w.writerows(linhas)
    (pasta / f"resumo_triagem_{evento}.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return meta


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--id", type=int, default=24340828)
    p.add_argument("--raiz", type=Path, default=RAIZ)
    p.add_argument("--saida", type=Path, default=RAIZ / "resultados/etapa8")
    p.add_argument("--controles", type=int, default=2)
    p.add_argument("--semi-janela-dias", type=int, default=12)
    args = p.parse_args()
    print(json.dumps(executar(args.raiz, args.id, args.saida,
                              args.controles, args.semi_janela_dias),
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
