"""Experimentos de busca global; dados completos para auditoria."""
from dataclasses import asdict
from .buscas import bfs,dfs,ucs,astar,manhattan
from .gerador_pomar import gerar_pomar


def comparar_buscas(grade):
    saida=[]
    for nome,h,fn in (
        ('BFS','-',bfs),('DFS','-',dfs),('UCS','-',ucs),
        ('A*','h1',lambda g:astar(g,lambda a,b:0)),
        ('A*','h2',lambda g:astar(g,manhattan)),
        ('A*','h3',lambda g:astar(g,lambda a,b:4*manhattan(a,b))),
    ):
        saida.append({'estrategia':nome,'heuristica':h,**asdict(fn(grade))})
    return saida


def bonus_dfs():
    # Construção: estrada barata na borda superior/direita; DFS desce primeiro.
    grade=[list('.....')]+[list('~~~~.') for _ in range(4)]
    return {'grade':grade,'dfs':asdict(dfs(grade)),'ucs':asdict(ucs(grade))}


def aferir():
    linhas=comparar_buscas(gerar_pomar(20231045))
    assert linhas[0]['custo']==55 and linhas[0]['passos']==22
    assert linhas[2]['custo']==34
    assert 112*.8<=linhas[2]['nos_expandidos']<=112*1.2
    assert 93*.8<=linhas[4]['nos_expandidos']<=93*1.2
    return {'matricula':20231045,'esperado':{'ucs_custo':34,'bfs_custo':55,'bfs_passos':22},
            'obtido':linhas}


def contraexemplo_h3(grade):
    objetivo=(len(grade)-1,len(grade[0])-1)
    # Varrer do objetivo para trás favorece uma evidência curta de conferir.
    for i in reversed(range(len(grade))):
        for j in reversed(range(len(grade[0]))):
            if grade[i][j]=='#':
                continue
            r=ucs(grade,(i,j),objetivo)
            h=4*manhattan((i,j),objetivo)
            if r.custo is not None and h>r.custo:
                return {'estado':(i,j),'objetivo':objetivo,'h3':h,'custo_real':r.custo,'rota':r.rota}
    return None
