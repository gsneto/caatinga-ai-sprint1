import unittest
from src.bayes import calcular


class TestBayes(unittest.TestCase):
    def test_conta_manual(self):
        r=calcular({'prevalencia':.01,'sensibilidade':.99,'taxa_falso_positivo':.05,'talhoes_por_semana':1000})
        self.assertAlmostEqual(r['vpp'],1/6)
        self.assertAlmostEqual(r['falsos_semana'],49.5)
        self.assertAlmostEqual(r['horas_semana'],9.9)
        self.assertGreater(r['vpp_dois_independentes'],r['vpp'])
        self.assertEqual(r['vpp_dois_correlacao_perfeita'],r['vpp'])

    def test_extremos_e_entrada(self):
        p={'prevalencia':0,'sensibilidade':0,'taxa_falso_positivo':0,'talhoes_por_semana':0}
        self.assertIsNone(calcular(p)['vpp'])
        self.assertEqual(calcular({**p,'prevalencia':1,'sensibilidade':1})['vpp'],1)
        for chave,valor in (('prevalencia',-1),('sensibilidade',2),('talhoes_por_semana',1.5)):
            with self.assertRaises(ValueError):
                calcular({**p,chave:valor})
