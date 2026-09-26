import unittest
import os
from time import perf_counter
from unittest.mock import patch
from src.escalabilidade import medir


def encerrar_sem_resposta(conn, matricula, n, estrategia):
    os._exit(7)


def resposta_ja_atrasada(conn, matricula, n, estrategia):
    conn.send({'evento':'pronto','geracao_s':0,'inicio_busca':perf_counter()-.1})
    conn.send({'status':'ok','tempo_s':.1})
    conn.close()


class TestEscala(unittest.TestCase):
    def test_busca_real_e_limite_pilha(self):
        r=medir(24114036,12,'bfs')
        self.assertEqual(r['status'],'ok')
        self.assertGreater(r['nos_expandidos'],0)
        r=medir(24114036,100,'dfs')
        self.assertEqual(r['status'],'RecursionError')
        self.assertGreater(r['profundidade'],0)

    def test_timeout(self):
        r=medir(24114036,40,'ucs',limite_s=0)
        self.assertEqual(r['status'],'tempo_acima_limite')

    def test_filho_morre_e_preserva_codigo_saida(self):
        with patch('src.escalabilidade._worker',encerrar_sem_resposta):
            r=medir(24114036,12,'bfs')
        self.assertEqual(r['status'],'processo_encerrado_sem_resposta')
        self.assertEqual(r['exitcode'],7)

    def test_resposta_fora_prazo_nao_vira_sucesso(self):
        with patch('src.escalabilidade._worker',resposta_ja_atrasada):
            r=medir(24114036,12,'bfs',limite_s=.01)
        self.assertEqual(r['status'],'tempo_acima_limite')
