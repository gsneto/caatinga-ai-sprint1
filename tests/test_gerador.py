import unittest
from src.gerador_pomar import gerar_pomar, parametros_sensor


class TestGerador(unittest.TestCase):
    def test_semente_e_formato(self):
        a = gerar_pomar(24114036)
        self.assertEqual(len(a), 12)
        self.assertTrue(all(len(linha) == 12 for linha in a))
        self.assertEqual(a[0][0], '.')
        self.assertEqual(a[-1][-1], '.')
        self.assertEqual(a, gerar_pomar(114036))
        self.assertNotEqual(a, gerar_pomar(20231045))
        self.assertEqual(parametros_sensor(24114036), parametros_sensor(114036))

    def test_caminho_garantido_em_outras_sementes(self):
        for s in (0, 1, 24114036, 20231045):
            g = gerar_pomar(s)
            vistos, pendentes = {(0, 0)}, [(0, 0)]
            for i, j in pendentes:
                for a, b in ((i-1,j),(i+1,j),(i,j-1),(i,j+1)):
                    if 0 <= a < 12 and 0 <= b < 12 and g[a][b] != '#' and (a,b) not in vistos:
                        vistos.add((a,b))
                        pendentes.append((a,b))
            self.assertIn((11, 11), vistos)
