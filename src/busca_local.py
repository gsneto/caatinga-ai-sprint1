"""Seleção de K=15 inspeções: hipóteses sintéticas, bateria e busca local."""
import heapq
import math
import random
import statistics

from .buscas import vizinhos, _validar
from .gerador_pomar import CUSTO

K = 15


def _distancias(grade, origem):
    d={origem:0}
    fila=[(0,origem)]
    while fila:
        custo,p=heapq.heappop(fila)
        if custo != d[p]:
            continue
        for q in vizinhos(grade,p):
            novo=custo+CUSTO[grade[q[0]][q[1]]]
            if novo < d.get(q,math.inf):
                d[q]=novo
                heapq.heappush(fila,(novo,q))
    return d


def criar_modelo(grade, matricula, bateria_min=360):
    objetivo=_validar(grade,(0,0),None)
    alcancaveis=sorted(_distancias(grade,(0,0)))
    candidatos=[p for p in alcancaveis if p not in ((0,0),objetivo)]
    if len(candidatos)<K or objetivo not in alcancaveis:
        raise ValueError('Sao necessarios objetivo alcancavel e 15 candidatos')
    rng=random.Random((matricula%1_000_000)+2026)
    return {'candidatos':candidatos,'beneficios':{p:rng.randint(1,100) for p in candidatos},
            'distancias':{p:_distancias(grade,p) for p in alcancaveis},
            'inicio':(0,0),'objetivo':objetivo,'bateria_min':bateria_min}


def avaliar(modelo, selecionados):
    s=tuple(sorted(selecionados))
    if len(s)!=K or len(set(s))!=K or any(p not in modelo['beneficios'] for p in s):
        raise ValueError('Selecione exatamente 15 candidatos distintos e alcancaveis')
    restantes=set(s)
    atual=modelo['inicio']
    visitas=[atual]
    custo=0
    while restantes:
        q=min(restantes,key=lambda p:(modelo['distancias'][atual][p],p))
        custo+=modelo['distancias'][atual][q]
        visitas.append(q)
        restantes.remove(q)
        atual=q
    custo+=modelo['distancias'][atual][modelo['objetivo']]
    visitas.append(modelo['objetivo'])
    tempo=custo+12*K
    violacao=max(0,tempo-modelo['bateria_min'])
    beneficio=sum(modelo['beneficios'][p] for p in s)
    return {'selecionados':s,'valor':beneficio-.5*custo-1000*violacao,
            'beneficio':beneficio,'tempo_min':tempo,'violacao':violacao,
            'viavel':violacao==0,'custo_movimento':custo,'rota_visitas':visitas}


def subida_encosta(modelo, inicial, semente, max_avaliacoes=3000):
    """Melhor melhoria entre trocas examinadas, até o teto de avaliações.

    No último passe incompleto, usa a melhor troca examinada; não declara
    máximo local nesse caso. A semente é registrada para pareamento.
    """
    atual=avaliar(modelo,inicial)
    avaliacoes=0
    traco=[]
    parada='orcamento'
    while avaliacoes<max_avaliacoes:
        melhor=atual
        fora=[p for p in modelo['candidatos'] if p not in atual['selecionados']]
        completo=True
        for sai in atual['selecionados']:
            for entra in fora:
                if avaliacoes>=max_avaliacoes:
                    completo=False
                    break
                s=tuple(p for p in atual['selecionados'] if p!=sai)+(entra,)
                candidato=avaliar(modelo,s)
                avaliacoes+=1
                if candidato['valor']>melhor['valor']:
                    melhor=candidato
            if not completo:
                break
        if melhor['valor']<=atual['valor']:
            parada='maximo_local' if completo else 'orcamento'
            break
        atual=melhor
        traco.append({'avaliacao':avaliacoes,'melhor':atual['valor']})
    return {**atual,'avaliacoes':avaliacoes,'parada':parada,'pioras_aceitas':0,'traco':traco}


def tempera_simulada(modelo, inicial, semente, max_avaliacoes=3000):
    rng=random.Random(semente)
    atual=avaliar(modelo,inicial)
    melhor=atual
    traco=[]
    pioras=0
    for passo in range(max_avaliacoes):
        temperatura=50*(.05/50)**(passo/max(1,max_avaliacoes-1))
        sai=rng.choice(atual['selecionados'])
        fora=[p for p in modelo['candidatos'] if p not in atual['selecionados']]
        if not fora:
            return {**melhor,'avaliacoes':passo,'parada':'sem_vizinhos','pioras_aceitas':pioras,'traco':traco}
        entra=rng.choice(fora)
        s=tuple(p for p in atual['selecionados'] if p!=sai)+(entra,)
        candidato=avaliar(modelo,s)
        delta=candidato['valor']-atual['valor']
        aceitou=delta>=0 or rng.random()<math.exp(delta/temperatura)
        if aceitou:
            atual=candidato
            pioras+=int(delta<0)
            if atual['valor']>melhor['valor']:
                melhor=atual
        traco.append({'passo':passo+1,'temperatura':temperatura,'delta':delta,
                      'aceitou':aceitou,'atual':atual['valor'],'melhor':melhor['valor']})
    return {**melhor,'avaliacoes':max_avaliacoes,'parada':'orcamento',
            'pioras_aceitas':pioras,'traco':traco}


def experimentar(grade, matricula, repeticoes=30, max_avaliacoes=3000):
    modelo=criar_modelo(grade,matricula)
    execucoes=[]
    for indice in range(repeticoes):
        seed=matricula+indice
        inicial=tuple(sorted(random.Random(seed).sample(modelo['candidatos'],K)))
        for nome,fn in (('subida_encosta',subida_encosta),('tempera_simulada',tempera_simulada)):
            r=fn(modelo,inicial,seed,max_avaliacoes)
            execucoes.append({'algoritmo':nome,'execucao':indice+1,'semente':seed,
                             'inicial':inicial,'valor_inicial':avaliar(modelo,inicial)['valor'],**r})
    resumo={}
    for nome in ('subida_encosta','tempera_simulada'):
        linhas=[r for r in execucoes if r['algoritmo']==nome]
        valores=[r['valor'] for r in linhas]
        resumo[nome]={'media':statistics.mean(valores),
                      'desvio_amostral':statistics.stdev(valores) if len(valores)>1 else 0,
                      'melhor':max(valores),'viaveis':sum(r['viavel'] for r in linhas)}
    return {'execucoes':execucoes,'resumo':resumo,
            'modelo':{'K':K,'bateria_min':360,'min_por_inspecao':12,'min_por_custo':1,
                      'beneficios':[{'talhao':p,'pontos':v} for p,v in modelo['beneficios'].items()],
                      'orcamento_avaliacoes':max_avaliacoes}}
