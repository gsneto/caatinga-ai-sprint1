
A.1 Ferramentas e partes em que foram utilizadas

Usei o GPT 6 Astra com o **OpenCode** para ajudar no planejamento, implementação dos módulos Python, criação dos testes, execução dos experimentos. O assistente operou as ferramentas no computador durante a conversa. Portanto, o fato de os testes terem sido executados automaticamente.

Ferramentas efetivamente usadas no trabalho:

- **Python, unittest e oráculo Bellman–Ford:** implementar e verificar rotas, custos, regras, Bayes e os comandos completos.
- **Matplotlib:** gerar o gráfico de nós expandidos.
- **Context7:** consultar documentação de Matplotlib e GitHub CLI.
- **PowerShell, Git e GitHub CLI:** executar os comandos e organizar o histórico de etapas.
- **Ferramentas de edição do OpenCode:** criar os arquivos e registrar a investigação de erros.
- **Agente revisor do OpenCode com contexto separado:** revisar o conjunto do código e documentos; apontou dois defeitos no supervisor de escalabilidade, reproduzidos e corrigidos com testes de regressão (ver `docs/VERIFICACAO.md`).

A.2 Dois prompts na íntegra e respostas recebidas

As transcrições abaixo preservam as mensagens textuais da conversa, inclusive maiúsculas. A segunda mensagem era uma continuação do planejamento já apresentado. As chamadas técnicas de ferramentas entre a mensagem e a resposta final não são mensagens redigidas pelo estudante e não foram confundidas com a resposta textual aqui reproduzida.

## Prompt 1

Vamos trabalhar juntos na Sprint 1 do Projeto Caatinga.AI

Nesta primeira etapa eu NÃO quero código. Quero que você:

1) Aponte os pontos que a correção realmente confere: a caixa de aferição 20231045
   (custo ótimo UCS = 34, custo BFS = 55, passos BFS = 22, nós UCS ≈ 112, A*+Manhattan
   ≈ 93), a ordem de expansão dos vizinhos, a reabertura de nós no A*, o comando único
   `python src/main.py <matricula>`.
2) Me proponha um plano de execução em etapas, na ordem certa, dizendo o que é
   implementado, o que é medido e o que vira texto em cada etapa.
3) Liste as decisões que dependem de mim ( ordem dos vizinhos, versão
   do A*, K=15) e me pergunte só o que realmente muda o trabalho.




# Prompt 2

PROMPT 2 — Execução e verificação

Plano aprovado. Agora execute, verificando cada passo antes de seguir:

1) Implemente BFS, DFS, UCS e A* (com reabertura de nós) em src/buscas.py, usando a ordem
   de vizinhos que declarei: [preencher, ex.: Norte, Sul, Oeste, Leste]. Instrumente os
   quatro contadores (custo, passos, nós expandidos, fronteira máxima).
2) Rode a AFERIÇÃO e me mostre o resultado lado a lado
   com a referência (34 / 55 / 22 / ~112 / ~93). Se custo ou passos não baterem exato,
   PARE e investigue antes de continuar; não ajuste o código para "forçar" o número.
3) Só depois da aferição bater, rode com a MINHA matrícula 241.14.036 e gere
   resultados/resultados.csv, resultados/grafico.png (eixos rotulados) e
   resultados/pomar.txt (semente na 1ª linha) pelo comando único.
4) Me mostre, para o meu pomar: a tabela de BFS/DFS/UCS, a tabela das três heurísticas do
   A*, os números de Bayes da Parte 4.3 e o ponto de falha do experimento de crescimento
   de n.
5) Se algo der errado, me mostre o erro real, explique a causa e corrija com teste de
   regressão. Não esconda erro nem invente resultado.

## A.3 Erro real, evidência e correção

O assistente escreveu um teste supondo que a grade 3×3 abaixo produziria alguma reabertura de A* quando fossem testadas todas as 512 atribuições possíveis de h=0 ou h=h* para os nove estados:

```
. ~ .
. . .
. . .
```

A afirmação não foi uma frase no relatório: estava materializada nesta expectativa do teste escrito pela IA:

```python
self.assertTrue(houve, 'Fixture deve realmente provocar reabertura')
```

O experimento contradisse a expectativa: **nenhuma das 512 execuções reabriu estado**, e o teste falhou com `AssertionError: False is not true`. Todas encontraram custo 4. O assistente tinha escolhido um caso que não demonstrava o comportamento que pretendia verificar.

A investigação separou dois fatos: uma heurística inconsistente **pode** exigir reabertura, mas uma grade arbitrária não necessariamente apresentará essa situação antes de o objetivo ser retirado. Foi então fixada uma grade 4×4 e uma tabela de heurística que realmente provocam **2 reaberturas**, com **15 expansões** e custo ótimo **6**. Um oráculo Bellman–Ford confirmou a admissibilidade da tabela em todos os estados.

A grade, a heurística e o erro original estão em [docs/erro_ia_reabertura.md](docs/erro_ia_reabertura.md); o teste corrigido está em `tests/test_astar.py`. O teste errado surgiu naturalmente durante o desenvolvimento, não foi introduzido de propósito para preencher esta seção. Para reproduzir o teste correto:

```bash
python -m unittest discover -s tests -p test_astar.py -v
```

## A.4 O que a execução acrescentou

**Conclusão apoiada pelos experimentos, a ser conferida pessoalmente pelo autor:** depois de executar o código, ficou demonstrado que neste pomar aceitar dois passos extras reduz o custo de 46 para 36, enquanto multiplicar Manhattan por quatro aumenta o custo para 51; a explicação teórica, sozinha, não fornecia esses números da minha matrícula.

## Nota de revisão pessoal

Este anexo registra o processo real. O projeto foi clonado e executado em outro computador. A revisão pessoal das transcrições e a assinatura cabem ao autor.
