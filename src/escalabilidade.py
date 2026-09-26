"""Ensaio isolado até primeira falha real: python src/escalabilidade.py <matricula>."""
import argparse
import multiprocessing as mp
from pathlib import Path
import platform
import sys
from time import perf_counter

if __package__ in (None,''):
    sys.path.insert(0,str(Path(__file__).resolve().parents[1]))

from src.buscas import bfs,dfs,ucs,LimiteDFS
from src.gerador_pomar import gerar_pomar
from src.main import matricula_inteira,salvar_csv,salvar_json,RAIZ


def _worker(conn,matricula,n,estrategia):
    try:
        t0=perf_counter()
        g=gerar_pomar(matricula,n)
        geracao=perf_counter()-t0
        t0=perf_counter()
        conn.send({'evento':'pronto','geracao_s':geracao,'inicio_busca':t0})
        try:
            r={'bfs':bfs,'dfs':dfs,'ucs':ucs}[estrategia](g)
            dados={'status':'ok','nos_expandidos':r.nos_expandidos,'fronteira_max':r.fronteira_max,
                   'custo':r.custo,'passos':r.passos,'profundidade':r.fronteira_max if estrategia=='dfs' else None}
        except LimiteDFS as e:
            dados={'status':'RecursionError','nos_expandidos':e.nos_expandidos,'profundidade':e.profundidade}
        except MemoryError:
            dados={'status':'MemoryError'}
        conn.send({**dados,'tempo_s':perf_counter()-t0,'limite_recursao':sys.getrecursionlimit()})
    except Exception as e:
        conn.send({'status':type(e).__name__,'erro':str(e)})
    finally:
        conn.close()


def medir(matricula,n,estrategia,limite_s=60):
    contexto=mp.get_context('spawn')
    pai,filho=contexto.Pipe(duplex=False)
    processo=contexto.Process(target=_worker,args=(filho,matricula,n,estrategia))
    processo.start()
    filho.close()
    resultado={'matricula':matricula,'n':n,'estrategia':estrategia,'limite_s':limite_s,'fase':'geracao'}
    try:
        if not pai.poll(60):
            resultado['status']='limite_geracao_60s'
        else:
            pronto=pai.recv()
            if pronto.get('evento')!='pronto':
                resultado.update(pronto)
            else:
                resultado.update(geracao_s=pronto['geracao_s'],fase='busca')
                inicio=pronto['inicio_busca']
                restante=max(0,inicio+limite_s-perf_counter())
                if not pai.poll(restante):
                    resultado.update(status='tempo_acima_limite',tempo_s=perf_counter()-inicio)
                else:
                    resultado.update(pai.recv())
                    if resultado.get('tempo_s',0)>limite_s:
                        resultado['status_original']=resultado['status']
                        resultado['status']='tempo_acima_limite'
    except (EOFError,OSError) as e:
        resultado.update(status='processo_encerrado_sem_resposta',erro=type(e).__name__)
    finally:
        processo.join(timeout=.2)
        if processo.is_alive():
            processo.terminate()
            processo.join()
        resultado['exitcode']=processo.exitcode
        pai.close()
    return resultado


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('matricula',type=matricula_inteira)
    parser.add_argument('--saida',type=Path,default=RAIZ/'resultados')
    args=parser.parse_args()
    args.saida.mkdir(parents=True,exist_ok=True)
    campos='matricula n estrategia status tempo_s geracao_s limite_s nos_expandidos fronteira_max custo passos profundidade limite_recursao fase exitcode'.split()
    linhas=[]
    n=12
    for passo in range(20):
        if passo<3:
            n=(12,40,100)[passo]
        else:
            n*=2
        falhou=False
        for estrategia in ('bfs','dfs','ucs'):
            r=medir(args.matricula,n,estrategia)
            print(r,flush=True)
            linhas.append(r)
            falhou |= r['status']!='ok'
            # Checkpoint por medição: uma falha posterior não apaga a evidência anterior.
            salvar_csv(args.saida/'escalabilidade.csv',linhas,campos)
            salvar_json(args.saida/'escalabilidade.json',{'python':sys.version,'plataforma':platform.platform(),'medicoes':linhas})
        if falhou:
            break


if __name__=='__main__':
    main()
