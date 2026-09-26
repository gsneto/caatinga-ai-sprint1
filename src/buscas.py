"""Busca em grafo; custos de entrada e ordem Norte, Sul, Oeste, Leste."""
from collections import deque
from dataclasses import dataclass
import heapq
import itertools
from time import perf_counter

from .gerador_pomar import CUSTO

ORDEM = ((-1, 0), (1, 0), (0, -1), (0, 1))


@dataclass
class ResultadoBusca:
    rota: list[tuple[int, int]]
    custo: int | None
    passos: int | None
    nos_expandidos: int
    fronteira_max: int
    tempo_ms: float
    reaberturas: int = 0


class LimiteDFS(RecursionError):
    def __init__(self, profundidade, expandidos):
        super().__init__('Limite real de recursao atingido pela DFS')
        self.profundidade = profundidade
        self.nos_expandidos = expandidos


def _validar(g, inicio, objetivo):
    if not g or not g[0] or any(len(r) != len(g[0]) for r in g):
        raise ValueError('A grade deve ser retangular e nao vazia')
    if any(c not in '.~#' for r in g for c in r):
        raise ValueError('Terreno desconhecido')
    objetivo = (len(g)-1, len(g[0])-1) if objetivo is None else objetivo
    for i,j in (inicio, objetivo):
        if not (0 <= i < len(g) and 0 <= j < len(g[0])) or g[i][j] == '#':
            raise ValueError('Inicio e objetivo devem ser transitaveis e estar na grade')
    return objetivo


def vizinhos(grade, estado):
    for di,dj in ORDEM:
        i,j = estado[0]+di,estado[1]+dj
        if 0 <= i < len(grade) and 0 <= j < len(grade[0]) and grade[i][j] != '#':
            yield i,j


def manhattan(estado, objetivo):
    return abs(estado[0]-objetivo[0])+abs(estado[1]-objetivo[1])


def _resultado(g, pais, fim, expandidos, maximo, t0, reaberturas=0):
    rota = []
    if fim is not None:
        while fim is not None:
            rota.append(fim)
            fim = pais[fim]
        rota.reverse()
    custo = sum(CUSTO[g[i][j]] for i,j in rota[1:]) if rota else None
    return ResultadoBusca(rota,custo,len(rota)-1 if rota else None,
                          expandidos,maximo,(perf_counter()-t0)*1000,reaberturas)


def bfs(grade, inicio=(0,0), objetivo=None):
    t0 = perf_counter()
    objetivo = _validar(grade,inicio,objetivo)
    fila, pais = deque([inicio]), {inicio:None}
    expandidos, maximo = 0,1
    while fila:
        atual = fila.popleft()
        if atual == objetivo:
            return _resultado(grade,pais,atual,expandidos,maximo,t0)
        expandidos += 1
        for q in vizinhos(grade,atual):
            if q not in pais:
                pais[q] = atual
                fila.append(q)
                maximo = max(maximo,len(fila))
    return _resultado(grade,pais,None,expandidos,maximo,t0)


def astar(grade, heuristica, inicio=(0,0), objetivo=None):
    """A* com relaxamento estrito, descarte obsoleto e reabertura.

    A heurística recebe (estado, objetivo). Garantia de custo ótimo exige
    admissibilidade, h(objetivo)=0 e custos positivos, como nesta grade.
    """
    t0 = perf_counter()
    objetivo = _validar(grade,inicio,objetivo)
    seq = itertools.count()
    fila = [(heuristica(inicio,objetivo),next(seq),0,inicio)]
    melhores,pais,fechados = {inicio:0},{inicio:None},{}
    expandidos,maximo,reaberturas = 0,1,0
    while fila:
        _,_,custo,atual = heapq.heappop(fila)
        if custo != melhores[atual]:
            continue
        if atual == objetivo:
            return _resultado(grade,pais,atual,expandidos,maximo,t0,reaberturas)
        if atual in fechados:
            reaberturas += 1
        fechados[atual] = custo
        expandidos += 1
        for q in vizinhos(grade,atual):
            novo = custo+CUSTO[grade[q[0]][q[1]]]
            if novo < melhores.get(q,float('inf')):
                melhores[q],pais[q] = novo,atual
                heapq.heappush(fila,(novo+heuristica(q,objetivo),next(seq),novo,q))
                maximo = max(maximo,len(fila))
    return _resultado(grade,pais,None,expandidos,maximo,t0,reaberturas)


def dfs(grade, inicio=(0,0), objetivo=None):
    """DFS recursiva: fronteira medida como pilha de chamadas ativas."""
    t0 = perf_counter()
    objetivo = _validar(grade,inicio,objetivo)
    pais = {inicio:None}
    expandidos, maximo = 0,1

    def visitar(atual, profundidade):
        nonlocal expandidos,maximo
        maximo = max(maximo,profundidade)
        if atual == objetivo:
            return True
        expandidos += 1
        for q in vizinhos(grade,atual):
            if q not in pais:
                pais[q] = atual
                if visitar(q,profundidade+1):
                    return True
        return False

    try:
        achou = visitar(inicio,1)
    except RecursionError as e:
        raise LimiteDFS(maximo,expandidos) from e
    return _resultado(grade,pais,objetivo if achou else None,expandidos,maximo,t0)


def ucs(grade, inicio=(0,0), objetivo=None):
    t0 = perf_counter()
    objetivo = _validar(grade,inicio,objetivo)
    seq = itertools.count()
    fila = [(0,next(seq),inicio)]
    melhores,pais = {inicio:0},{inicio:None}
    expandidos,maximo = 0,1
    while fila:
        custo,_,atual = heapq.heappop(fila)
        if custo != melhores[atual]:
            continue
        if atual == objetivo:
            return _resultado(grade,pais,atual,expandidos,maximo,t0)
        expandidos += 1
        for q in vizinhos(grade,atual):
            novo = custo+CUSTO[grade[q[0]][q[1]]]
            if novo < melhores.get(q,float('inf')):
                melhores[q],pais[q] = novo,atual
                heapq.heappush(fila,(novo,next(seq),q))
                maximo = max(maximo,len(fila))
    return _resultado(grade,pais,None,expandidos,maximo,t0)
