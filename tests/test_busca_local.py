import unittest
from src.busca_local import criar_modelo,avaliar,subida_encosta,tempera_simulada,experimentar
from src.gerador_pomar import gerar_pomar


class TestLocal(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.modelo=criar_modelo(gerar_pomar(24114036),24114036)
        cls.inicial=tuple(cls.modelo['candidatos'][:15])

    def test_distancias_direcionadas(self):
        m=criar_modelo([list('.~....') for _ in range(4)],0)
        self.assertEqual(m['distancias'][(0,0)][(0,1)],4)
        self.assertEqual(m['distancias'][(0,1)][(0,0)],1)

    def test_conjunto_e_bateria(self):
        a=avaliar(self.modelo,self.inicial)
        b=avaliar(self.modelo,tuple(reversed(self.inicial)))
        self.assertEqual(a,b)
        m={**self.modelo,'bateria_min':0}
        self.assertFalse(avaliar(m,self.inicial)['viavel'])
        self.assertGreater(avaliar(m,self.inicial)['violacao'],0)
        for s in (self.inicial[:14],self.inicial[:14]+(self.inicial[0],)):
            with self.assertRaises(ValueError):
                avaliar(self.modelo,s)
        with self.assertRaises(ValueError):
            criar_modelo([list('..')],0)

    def test_determinismo_e_melhor_guardado(self):
        inicial=avaliar(self.modelo,self.inicial)['valor']
        for fn in (subida_encosta,tempera_simulada):
            a=fn(self.modelo,self.inicial,42,max_avaliacoes=80)
            b=fn(self.modelo,self.inicial,42,max_avaliacoes=80)
            self.assertEqual(a,b)
            self.assertGreaterEqual(a['valor'],inicial)
            self.assertEqual(len(set(a['selecionados'])),15)
            self.assertLessEqual(a['avaliacoes'],80)

    def test_pareamento(self):
        r=experimentar(gerar_pomar(24114036),24114036,repeticoes=2,max_avaliacoes=30)
        self.assertEqual(len(r['execucoes']),4)
        self.assertEqual(r['execucoes'][0]['inicial'],r['execucoes'][1]['inicial'])
