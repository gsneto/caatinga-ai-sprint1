# Caatinga.AI — relatório da Sprint 1

**Inteligência Artificial — UniRios — 2026.2 — Prof. Ronierison Maciel**  
**Autor:** ANTONIO GOMES SOUZA NETO — **matrícula:** 241.14.036  
**Entrada inteira:** 24114036 — **semente efetiva:** 114036.

Os números abaixo vieram da execução do código deste repositório. A assistência de IA e as verificações estão descritas no [anexo](ANEXO_IA.md). As referências às Aulas 01–05 seguem os conceitos nomeados no enunciado; os slides não foram fornecidos. Coordenadas começam em zero e têm ordem **(linha, coluna)**.

## Convenções que tornam os resultados reproduzíveis

- Vizinhos: **Norte, Sul, Oeste, Leste**, em todas as estratégias.
- BFS descobre ao enfileirar. DFS é recursiva, visita cada estado no máximo uma vez e explora o próximo vizinho somente depois de retornar do anterior.
- UCS/A*: heap, desempate pela ordem de inserção, relaxamento por custo estritamente menor, descarte de entradas obsoletas. A* **reabre estados** se encontrar menor g. O teste de regressão demonstra duas reaberturas com h admissível inconsistente.
- Um nó é expandido quando seus sucessores serão examinados. O objetivo é testado antes desse exame e **não conta** como expandido. UCS e A* só terminam ao retirar uma entrada válida do objetivo da fila, nunca na primeira geração dele.
- Fronteira máxima é a quantidade máxima de entradas físicas na fila/heap. No heap inclui entradas obsoletas ainda não retiradas. Na DFS mede os quadros ativos da pilha recursiva, incluindo início e objetivo. Não mede toda a memória: visitados, pais e melhores custos também ocupam espaço.
- Custo é soma dos terrenos em que a rota entra; o terreno inicial fica de fora. Passos = tamanho da rota − 1. Tempo está em milissegundos no CSV e varia com a máquina; custo, rota e contadores são determinísticos sob estas convenções.

### Aferição com a matrícula fictícia

| Medida | PDF | Execução |
|---|---:|---:|
| UCS: custo | 34 | 34 |
| BFS: custo | 55 | 55 |
| BFS: passos | 22 | 22 |
| UCS: expansões | aproximadamente 112 | 111 |
| A* Manhattan: expansões | aproximadamente 93 | 90 |

Fonte: [afericao.json](resultados/afericao.json). Custos e passos coincidem exatamente; expansões estão dentro da tolerância. Além disso, um **oráculo Bellman–Ford independente** confirmou UCS em quatro sementes. Gerar o objetivo cedo não é critério geral seguro para UCS/A*: uma rota mais barata ainda pode estar na fronteira.

## Parte 1 — O agente antes do código

### 1.1 Ficha PEAS

| Componente | Especificação |
|---|---|
| P — desempenho | Chegar ao ponto de coleta em 100% das missões com rota disponível; minimizar **unidades de custo por missão**; na seleção de inspeções, maximizar benefício sob **360 minutos**; medir **falsos alertas/semana**, **horas de inspeção improdutiva/semana** e **talhões distintos inspecionados/missão**. Tratar colisão/entrada bloqueada como violação, não como troca aceitável por benefício. |
| E — ambiente | Pomar de manga com 12×12 talhões, carreadores, irrigação/solo encharcado e bloqueios; portão (0,0), coleta (11,11), pragas e equipe humana de inspeção. |
| A — atuadores | Deslocamento ortogonal, parada para leitura/inspeção e emissão de alerta localizado para o agrônomo. O protótipo calcula planos e recomendações; não aciona pulverizador. |
| S — sensores | Posição e mapa dos terrenos, sensor óptico de pragas; para a base de regras, observações de armadilha, umidade, lesões e registro de pulverização são entradas fornecidas. |

### 1.2 Seis dimensões do ambiente

| Dimensão | Classificação adotada | Trecho do cenário e justificativa |
|---|---|---|
| Observabilidade | Total para a navegação com grade conhecida; parcial para o estado sanitário | “Cada talhão é de um dos três tipos” e o gerador fornece a grade; o sensor apenas “aponta talhões suspeitos”. Suspeita não revela a infestação com certeza. |
| Determinismo | Transição de navegação determinística; observação sanitária estocástica | “Só se move nas quatro direções ortogonais” e cada terreno possui custo definido. O enunciado fornece sensibilidade e falso positivo, portanto a leitura não determina a verdade sanitária. |
| Episódico/sequencial | Sequencial | “Entra pelo portão em (0,0), precisa chegar [...] em (11,11)”. Cada movimento altera a posição e as próximas escolhas, além de consumir recurso. |
| Estático/dinâmico | Estático durante a busca simulada; discutível na operação real | A grade e os custos são gerados antes da execução. Entretanto, “solo encharcado / linha de irrigação” pode mudar enquanto o agente delibera; o texto não informa quando isso ocorre. |
| Discreto/contínuo | Discreto no modelo | “Grade de 12×12 talhões” e “quatro direções ortogonais”: posições e ações enumeráveis, custos 1 ou 4. |
| Agente único/multiagente | Agente único no planejamento | “Um agente que percorre um pomar”. Humanos recebem inspeções; não há outro agente com decisões estratégicas concorrentes na busca modelada. |

As **duas dimensões discutíveis** são observabilidade e estaticidade. Para a primeira, falta saber se o agente conhece previamente todo o mapa e quais informações sanitárias reais recebe; conhecer a grade não significa conhecer a infestação. Para a segunda, falta saber se irrigação, obstáculos e pragas mudam durante uma missão/planejamento. A distinção entre transição determinística e sensor ruidoso evita chamar o movimento de aleatório apenas porque a percepção sanitária é incerta.

### 1.3 Tipo de agente

Escolha: **agente baseado em utilidade**, com estado interno. Um agente apenas orientado ao objetivo distingue chegar de não chegar, mas não expressa adequadamente a preferência por uma rota de custo 36 em vez de 46, nem a seleção de inspeções sob bateria limitada. A utilidade representa benefício, deslocamento e restrição de tempo. O estado interno registra posição, terrenos conhecidos e observações. Não é necessário classificá-lo como agente com aprendizagem: a Sprint 1 usa custos e regras explícitos e não treina um modelo.

### 1.4 Métrica perversa

“Quanto mais alertas por hora, melhor” parece uma medida de produtividade, mas incentiva repetir alertas em vez de encontrar novos problemas. Por exemplo, (0,1) é transitável e fica ao lado do portão; supondo ali uma leitura positiva, o agente poderia permanecer ou retornar ao mesmo ponto e reenviar o alerta, evitando a inspeção do restante do pomar. A leitura positiva nesse ponto é um **exemplo hipotético**, não uma infestação medida.

Correção: contar **talhões distintos com infestação confirmada por missão**, deduplicar alertas por talhão/janela temporal, acompanhar cobertura de talhões e penalizar horas gastas com falsos alertas. Atingir a coleta e respeitar 360 minutos são restrições. Assim, repetir o mesmo alerta não aumenta a pontuação.

## Parte 2 — Formulação e busca cega

### 2.1 Cinco componentes e tamanho do espaço

1. **Estado inicial:** posição (0,0).
2. **Ações:** Norte, Sul, Oeste e Leste, somente quando a coordenada de destino está dentro da grade e não contém `#`.
3. **Modelo de transição:** aplicar o deslocamento correspondente à posição atual; o mapa permanece fixo nesta busca.
4. **Teste de objetivo:** posição igual a (11,11).
5. **Custo do caminho:** soma de 1 por entrada em `.` e 4 por entrada em `~`, excluindo o início.

Há **144 posições**, das quais **29 são bloqueadas**. Portanto, o espaço de posições transitáveis tem **115 estados**; uma travessia a partir do portão confirmou que todos os 115 são alcançáveis. Um nó de busca pode representar um caminho diferente para um estado já conhecido, por isso estado e nó não são sinônimos. Não incluí bateria ou histórico de inspeções neste estado de navegação; isso pertence à modelagem da Parte 3.4.

### 2.2 Resultados da busca cega

| Estratégia | Custo (u.c.) | Passos | Nós expandidos | Fronteira máx. (entradas) | Ótima em custo? |
|---|---:|---:|---:|---:|---|
| BFS | 46 | 22 | 114 | 12 | Não |
| DFS | 131 | 62 | 81 | 63 | Não |
| UCS | 36 | 24 | 112 | 16 | Sim |

Fonte: [resultados.csv](resultados/resultados.csv); rotas em [resumo.json](resultados/resumo.json).

### 2.3 Por que BFS não está errada?

BFS minimiza o número de arestas quando usa fila FIFO. Sua rota tem **22 passos**, igual ao limite inferior Manhattan entre os cantos, mas custa **46**. UCS faz **24 passos** e custa **36**. Dois passos adicionais compensaram a passagem por terrenos mais baratos. A hipótese violada é a de **custo uniforme das ações**, necessária para transformar optimalidade em profundidade da BFS em optimalidade de custo. Aqui entrar em um talhão pode custar 1 ou 4.

### 2.4 Escalabilidade: falha efetivamente observada

Comando separado: `python src/escalabilidade.py 24114036`. Cada par tamanho/algoritmo foi executado em processo novo. O tempo de geração foi separado do tempo de busca; o processo tem limite de 60 segundos para a busca. Nenhum limite de recursão foi aumentado.

| n | Estratégia | Estado | Expansões | Fronteira/pilha máx. | Tempo de busca (s, aprox.) |
|---:|---|---|---:|---:|---:|
| 12 | BFS | Concluiu | 114 | 12 | 0,000259 |
| 12 | DFS | Concluiu | 81 | 63 | 0,000198 |
| 12 | UCS | Concluiu | 112 | 16 | 0,000489 |
| 40 | BFS | Concluiu | 1294 | 38 | 0,001818 |
| 40 | DFS | Concluiu | 1035 | 707 | 0,001741 |
| 40 | UCS | Concluiu | 1292 | 53 | 0,002935 |
| 100 | BFS | Concluiu | 8030 | 101 | 0,012027 |
| 100 | DFS | **RecursionError** | 1443 | **993 quadros registrados** | 0,003230 |
| 100 | UCS | Concluiu | 8023 | 169 | 0,019017 |

Fonte: [escalabilidade.json](resultados/escalabilidade.json). Ambiente: CPython 3.12 no Windows, limite de recursão **1000**. As chamadas externas à função recursiva também usam quadros, por isso a falha aparece com 993 níveis registrados, não exatamente 1000. Esta é a **primeira falha nos tamanhos ensaiados**, não a afirmação de que 100 é o menor n possível de falha.

Na apresentação clássica de busca em árvore, BFS usa O(b^d) espaço e DFS O(bm), onde b é ramificação, d a profundidade da solução mais rasa e m a profundidade máxima. Aqui b≤4. Em n=40 a pilha DFS já chegou a 707 entradas; em n=100 alcançou o limite concreto de chamadas. A parte da pilha cresce com a profundidade, mas **esta implementação em grafo também mantém visitados e pais O(V)**. Como E≤4V, BFS/DFS com visitados têm trabalho O(V+E), além da reconstrução; UCS com heap tem O((V+E) log V) neste grafo de grau limitado. Não seria correto usar 4^198 como previsão de estados efetivamente visitados na grade 100×100: visitados impedem a enumeração repetida de caminhos. Uma DFS iterativa removeria o limite da pilha Python, não os limites de memória da busca.

## Parte 3 — Busca informada

### 3.1 Três heurísticas

| Heurística | Custo (u.c.) | Nós expandidos | Admissível? |
|---|---:|---:|---|
| h1=0 | 36 | 112 | Sim: 0≤h* para custos não negativos. |
| h2=Manhattan | 36 | 62 | Sim: cada passo custa no mínimo 1 e reduz a distância no máximo em 1. |
| h3=4×Manhattan | 51 | 31 | Não: (11,10)→(11,11) tem h3=4 e custo real 1. |

h1 reproduziu UCS também em passos e fronteira. h2 poupou **50 expansões (44,64%)** relativamente ao UCS, sem alterar o custo.

### 3.2 Prova e contraexemplo concretos

Se D=|i−11|+|j−11|, qualquer rota ortogonal até o objetivo precisa de pelo menos D passos. Cada passo custa pelo menos c_min=1. Assim, h*(i,j)≥D×1=h2(i,j). Obstáculos podem aumentar o caminho real, mas não diminuir esse limite inferior. Além disso, h2 é consistente: para uma aresta n→n', h2(n)≤1+h2(n')≤c(n,n')+h2(n').

No próprio pomar, (11,10) contém `~` e (11,11) contém `.`. O custo é **de entrada no destino**: basta um passo para entrar em (11,11), custando 1. Portanto, h3(11,10)=4×1=**4 > 1=h***. O fato de a origem estar encharcada não acrescenta custo a esse caminho. A rota e os valores estão em `contraexemplo_h3` no resumo.

### 3.3 Troca entre custo e esforço de busca

h3 devolveu custo 51 contra 36 do UCS. A perda é:

`(51 − 36) / 36 × 100 = 41,6667%`.

Foram poupadas **112−31=81 expansões** em relação ao UCS (72,32%), ou 31 expansões em relação a h2. Isso mede trabalho de busca, **não prova a mesma redução percentual de tempo**, pois cada estratégia tem despesas diferentes. Na matrícula fictícia, h3 chegou ao ótimo 34; esse acerto isolado não prova admissibilidade, que exige h(n)≤h*(n) para todo estado relevante.

Uma condição de negócio verificável seria: em replanejamento emergencial, só admitir o método sem garantia de ótimo se medições em cenários representativos mostrarem **p95 de latência ≤100 ms**, enquanto o método ótimo viola esse prazo, e o acréscimo de custo medido ficar abaixo de **10%** do ótimo. São critérios propostos, não um SLA comprovado por este ensaio. A nossa h3, com perda de 41,67%, **não atende** ao limite de custo proposto; para este pomar a recomendação é h2.

### 3.4 Busca local: escolher K=15 talhões

**Hipóteses explícitas.** O enunciado não dá risco por coordenada nem velocidade do robô. Para ter uma função executável, cada um dos **113 candidatos** (115 alcançáveis menos portão/coleta) recebe benefício sintético inteiro de 1 a 100, por gerador independente `Random(114036+2026)` em ordem lexicográfica. Benefício não representa infestação observada. Adoto 12 min/inspeção e 1 min/unidade de custo de movimento. Inspecionar todos os 113 candidatos exigiria **1356 min só de inspeção**, acima de 360 min.

- **Estado:** conjunto de 15 coordenadas distintas alcançáveis, representado por tupla ordenada.
- **Vizinhança:** retirar uma coordenada e inserir uma das não escolhidas: 15×98=**1470 vizinhos** por estado.
- **Roteiro:** sair do portão, escolher repetidamente a inspeção não visitada mais próxima pelo custo real de caminho, desempatar por coordenada e terminar na coleta. Dijkstra pré-calcula os custos direcionados: o custo de entrar em terreno torna a distância potencialmente assimétrica. O roteiro por vizinho mais próximo é determinístico, mas **não é garantia de roteiro ótimo**. Passar por outro talhão não equivale a realizar a inspeção de 12 minutos nele.
- **Tempo:** T=C_mov+12×15=C_mov+180 minutos.
- **Objetivo a maximizar:** F=Σbenefício−0,5×C_mov−1000×max(0,T−360), em pontos. Os coeficientes convertem custo/violação em pontos; são opções de modelagem, não preços da cooperativa.
- **Viabilidade:** T≤360. O programa informa tempo e violação separadamente; uma boa pontuação não oculta inviabilidade.

**Subida de encosta:** melhor melhoria das trocas examinadas. **Têmpera:** uma troca aleatória por avaliação, aceita melhoria e aceita piora Δ com probabilidade exp(Δ/T_temp); temperatura geométrica de 50 até 0,05. A temperatura é parâmetro da otimização, não temperatura física do pomar. Guarda-se a melhor solução visitada.

**Comparação:** 30 pares de execuções, sementes 24114036 até 24114065, mesmo conjunto inicial em cada par e teto de **3000 avaliações de vizinhos** para ambos, além da avaliação inicial. A subida faz duas vizinhanças completas e parte da terceira: todos os seus resultados terminaram por orçamento, não por máximo local provado. Essa limitação importa: a vantagem observada da têmpera inclui a exploração de mais mudanças aceitas por avaliação, e não demonstra que toda subida de encosta seja inferior. O estado inicial usa fluxo aleatório separado do fluxo da têmpera.

| Método | Execuções | Média F (pontos) | Desvio amostral F (pontos) | Melhor F | Planos viáveis |
|---|---:|---:|---:|---:|---:|
| Subida de encosta | 30 | 889,1000 | 85,9636 | 1036,5 | 30/30 |
| Têmpera simulada | 30 | 1315,9000 | 3,4225 | 1317,5 | 30/30 |

Desvio amostral usa denominador 29. Não é desvio de tempos de execução. Resultados individuais:

| Execução | Subida F | Têmpera F | Pioras aceitas pela têmpera |
|---:|---:|---:|---:|
|1|874,5|1314,5|167|
|2|990,5|1300,5|181|
|3|1036,5|1310,0|193|
|4|750,5|1315,5|171|
|5|818,0|1317,0|167|
|6|893,5|1317,5|183|
|7|856,0|1317,0|175|
|8|997,5|1317,5|198|
|9|1015,5|1317,5|167|
|10|793,0|1317,5|165|
|11|985,5|1317,5|179|
|12|962,0|1317,5|173|
|13|874,5|1317,5|164|
|14|742,5|1317,0|156|
|15|944,0|1317,5|195|
|16|891,5|1317,5|160|
|17|897,0|1317,5|174|
|18|901,0|1317,5|168|
|19|916,5|1315,5|186|
|20|819,0|1313,5|152|
|21|1023,0|1317,5|174|
|22|793,5|1317,5|158|
|23|765,0|1317,5|177|
|24|894,0|1314,0|190|
|25|980,0|1313,5|166|
|26|882,5|1317,0|170|
|27|797,5|1314,5|163|
|28|773,5|1317,5|200|
|29|931,0|1317,5|173|
|30|874,0|1317,5|160|

**Onde aceitar piora aparece de fato:** execução 1 começa em F=630,5. Passos 1–3 aceitam −4,5, −11,5 e −1, chegando a 613,5. No passo 4 chega a 636. No passo 5 aceita −41, cai a 595, e no passo 7 alcança 640,5. Termina com melhor F=1314,5, contra 874,5 da subida do mesmo início. Aceitar descidas permite atravessar regiões que uma estratégia monotônica recusaria; isso explica o mecanismo discutido em busca local. O rastro demonstra descida seguida de recuperação, **não prova causalmente que cada descida foi necessária**, nem garante ótimo global com este resfriamento finito.

Fontes: [60 resultados](resultados/busca_local.csv), [rastro legível da execução 1](resultados/tempera_execucao_1.json) e [rastros completos comprimidos](resultados/busca_local_tracos.json.gz). Soluções e roteiros individuais estão no resumo.

### Bônus — contraexemplo DFS construído à mão

Construção 5×5: criar estrada barata no topo e na borda direita; preencher o interior e a borda esquerda com solo caro. Como a DFS prefere Sul antes de Leste, ela desce e serpenteia antes de alcançar a saída.

```
. . . . .
~ ~ ~ ~ .
~ ~ ~ ~ .
~ ~ ~ ~ .
~ ~ ~ ~ .
```

Rota DFS:
`(0,0)→(1,0)→(2,0)→(3,0)→(4,0)→(4,1)→(3,1)→(2,1)→(1,1)→(0,1)→(0,2)→(1,2)→(2,2)→(3,2)→(4,2)→(4,3)→(3,3)→(2,3)→(1,3)→(0,3)→(0,4)→(1,4)→(2,4)→(3,4)→(4,4)`.

Rota ótima:
`(0,0)→(0,1)→(0,2)→(0,3)→(0,4)→(1,4)→(2,4)→(3,4)→(4,4)`.

DFS entra em 16 terrenos caros e 8 baratos: **16×4+8=72**. A ótima custa **8**, exatamente o limite Manhattan, com todos os passos de custo 1. Logo **72>2×8** (é nove vezes o ótimo). A construção decorre da ordem de exploração; não foi uma busca aleatória por sementes favoráveis. Código e evidência: [bonus_dfs.json](resultados/bonus_dfs.json).

## Parte 4 — Regras e incerteza

Parâmetros retornados por `parametros_sensor(24114036)`:

| Parâmetro | Valor |
|---|---:|
| Prevalência | 0,0313 = 3,13% |
| Sensibilidade | 0,99 = 99% |
| Taxa de falso positivo | 0,05 = 5% |
| Talhões por semana | 2000 |

### 4.1 Mini sistema especialista

As regras são de triagem ilustrativa, não recomendação agronômica validada:

1. R1: SE sensor_positivo ENTÃO suspeita.
2. R2: SE armadilha_positiva ENTÃO suspeita.
3. R3: SE suspeita E umidade_alta ENTÃO risco_alto.
4. R4: SE risco_alto E intervalo_maior_14 ENTÃO inspecionar_prioridade_alta.
5. R5: SE suspeita E intervalo_ate_14 ENTÃO inspecionar_prioridade_normal.
6. R6: SE inspecionar_prioridade_alta ENTÃO solicitar_agronomo.
7. R7: SE inspecionar_prioridade_normal ENTÃO solicitar_agronomo.

`intervalo_maior_14` significa mais de 14 dias desde a pulverização; `intervalo_ate_14` cobre até 14 dias. Fatos contraditórios nesses dois intervalos são rejeitados.

O encadeamento para trás começa na conclusão desejada, procura regras que a concluem e tenta provar todas as premissas. Se um ramo falha, tenta outra regra. Detecta ciclos por caminho de prova. A resposta inclui árvore de justificativa e rastro das tentativas, inclusive das fracassadas. Não provar uma inspeção significa **falta de derivação**, não certeza de que o talhão está saudável.

### 4.2 Caso que quebra a base e correção

Caso legítimo: sensor negativo, armadilha negativa, lesões visíveis, umidade alta e mais de 14 dias desde a pulverização. Lesões precisam de inspeção mesmo quando os dois instrumentos não alertaram. Antes, R1 e R2 não estabelecem suspeita; a triagem deixa esse caso sem prioridade.

Correção, mantendo a base final em **8 regras**: **R8: SE lesoes_visiveis ENTÃO suspeita**. Ela acrescenta uma fonte de suspeita e reaproveita R3/R4. Não conclui “sem praga”, não ordena aplicação de produto e não contradiz prioridades: alta e normal dependem de intervalos mutuamente exclusivos. Ainda existem casos não cobertos, como certas suspeitas sem umidade alta e com intervalo longo; a base é propositalmente pequena e isso está declarado.

Traço resumido antes:
```
OBJETIVO inspecionar_prioridade_alta
  R4 precisa de risco_alto e intervalo_maior_14
    R3 precisa de suspeita e umidade_alta
      R1: sensor_positivo NÃO PROVADO
      R2: armadilha_positiva NÃO PROVADO
    suspeita NÃO PROVADO
  risco_alto NÃO PROVADO
inspecionar_prioridade_alta NÃO PROVADO
```
Depois:
```
OBJETIVO inspecionar_prioridade_alta
  R4 -> R3 -> suspeita
    R1 e R2 falham
    R8: lesoes_visiveis é FATO -> suspeita
  umidade_alta é FATO -> risco_alto por R3
intervalo_maior_14 é FATO -> inspecionar_prioridade_alta por R4
```
O [traço integral emitido pelo programa](resultados/especialista_tracos.txt) preserva cada tentativa; a árvore identifica **R8→R3→R4**.

### 4.3 Bayes com os parâmetros da matrícula

Defina I=infestado e +=sensor positivo. P(I)=0,0313, P(+|I)=0,99 e P(+|¬I)=0,05.

**(a)**

`P(I|+) = [P(+|I)P(I)] / [P(+|I)P(I)+P(+|¬I)P(¬I)]`

`= (0,99×0,0313) / (0,99×0,0313 + 0,05×0,9687)`

`= 0,030987 / 0,079422 = 0,39015638 ≈ 39,02%.`

**(b)** A cada 100 alertas do meu sistema, cerca de **61 serão falsos**: 100×(1−0,39015638)=60,9844. Esse “meu sistema” identifica o projeto, não implica treinamento de um detector real.

**(c)** Falsos alertas esperados por semana:

`2000×(1−0,0313)×0,05 = 96,87`.

Tempo esperado: `96,87×12/60 = 19,374 horas/semana` (aproximadamente 19h22min). São expectativas, por isso podem ser fracionárias. Para conferir a conta: verdadeiros positivos esperados=2000×0,0313×0,99=61,974; total de alertas=158,844; 61,974/158,844=39,0156%.

**(d)** Com sensibilidade 99,9% e mesmo falso positivo:

`VPP_novo = (0,999×0,0313) / (0,999×0,0313+0,05×0,9687)`

`= 0,0312687 / 0,0797037 = 0,39231177 ≈ 39,23%.`

O VPP aumenta apenas **0,2155 ponto percentual**. A melhoria é real, porém pequena; os **96,87 falsos alertas semanais permanecem**, pois prevalência, população e taxa de falso positivo não mudaram. O parâmetro prioritário é a **taxa de falso positivo**, por calibração e/ou confirmação independente, verificando em validação como isso afeta a sensibilidade. Não prometo melhorar um parâmetro sem medir a troca com o outro.

### 4.4 Decisão que deve ser regra explícita

**SE não há autorização registrada de agrônomo responsável para o talhão, produto e momento ENTÃO bloquear a ordem de intervenção química.** Essa restrição deve ficar fora de um modelo aprendido: é preciso demonstrar quem autorizou o quê e quando, reconstruir a decisão e atribuir responsabilidade. Mesmo que um classificador acerte com frequência, ele não substitui uma autorização auditável. No protótipo, a saída já se limita a solicitar inspeção humana.

## Parte 5 — Auditoria do laudo do fornecedor

### Afirmação 1 — “A* com Manhattan ×4 sempre entrega a mais barata”

**Incorreta.** A garantia de A* depende da heurística e do tratamento de estados, não apenas do nome do algoritmo. Na nossa semente h3 devolve **51**, enquanto UCS comprova **36**. Em (11,10), h3=4 supera h*=1. A reabertura não corrige a falta de admissibilidade: ela trata melhorias em estados, não transforma uma estimativa excessiva em limite inferior.

### Afirmação 2 — “BFS→A* caiu 38%; a heurística melhora a qualidade”

**Parcialmente correta.** A* pode devolver uma rota mais barata que BFS neste domínio de custos não uniformes, mas essa comparação não isola o efeito da heurística. Aqui BFS custa **46**, A* h2 **36**: queda de **21,7391%**, e não 38% na nossa instância. UCS e A* h1 também custam **36**, sem orientação heurística informativa. O efeito demonstrado de h2 frente ao UCS é reduzir **112 para 62 expansões**, preservando o mesmo custo ótimo. Os 38% poderiam ser um dado de outra instância, mas não provam a causalidade alegada.

### Afirmação 3 — “Sensibilidade de 99% significa 99% de infestados entre os alertas”

**Incorreta.** Confunde P(+|I) com P(I|+). Com os **99% de sensibilidade**, **3,13% de prevalência** e **5% de falsos positivos** gerados, apenas **39,0156%** dos alertas são de infestados em expectativa. São aproximadamente **61 falsos a cada 100 alertas**. A taxa-base precisa entrar na análise.

### Afirmação 4 — “Dois positivos dão confiança acima de 99%”

**Incorreta como garantia.** Mesmo assumindo independência condicional dos testes dado I e dado ¬I:

`P(I|++) = (0,99²×0,0313)/(0,99²×0,0313+0,05²×0,9687)`

`= 0,03067713/0,03309888 = 92,6833%`, ainda **abaixo de 99%**.

Repetir o mesmo sensor no mesmo talhão pode repetir erro de iluminação, sujeira ou padrão visual. Com erros perfeitamente correlacionados, o segundo teste não acrescenta informação e o VPP continua **39,0156%**. Precisamos medir dependência ou usar confirmação independente; não se deve elevar probabilidades ao quadrado sem justificar a hipótese.

### Afirmação 5 — “DFS usa muito menos memória; ambiente estático/observável basta”

**Parcialmente correta.** DFS em árvore pode ter vantagem de espaço frente à BFS, mas isso não garante rota adequada nem menor uso de memória em toda implementação/instância. Aqui a pilha DFS atingiu **63**, contra fronteira BFS **12** e UCS **16**, além dos mapas auxiliares. A rota DFS custa **131**, contra ótimo **36**, e a versão recursiva falhou em **n=100**. Estaticidade e observabilidade não garantem optimalidade de custo. DFS pode servir se qualquer caminho viável bastar e os limites forem medidos, mas o argumento do laudo não atende ao objetivo econômico apresentado.

### Recomendação à diretoria (até oito linhas)

**Recusar a proposta na forma atual.** O laudo promete ótimo com uma configuração que produziu custo 51 em vez de 36 e confunde sensibilidade com confiabilidade dos alertas.  
Reconsiderar mediante teste reproduzível com A* admissível/UCS, custos e latências registrados, calibração do detector e evidência de dependência entre testes.  
Exigir ainda teto contratual de horas desperdiçadas com falsos alertas e autorização humana auditável para intervenções.  
As condições devem ser comprovadas com sementes e dados de validação que não tenham sido escolhidos pelo fornecedor.

## Parte 6 e conferência final

O [ANEXO_IA.md](ANEXO_IA.md) contém ferramentas, dois pares reais de prompts/respostas, um erro efetivo do assistente e a conclusão apoiada pela execução. O projeto foi clonado e executado em outro computador. A revisão pessoal do anexo e a assinatura cabem ao autor.
