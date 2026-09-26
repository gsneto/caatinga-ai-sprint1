# Erro real encontrado durante a implementação

O assistente escreveu inicialmente um teste que supunha que a grade
`[".~.", "...", "..."]`, com objetivo (2,2), provocaria reabertura de A*
em pelo menos uma das 512 atribuições de h=0 ou h=h* por estado.
A expectativa estava expressa no teste como:

```python
self.assertTrue(houve, 'Fixture deve realmente provocar reabertura')
```

Execução real: **FAIL**, `AssertionError: False is not true`.
As 512 execuções retornaram custo 4, mas nenhuma reabriu estado.
O erro estava na escolha do caso de teste: admissibilidade inconsistente
pode exigir reabertura, mas não significa que qualquer grade pequena
irá demonstrá-la antes da retirada do objetivo. Nessa grade o atalho
caro não é expandido a tempo de criar a melhora esperada.

O assistente investigou grades pequenas e fixou este caso 4×4:

```
. ~ . ~
. . . ~
. . . .
~ . . .
```

Tabela de h, com objetivo (3,3):

```
6 0 0 0
5 4 0 2
0 0 0 0
0 2 1 0
```

Resultado observado: custo **6**, **15** expansões e **2** reaberturas.
O oráculo Bellman–Ford confirma h≤h* em cada coordenada. A inconsistência
é concreta: h(0,0)=6 > custo((0,0),(0,1))+h(0,1)=4+0.
O teste corrigido está em `tests/test_astar.py`.

Esta foi uma suposição errada do assistente efetivamente desmentida pelo
experimento, e não um erro introduzido de propósito para preencher o anexo.
