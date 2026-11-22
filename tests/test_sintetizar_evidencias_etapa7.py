"""Etapa 7: analise real e casos sintéticos mínimos."""
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from sintetizar_evidencias_etapa7 import angulo_circular, sintetizar, executar


class TestesUnitarios(unittest.TestCase):
    def test_angulo_circular(self):
        self.assertEqual(angulo_circular(350, 10), 20)
        self.assertEqual(angulo_circular(10, 350), 20)
        self.assertEqual(angulo_circular(20, 200), 180)
        self.assertIsNone(angulo_circular(None, 10))


class TestesDadosVersionados(unittest.TestCase):
    def test_metricas_e_casos_sentinela(self):
        resumo, linhas, casos = sintetizar(ROOT, 24340828)
        self.assertEqual((resumo["datas"], resumo["transicoes"]), (57, 56))
        self.assertEqual(resumo["lacunas_maiores_um_dia"], 3)
        self.assertEqual(len(linhas), 56)
        self.assertEqual(len(casos), 3)
        self.assertEqual(
            [c["data_atual"] for c in casos],
            ["2020-09-11", "2020-09-01", "2020-08-12"]
        )
        self.assertAlmostEqual(resumo["incorporacao_area_ja_queimada_p2_km2"],
                               195.958449957, places=4)
        self.assertAlmostEqual(resumo["incremento_geometrico_p2_km2"],
                               949.843488705, places=4)
        self.assertAlmostEqual(resumo["fracao_incorporacao_no_incremento_p2_pct"],
                               20.630604, places=3)
        self.assertEqual(resumo["comparacoes_direcionais"], 55)
        self.assertAlmostEqual(resumo["mediana_diferenca_angular_tr_igt_graus"],
                               1.142218646, places=4)

    def test_produtos_sem_perturbar_entradas(self):
        origem = ROOT / "resultados/etapa5/transicoes_integradas_24340828.csv"
        antes = origem.read_bytes()
        with TemporaryDirectory() as pasta:
            r = executar(ROOT, 24340828, Path(pasta), sem_figuras=True)
            self.assertEqual(r["transicoes"], 56)
            resumo = json.loads((Path(pasta) / "resumo_minimo_24340828.json").read_text())
            self.assertEqual(resumo["datas"], 57)
            relatorio = (Path(pasta) / "relatorio_sintese_24340828.md").read_text()
            self.assertIn("Não tratar concordância angular", relatorio)
            self.assertTrue((Path(pasta) / "casos_sentinela_24340828.csv").exists())
        self.assertEqual(antes, origem.read_bytes())


if __name__ == "__main__":
    unittest.main()
