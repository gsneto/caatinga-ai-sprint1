import unittest
from src.especialista import Regra,provar,demonstracao


class TestEspecialista(unittest.TestCase):
    def test_correcao_e_traco(self):
        d=demonstracao()
        self.assertFalse(d['antes']['provado'])
        self.assertTrue(d['depois']['provado'])
        for nome in ('R8','R3','R4'):
            self.assertIn(nome,str(d['depois']['prova']))

    def test_ciclo_e_desconhecido(self):
        regras=[Regra('a',('b',),'a'),Regra('b',('a',),'b')]
        self.assertFalse(provar('a',set(),regras)['provado'])
        self.assertTrue(provar('a',{'b'},regras)['provado'])
        self.assertFalse(provar('x',set(),[])['provado'])

    def test_alternativa_apos_ciclo(self):
        regras=[Regra('ciclo',('a',),'a'),Regra('caminho',('fato',),'a')]
        self.assertTrue(provar('a',{'fato'},regras)['provado'])

    def test_intervalos(self):
        d=demonstracao()
        for intervalo in ('intervalo_maior_14','intervalo_ate_14'):
            fatos={'sensor_positivo','umidade_alta',intervalo}
            valores=[provar('inspecionar_prioridade_'+p,fatos,d['regras_corrigidas'])['provado'] for p in ('alta','normal')]
            self.assertEqual(sum(valores),1)
        with self.assertRaises(ValueError):
            provar('x',{'intervalo_maior_14','intervalo_ate_14'},[])
