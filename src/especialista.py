"""Regras de triagem ilustrativas; ausência de prova não significa falsidade."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Regra:
    nome: str
    premissas: tuple[str, ...]
    conclusao: str


REGRAS = [
    Regra('R1',('sensor_positivo',),'suspeita'),
    Regra('R2',('armadilha_positiva',),'suspeita'),
    Regra('R3',('suspeita','umidade_alta'),'risco_alto'),
    Regra('R4',('risco_alto','intervalo_maior_14'),'inspecionar_prioridade_alta'),
    Regra('R5',('suspeita','intervalo_ate_14'),'inspecionar_prioridade_normal'),
    Regra('R6',('inspecionar_prioridade_alta',),'solicitar_agronomo'),
    Regra('R7',('inspecionar_prioridade_normal',),'solicitar_agronomo'),
]
CORRECAO = Regra('R8',('lesoes_visiveis',),'suspeita')


def provar(objetivo, fatos, regras):
    if {'intervalo_maior_14','intervalo_ate_14'} <= fatos:
        raise ValueError('Intervalos mutuamente exclusivos')
    traco=[]

    def tentar(meta, ancestrais, nivel):
        prefixo='  '*nivel
        traco.append(f'{prefixo}OBJETIVO {meta}')
        if meta in fatos:
            traco.append(f'{prefixo}FATO {meta}')
            return {'fato':meta}
        if meta in ancestrais:
            traco.append(f'{prefixo}CICLO; ramo interrompido')
            return None
        for regra in regras:
            if regra.conclusao!=meta:
                continue
            traco.append(f'{prefixo}TENTA {regra.nome}: {" E ".join(regra.premissas)} -> {meta}')
            provas=[]
            for p in regra.premissas:
                prova=tentar(p,ancestrais|{meta},nivel+1)
                if prova is None:
                    break
                provas.append(prova)
            else:
                traco.append(f'{prefixo}CONCLUI {meta} por {regra.nome}')
                return {'conclusao':meta,'regra':regra.nome,'premissas':provas}
        traco.append(f'{prefixo}NAO PROVADO {meta}')
        return None

    prova=tentar(objetivo,set(),0)
    return {'objetivo':objetivo,'provado':prova is not None,'prova':prova,'traco':traco}


def demonstracao():
    fatos={'sensor_negativo','armadilha_negativa','lesoes_visiveis','umidade_alta','intervalo_maior_14'}
    corrigidas=REGRAS+[CORRECAO]
    return {'fatos':sorted(fatos),'regras_iniciais':REGRAS,'regras_corrigidas':corrigidas,
            'antes':provar('inspecionar_prioridade_alta',fatos,REGRAS),
            'depois':provar('inspecionar_prioridade_alta',fatos,corrigidas)}
