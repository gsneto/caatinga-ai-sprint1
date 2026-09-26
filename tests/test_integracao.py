import csv
import gzip
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from src.gerador_pomar import gerar_pomar,parametros_sensor

RAIZ=Path(__file__).resolve().parents[1]


class TestIntegracao(unittest.TestCase):
    def test_execucao_limpa_e_outra_semente(self):
        for seed in ('241.14.036','20231045'):
            with tempfile.TemporaryDirectory() as pasta:
                p=subprocess.run([sys.executable,str(RAIZ/'src/main.py'),seed,'--saida',pasta],
                                 cwd=pasta,capture_output=True,text=True,timeout=180)
                self.assertEqual(p.returncode,0,p.stdout+p.stderr)
                dest=Path(pasta)
                with (dest/'resultados.csv').open(encoding='utf8',newline='') as f:
                    linhas=list(csv.DictReader(f))
                self.assertEqual(len(linhas),6)
                self.assertEqual((dest/'grafico.png').read_bytes()[:8],b'\x89PNG\r\n\x1a\n')
                m=int(seed.replace('.',''))
                grade=(dest/'pomar.txt').read_text().splitlines()[1:]
                self.assertEqual(grade,[' '.join(r) for r in gerar_pomar(m)])
                r=json.loads((dest/'resumo.json').read_text(encoding='utf8'))
                self.assertEqual(r['bayes']['parametros'],parametros_sensor(m))
                self.assertEqual(len(r['busca_local']['execucoes']),60)
                with gzip.open(dest/'busca_local_tracos.json.gz','rt',encoding='utf8') as f:
                    self.assertEqual(len(json.load(f)),60)

    def test_rejeita_matricula_invalida(self):
        p=subprocess.run([sys.executable,str(RAIZ/'src/main.py'),'abc'],capture_output=True)
        self.assertNotEqual(p.returncode,0)
