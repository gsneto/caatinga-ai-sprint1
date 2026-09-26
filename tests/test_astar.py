import itertools
import unittest
from src.buscas import astar, ucs, manhattan
from src.gerador_pomar import gerar_pomar
from src.experimentos import bonus_dfs
from test_buscas import oraculo


class TestAstar(unittest.TestCase):
    def test_otimalidade_e_h_zero(self):
        for seed in (0,1,24114036,20231045):
            g=gerar_pomar(seed)
            r=ucs(g)
            zero=astar(g,lambda a,b:0)
            self.assertEqual((r.custo,r.passos,r.nos_expandidos,r.fronteira_max),
                             (zero.custo,zero.passos,zero.nos_expandidos,zero.fronteira_max))
            self.assertEqual(astar(g,manhattan).custo,r.custo)

    def test_admissivel_inconsistente_reabre(self):
        g=[list('.~.~'),list('...~'),list('....'),list('~...')]
        valores=[[6,0,0,0],[5,4,0,2],[0,0,0,0],[0,2,1,0]]
        for p in itertools.product(range(4),repeat=2):
            self.assertLessEqual(valores[p[0]][p[1]],oraculo(g,p))
        r=astar(g,lambda p,_:valores[p[0]][p[1]])
        self.assertEqual(r.custo,6)
        self.assertEqual(r.reaberturas,2)

    def test_bonus(self):
        d=bonus_dfs()
        self.assertLessEqual(len(d['grade']),8)
        self.assertGreater(d['dfs']['custo'],2*d['ucs']['custo'])

    def test_sem_caminho(self):
        self.assertIsNone(astar([list('.#'),list('#.')],manhattan).custo)
