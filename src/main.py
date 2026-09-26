"""Ponto de entrada: python src/main.py <matricula>."""
import argparse
import csv
import gzip
from dataclasses import asdict,is_dataclass
import json
from pathlib import Path
import re
import sys

if __package__ in (None,''):
    sys.path.insert(0,str(Path(__file__).resolve().parents[1]))

from src.gerador_pomar import gerar_pomar,parametros_sensor
from src.buscas import vizinhos
from src.experimentos import comparar_buscas,bonus_dfs,aferir,contraexemplo_h3
from src.busca_local import experimentar
from src.especialista import demonstracao
from src.bayes import calcular

RAIZ=Path(__file__).resolve().parents[1]
CAMPOS='estrategia heuristica custo passos nos_expandidos fronteira_max tempo_ms'.split()


def matricula_inteira(texto):
    if not re.fullmatch(r'[0-9]+(?:\.[0-9]+)*',texto):
        raise argparse.ArgumentTypeError('Use matricula numerica, com pontos opcionais')
    return int(texto.replace('.',''))


def salvar_json(caminho,dados):
    caminho.write_text(json.dumps(dados,ensure_ascii=False,indent=2,
                      default=lambda o:asdict(o) if is_dataclass(o) else str(o))+'\n',encoding='utf8')


def salvar_csv(caminho,linhas,campos):
    with caminho.open('w',encoding='utf8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=campos,extrasaction='ignore')
        w.writeheader()
        w.writerows(linhas)


def executar(matricula,saida):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    saida=Path(saida)
    saida.mkdir(parents=True,exist_ok=True)
    grade=gerar_pomar(matricula)
    globais=comparar_buscas(grade)
    local=experimentar(grade,matricula)
    tracos={f"{r['algoritmo']}_{r['execucao']}":r.pop('traco') for r in local['execucoes']}
    especialista=demonstracao()
    vistos={(0,0)}
    fila=[(0,0)]
    for p in fila:
        for q in vizinhos(grade,p):
            if q not in vistos:
                vistos.add(q)
                fila.append(q)
    resumo={'matricula':matricula,'semente':matricula%1_000_000,'grade':grade,
            'transitaveis':sum(c!='#' for row in grade for c in row),
            'alcancaveis':len(vistos),'buscas':globais,'busca_local':local,
            'bayes':calcular(parametros_sensor(matricula)),
            'especialista':especialista,'contraexemplo_h3':contraexemplo_h3(grade),
            'bonus_dfs':bonus_dfs(),'afericao':aferir()}
    salvar_csv(saida/'resultados.csv',globais,CAMPOS)
    (saida/'pomar.txt').write_text(f'Matricula-semente: {matricula} (modulo 1000000: {matricula%1_000_000})\n'
                                  +'\n'.join(' '.join(row) for row in grade)+'\n',encoding='utf8')
    fig,ax=plt.subplots(figsize=(10,5),layout='constrained')
    labels=[r['estrategia']+(' '+r['heuristica'] if r['heuristica']!='-' else '') for r in globais]
    barras=ax.bar(labels,[r['nos_expandidos'] for r in globais],color=['#448844','#778844','#228888','#5599aa','#2266bb','#cc8833'])
    ax.bar_label(barras,padding=3)
    ax.set(xlabel='Estrategia / heuristica',ylabel='Nos expandidos (quantidade)',
           title=f'Caatinga.AI - matricula {matricula}')
    ax.set_ylim(0,max(r['nos_expandidos'] for r in globais)*1.15)
    fig.savefig(saida/'grafico.png',dpi=160)
    plt.close(fig)
    salvar_json(saida/'resumo.json',resumo)
    salvar_json(saida/'afericao.json',resumo['afericao'])
    salvar_json(saida/'bonus_dfs.json',resumo['bonus_dfs'])
    salvar_json(saida/'bayes.json',resumo['bayes'])
    salvar_json(saida/'especialista.json',especialista)
    salvar_json(saida/'busca_local_resumo.json',local['resumo'])
    salvar_csv(saida/'busca_local.csv',local['execucoes'],
               'algoritmo execucao semente valor valor_inicial beneficio custo_movimento tempo_min viavel avaliacoes pioras_aceitas parada'.split())
    # Todos os 90 mil passos ficam disponíveis, sem duplicá-los no resumo.
    with gzip.open(saida/'busca_local_tracos.json.gz','wt',encoding='utf8') as f:
        json.dump(tracos,f,ensure_ascii=False,separators=(',',':'))
    salvar_json(saida/'tempera_execucao_1.json',tracos['tempera_simulada_1'])
    texto='ANTES\n'+'\n'.join(especialista['antes']['traco'])+'\n\nDEPOIS\n'+'\n'.join(especialista['depois']['traco'])+'\n'
    (saida/'especialista_tracos.txt').write_text(texto,encoding='utf8')
    for r in globais:
        print(f"{r['estrategia']} {r['heuristica']}: custo={r['custo']}, passos={r['passos']}, expandidos={r['nos_expandidos']}, fronteira={r['fronteira_max']}")
    print(texto)
    print('Busca local:',json.dumps(local['resumo'],ensure_ascii=True))
    print('Resultados:',saida.resolve())
    return resumo


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('matricula',type=matricula_inteira)
    parser.add_argument('--saida',type=Path,default=RAIZ/'resultados')
    args=parser.parse_args()
    executar(args.matricula,args.saida)


if __name__=='__main__':
    main()
