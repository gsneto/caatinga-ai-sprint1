"""Probabilidades sem arredondamento intermediário."""
import math


def _vpp(p,s,f):
    total=s*p+f*(1-p)
    return s*p/total if total else None


def calcular(parametros):
    p=parametros['prevalencia']
    s=parametros['sensibilidade']
    f=parametros['taxa_falso_positivo']
    n=parametros['talhoes_por_semana']
    if any(not isinstance(v,(int,float)) or not math.isfinite(v) or not 0<=v<=1 for v in (p,s,f)):
        raise ValueError('Probabilidades devem estar entre zero e um')
    if not isinstance(n,int) or isinstance(n,bool) or n<0:
        raise ValueError('Numero de talhoes deve ser inteiro nao negativo')
    vpp=_vpp(p,s,f)
    fp=n*f*(1-p)
    return {'parametros':dict(parametros),'vpp':vpp,
            'falsos_por_100_alertas':100*(1-vpp) if vpp is not None else None,
            'verdadeiros_semana':n*s*p,'falsos_semana':fp,'horas_semana':fp*12/60,
            'vpp_sensibilidade_999':_vpp(p,.999,f),
            'vpp_dois_independentes':_vpp(p,s*s,f*f),
            'vpp_dois_correlacao_perfeita':vpp,
            'vpp_fornecedor_99':_vpp(p,.99,f),
            'vpp_fornecedor_dois_99_independentes':_vpp(p,.99**2,f*f)}
