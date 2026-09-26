import unittest
from src import buscas as b
from src.gerador_pomar import gerar_pomar


def oraculo(g, inicio=(0, 0), objetivo=None):
    """Bellman-Ford independente: sem heap, vizinhos ou pais da produção."""
    objetivo = objetivo or (len(g)-1, len(g[0])-1)
    d = {(i,j): float('inf') for i,row in enumerate(g) for j,c in enumerate(row) if c != '#'}
    d[inicio] = 0
    for _ in range(len(d)-1):
        mudou = False
        for (i,j), custo in list(d.items()):
            for q in ((i-1,j),(i+1,j),(i,j-1),(i,j+1)):
                if q in d:
                    novo = custo + (1 if g[q[0]][q[1]] == '.' else 4)
                    if novo < d[q]:
                        d[q] = novo
                        mudou = True
        if not mudou:
            break
    return d.get(objetivo, float('inf'))


class TestBuscas(unittest.TestCase):
    def test_bordas_e_rota(self):
        for fn in (b.bfs, b.dfs, b.ucs):
            r = fn([['.']])
            self.assertEqual((r.custo,r.passos,r.nos_expandidos,r.fronteira_max), (0,0,0,1))
            self.assertIsNone(fn([list('.#'),list('#.')]).custo)
            g = gerar_pomar(24114036)
            r = fn(g)
            self.assertEqual(r.rota[0], (0,0))
            self.assertEqual(r.rota[-1], (11,11))
            self.assertEqual(r.passos,len(r.rota)-1)
            self.assertEqual(r.custo,sum({'.':1,'~':4}[g[i][j]] for i,j in r.rota[1:]))
            self.assertTrue(all(abs(a[0]-c[0])+abs(a[1]-c[1])==1 for a,c in zip(r.rota,r.rota[1:])))

    def test_ucs_oraculo(self):
        for seed in (0,1,24114036,20231045):
            g=gerar_pomar(seed)
            self.assertEqual(b.ucs(g).custo,oraculo(g))
        self.assertEqual(b.ucs([list('.~.'),list('...')],objetivo=(0,2)).custo,4)

    def test_bfs_menor_numero_passos(self):
        r=b.bfs([list('.~.'),list('...')],objetivo=(0,2))
        self.assertEqual((r.passos,r.custo),(2,5))

    def test_grade_invalida(self):
        for g in ([],[[]],[list('.'),list('..')],[list('.x')]):
            with self.assertRaises(ValueError):
                b.ucs(g)
