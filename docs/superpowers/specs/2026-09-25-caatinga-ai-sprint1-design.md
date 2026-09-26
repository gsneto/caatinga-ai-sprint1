# Especificação — Caatinga.AI, Sprint 1

## 1. Objetivo e identificação

Preparar a atividade de Inteligência Artificial, UniRios, 2026.2, professor Ronierison Maciel, seguindo as seções 1–12 de `Atividade-Pratica.pdf`.

- Autor informado: ANTONIO GOMES SOUZA NETO.
- Matrícula apresentada: 241.14.036.
- Matrícula inteira entregue ao gerador: 24114036; resto por 1.000.000: 114036.
- Modalidade informada pelo autor: individual. O enunciado exige dupla; a exceção precisa ser aceita pelo professor e será documentada como pendência de entrega.
- Resultado esperado: código reproduzível, experimentos reais, relatório completo, anexo fiel de IA, repositório público e documento de uma página para o AVA.
- A finalidade inclui preparar o autor para executar outra semente e explicar os resultados na arguição.

## 2. Arquitetura e execução

Python 3.12 como ambiente de desenvolvimento; código compatível com Python 3.10 ou superior, sujeito à verificação das dependências. Biblioteca padrão para os algoritmos. Matplotlib exclusivamente para o gráfico, com versão compatível declarada em `requirements.txt` após consulta à documentação e teste.

Comando principal: `python src/main.py 24114036`. A interface também aceitará a matrícula pontuada, normalizando apenas pontos e rejeitando caracteres inesperados. Matrículas diferentes deverão funcionar sem alterar código.

Arquivos obrigatórios:

- `README.md`: identificação, descrição de 3–5 linhas, instalação/execução, tabela-resumo, convenções, mapa de arquivos e limitações, nessa ordem.
- `RELATORIO.md`: respostas numeradas para todas as questões das Partes 1–5 e bônus.
- `ANEXO_IA.md`: A.1–A.4, com transcrições reais e distinção entre verificação automática e revisão pessoal do estudante.
- `requirements.txt` e `.gitignore`.
- `src/gerador_pomar.py`: código do enunciado, sem mudanças de lógica, comentários, nomes ou valores. Conferência textual contra o trecho extraído do PDF, considerando somente as quebras de linha introduzidas pela diagramação.
- `src/buscas.py`: BFS, DFS, UCS e A*.
- `src/busca_local.py`: modelo explícito, subida de encosta e têmpera simulada.
- `src/especialista.py`: base de regras, encadeamento para trás e explicações.
- `src/bayes.py`: cálculos e resultados probabilísticos.
- `src/main.py`: execução integrada e geração dos artefatos.
- `resultados/resultados.csv`: cabeçalho exatamente `estrategia,heuristica,custo,passos,nos_expandidos,fronteira_max,tempo_ms`.
- `resultados/grafico.png`: estratégias/heurísticas no eixo horizontal, nós expandidos no vertical; título e eixos rotulados.
- `resultados/pomar.txt`: matrícula-semente na primeira linha e grade abaixo.

Arquivos adicionais justificados: testes, dados das 30 execuções, resultados de escalabilidade, rastros das regras, rotas, cálculos estruturados, evidências de aferição e roteiro breve de estudo para arguição.

O comando principal recriará os artefatos obrigatórios e os experimentos de tamanho fixo. O ensaio de escalabilidade terá comando separado, copiável no README, para evitar incluir uma espera de mais de 60 segundos em cada demonstração. Ambos os comandos terão seus resultados preservados.

## 3. Busca global e convenções de medição

- Estado: coordenada `(linha, coluna)` de um talhão transitável; distinguir total de estados transitáveis de estados alcançáveis a partir do portão.
- Início `(0, 0)`; objetivo `(n-1, n-1)`; movimento ortogonal; custo de entrada 1 ou 4; início excluído do custo.
- Fixar uma única ordem de vizinhos para todos os algoritmos. Verificar primeiro as consequências dessa ordem na matrícula de aferição. A ordem final será explicitada junto com desempates e tratamento do objetivo.
- BFS com fila e descoberta única; DFS com implementação e semântica documentadas; UCS e A* com fila de prioridade, melhor custo conhecido, descarte de entradas obsoletas e reabertura quando houver melhora.
- UCS/A*: testar objetivo quando retirado como entrada válida de menor prioridade. Não adotar término prematuro na geração apenas para aproximar uma contagem de referência.
- Definir nó expandido como retirada válida seguida de geração de sucessores; informar explicitamente se o objetivo é excluído. Entradas obsoletas não contam como expansão.
- Fronteira máxima: maior tamanho físico da estrutura de fronteira observado durante a execução, incluindo entradas obsoletas ainda presentes nas filas de prioridade. Se também houver métrica lógica, nomeá-la separadamente.
- Custo e passos serão recalculados a partir da rota; todas as arestas serão verificadas.
- Tempos medidos com relógio monotônico de alta resolução; informar que variam conforme computador e execução.

### Aferição e correção

Testar a matrícula 20231045: UCS 34, BFS 55 e 22 passos segundo o PDF. Investigar qualquer divergência com um oráculo independente, ordem de vizinhos, transcrição do gerador e semântica dos algoritmos. Não alterar o contrato nem preencher resultados esperados como se fossem medidos. Se a referência for incompatível com o gerador fornecido, registrar a evidência reproduzível e a limitação.

Casos pequenos verificarão custo inicial excluído, terreno bloqueado, rota válida, início igual ao objetivo, ausência de caminho, melhorias de custo e reabertura. A* com h=0 deve igualar UCS sob o mesmo desempate. UCS será comparado a um cálculo independente de menor custo em grades pequenas e na semente do autor.

## 4. Parte 1 — agente

PEAS com medidas quantitativas e unidades; seis classificações do ambiente com citações curtas do cenário; separar o problema de navegação do sistema completo com sensor imperfeito. Discutir especialmente observabilidade e evolução temporal, explicitando as informações faltantes e sem atribuir ao texto dados inexistentes.

Escolher e justificar um tipo de agente da taxonomia usual de cinco tipos, marcando que os slides das Aulas 01–05 não foram fornecidos. Formular métrica perversa com comportamento concreto e coordenadas verificadas no pomar, seguida de correção mensurável.

## 5. Parte 2 — busca cega e escalabilidade

Relatar os cinco componentes, contagem exata de estados, tabela BFS/DFS/UCS e diferença entre optimalidade em passos e em custo.

Escalabilidade: executar tamanhos crescentes começando em 12, 40 e 100, mantendo a mesma matrícula. Usar processos isolados, medição de tempo e captura do tipo real de falha. Interromper uma execução ao ultrapassar 60 segundos, ou registrar erro real de memória/pilha quando ocorrer. Não provocar deliberadamente esgotamento da memória de todo o Windows. Se a DFS usar recursão, manter e informar o limite efetivo, medir profundidade e distinguir esse limite da fronteira. Explicar os limites da implementação em grafo com visitados, comparando-os corretamente às fórmulas de busca em árvore.

## 6. Parte 3 — A*, busca local e bônus

Rodar h1=0, h2=Manhattan e h3=4×Manhattan. Provar admissibilidade de h1/h2. Encontrar no próprio pomar um estado concreto com h3 maior que o custo exato até o objetivo; imprimir coordenadas e valores. Comparar h3 com UCS, calculando perda percentual e diferença de expansões quando aplicável. Igualdade de custo em uma instância não prova admissibilidade.

Definir uma condição de negócio mensurável para usar uma busca sem garantia de ótimo. Distinguir condição proposta de desempenho realmente medido.

### Modelo da busca local

O enunciado não fornece riscos por talhão, conversão de custo em tempo nem duração da inspeção. Esses dados serão hipóteses sintéticas explícitas, geradas deterministamente em fluxo aleatório separado, sem alterar o gerador obrigatório.

- Estado: conjunto de K=15 talhões distintos e alcançáveis elegíveis para inspeção.
- Vizinhança: troca de um talhão selecionado por um não selecionado.
- Avaliação: benefício de inspeção sintético menos penalidade de deslocamento e violação do orçamento de 360 minutos; coeficientes, unidades e hipóteses declarados.
- O deslocamento será calculado por caminhos em talhões transitáveis, não por Manhattan atravessando bloqueios. A ordem de visita terá um procedimento determinístico declarado; seu custo não será apresentado como solução ótima do problema de roteamento.
- Sempre reportar viabilidade das soluções em relação à bateria; não chamar solução inviável de plano executável. Caso as hipóteses não produzam soluções viáveis, revisar o modelo antes dos experimentos finais, documentando a razão.
- Realizar 30 execuções por algoritmo, com sementes de reinício registradas, mesmos estados iniciais por par e orçamento de avaliações comparável.
- Reportar média, desvio padrão amostral, melhor valor e dados individuais; têmpera mantém a melhor solução encontrada.
- Instrumentar pioras aceitas e a evolução da melhor solução. Destacar evidência real nos rastros, inclusive se a têmpera não superar a subida de encosta. Não inventar superioridade.

Bônus: construir deliberadamente grade de no máximo 8×8 que direcione a DFS para uma rota de custo maior que duas vezes o ótimo, usando a ordem final de vizinhos. Entregar construção, explicação, rotas e custos verificados.

## 7. Parte 4 — regras e Bayes

Base inicial de 5–7 regras e base corrigida com até 8, com fatos explícitos, objetivos e encadeamento para trás. Explicar cada regra aplicada e fato usado; tratar ciclos e fracassos de prova. Construir caso legítimo mal classificado, mostrando rastros antes/depois e demonstrando que a correção não produz recomendações incompatíveis.

Calcular os quatro parâmetros da semente. Mostrar substituições numéricas para valor preditivo positivo, falsos por 100 alertas, falsos semanais, horas desperdiçadas a 12 minutos por inspeção e novo VPP com sensibilidade 0,999.

Na auditoria de dois testes, calcular o resultado sob independência condicional explicitamente assumida e explicar por que repetir o mesmo sensor no mesmo talhão não garante essa hipótese. Também considerar o limite de erros perfeitamente correlacionados.

Regra explícita de responsabilidade/auditabilidade: justificar a exigência de validação humana antes de uma intervenção agronômica relevante, sem apresentar o protótipo como sistema de aplicação automática.

## 8. Parte 5 — auditoria

Classificar as cinco afirmações como correta, parcialmente correta ou incorreta, com justificativa e evidências numéricas dos experimentos. Separar alegações universais de resultados de uma instância. Não assumir a queda de 38% nem a sensibilidade de 99% como valores medidos do próprio projeto quando os parâmetros gerados forem outros.

Recomendação final com no máximo oito linhas e condição técnica objetiva para mudar o veredito.

## 9. Parte 6 — registro de IA

Registrar o assistente e ferramentas efetivamente utilizados e em quais etapas. Preservar prompts e respostas reais para escolher duas transcrições integrais rastreáveis. Evitar atribuir ao estudante execuções feitas pelo assistente. Selecionar um erro real surgido no desenvolvimento com evidência verificável; um erro de ambiente não será disfarçado como erro conceitual. Se ainda não existir um erro apropriado, o anexo registrará essa pendência em vez de fabricar um.

Escrita natural e específica aos resultados, com explicações que o estudante possa revisar. A.4 deverá expressar uma conclusão sustentada pela execução; a validação de que corresponde ao aprendizado pessoal cabe ao autor.

## 10. GitHub, PDF e evidências de entrega

Repositório público: `caatinga-ai-sprint1`. Verificar previamente se já existe e qual conta está autenticada, sem mostrar credenciais. Usar a identidade Git existente, sem alterar configuração nem atribuir commits a uma segunda pessoa.

Histórico planejado: no mínimo oito commits correspondentes a etapas reais, por exemplo especificação, gerador/estrutura, busca cega, A*, busca local, especialista/Bayes, experimentos e documentação. Datas reais; sem fabricar autoria, sessões de trabalho ou participação de colega.

Antes de cada commit: conferir status, diff e histórico; incluir somente arquivos intencionais. Antes de publicar: verificar segredos, artefatos indevidos, testes e escopo. O pedido de executar o enunciado abrange preparar a entrega, mas nenhuma autenticação será inferida apenas da afirmação de que o Git já está logado.

Verificar acesso público sem autenticação e clonagem em diretório limpo. Um clone no mesmo PC não satisfaz a exigência de outro computador: registrar separadamente o teste local limpo e o teste externo pendente.

PDF `entrega_24114036.pdf`: uma página, identificação, URL clicável, hash curto real e checklist com estado comprovado. A declaração do enunciado será preservada para conferência e assinatura do autor, não assinada automaticamente. Enquanto houver teste externo ou autorização individual pendente, o documento será identificado como minuta e não como entrega integralmente atestada. Não enviar ao AVA sem pedido específico.

## 11. Critérios de conclusão

1. Comando documentado gera todos os três artefatos obrigatórios do zero.
2. As tabelas e afirmações quantitativas correspondem aos arquivos de resultados.
3. Testes conferem rotas, custos e propriedades de busca; gerador confere com o PDF.
4. Há 30 resultados para cada algoritmo local, rastros das regras e falha de escalabilidade efetivamente registrada.
5. Relatório cobre cada questão e os dois bônus quando sustentados por evidências.
6. Anexo de IA é fiel, específico e revisável pelo autor.
7. GitHub e PDF são verificados; requisitos que dependem do professor ou do autor permanecem expressamente identificados.

## 12. Revisão desta especificação

Conferida contra as seções 1–12 do PDF extraído. As hipóteses adicionais ficam restritas à modelagem solicitada de busca local e são identificadas. As pendências externas são conhecidas: permissão para trabalho individual, participação/assinatura do próprio autor, teste em outro computador e prazo exato do AVA. Não são usadas como evidência de etapas já concluídas.
