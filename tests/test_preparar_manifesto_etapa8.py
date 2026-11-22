"""Etapa 8: preregistro deterministico de sentinelas e controles."""
from __future__ import annotations
import csv
from datetime import date
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "scripts"))
from preparar_manifesto_etapa8 import (
    distancia, selecionar_controles, manifesto, executar)


class TesteSintetico(unittest.TestCase):
    def test_distancia_calendario(self):
        self.assertEqual(distancia("2020-09-22", "2020-09-18"), 4)
        self.assertEqual(distancia("2020-09-22", "2020-09-22"), 0)

    def test_amostra_exclui_proximidades(self):
        alvos = [{"data_atual": "2020-09-11"}]
        linhas = [
            {"data_atual": "2020-09-12", "dias": 1, "convergencias_grafo": 0,
             "area_nova_evento_km2": 1},
            {"data_atual": "2020-09-20", "dias": 1, "convergencias_grafo": 0,
             "area_nova_evento_km2": 1},
            {"data_atual": "2020-09-30", "dias": 1, "convergencias_grafo": 1,
             "area_nova_evento_km2": 1},
            {"data_atual": "2020-10-05", "dias": 2, "convergencias_grafo": 0,
             "area_nova_evento_km2": 1},
        ]
        cs = selecionar_controles(linhas, alvos, 1, n=1)
        self.assertEqual(cs[0]["data_atual"], "2020-09-20")


class TestesRegressaoReal(unittest.TestCase):
    def test_manifesto_pre_registrado(self):
        rows, meta = manifesto(RAIZ, 24340828)
        self.assertEqual(len(rows), 5)
        self.assertEqual([x["data_atual"] for x in rows[:3]],
                         ["2020-09-11", "2020-09-01", "2020-08-12"])
        self.assertEqual([x["data_atual"] for x in rows[3:]],
                         ["2020-09-22", "2020-10-02"])
        self.assertEqual([x["tipo"] for x in rows].count("controle"), 2)
        for r in rows:
            self.assertLess(date.fromisoformat(r["janela_pre_inicio"]),
                            date.fromisoformat(r["janela_pre_fim_exclusivo"]))
            self.assertLess(date.fromisoformat(r["janela_pos_inicio"]),
                            date.fromisoformat(r["janela_pos_fim_exclusivo"]))
            self.assertEqual(r["status"], "imagem_pendente")
            self.assertTrue(
                r["tipo"] != "controle" or r["distancia_minima_casos_dias"] >= 4)
        self.assertFalse(meta["validacao_externa_concluida"])
        self.assertEqual(meta["cenas_confirmadas"], 0)

    def test_exporta_sem_mudar_entradas(self):
        fonte = RAIZ / "resultados/etapa5/transicoes_integradas_24340828.csv"
        antes = fonte.read_bytes()
        with TemporaryDirectory() as pasta:
            s = executar(RAIZ, 24340828, Path(pasta))
            self.assertEqual(s["total"], 5)
            with (Path(pasta) / "manifesto_cenas_24340828.csv").open(
                    encoding="utf-8", newline="") as f:
                rows = list(csv.DictReader(f))
            self.assertEqual(len(rows), 5)
            self.assertTrue(
                (Path(pasta) / "resumo_triagem_24340828.json").exists())
        self.assertEqual(antes, fonte.read_bytes())


if __name__ == "__main__":
    unittest.main()
