# Caatinga.AI Sprint 1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Entregar uma implementação reproduzível da atividade, com resultados medidos da matrícula 24114036, explicações verificáveis e evidências de entrega.

**Architecture:** Módulos Python independentes para buscas globais, busca local, regras e Bayes. Um orquestrador escreve resultados estruturados e um gráfico; o relatório utiliza esses mesmos resultados. Ensaios demorados ficam em um comando separado documentado.

**Tech Stack:** Python 3.12 no desenvolvimento, Python >=3.10 para execução, biblioteca padrão, Matplotlib para o gráfico, unittest para testes. ReportLab do ambiente local apenas para preparar o PDF de entrega, sem virar dependência do programa do estudante.

**Spec:** `docs/superpowers/specs/2026-09-25-caatinga-ai-sprint1-design.md`.

## Global Constraints

- Autor: ANTONIO GOMES SOUZA NETO; matrícula apresentada 241.14.036; inteiro 24114036; resto 114036.
- `src/gerador_pomar.py` preserva o código fornecido no PDF.
- Comando obrigatório: `python src/main.py 24114036`.
- CSV obrigatório: `estrategia,heuristica,custo,passos,nos_expandidos,fronteira_max,tempo_ms`.
- O projeto funciona com outras sementes; não codificar os resultados da matrícula como saídas do algoritmo.
- Busca local: K=15, 30 execuções de cada algoritmo, bateria de 360 minutos.
- Repositório público `caatinga-ai-sprint1`, no mínimo oito commits de etapas reais.
- Anexo de IA registra prompts, respostas e erro reais, sem simular revisão pessoal do autor.
- Trabalho individual, teste externo e assinatura serão tratados conforme evidências e aceite do professor.
- Antes de cada commit: `git status`, `git diff`, `git log --oneline -10`; no repositório sem commits, registrar que o histórico ainda não existe. Conferir também o diff preparado para o commit. Sem alterar configuração Git.

## Review Focus

1. Semente diferente da principal: a execução precisa regenerar o pomar, sensor e resultados de forma consistente (Tarefas 1 e 7).
2. Grade sem caminho e início igual ao objetivo: término finito e resposta explícita, sem reconstrução inválida (Tarefa 2).
3. Heurística admissível inconsistente: A* precisa reabrir estados e continuar correto (Tarefa 3).
4. Inviabilidade de inspecionar 15 talhões na bateria: registrar violação e não apresentar o plano como viável (Tarefa 4).
5. Falta de fato no especialista e repetição correlacionada de sensores: não transformar desconhecimento em verdade nem assumir independência implicitamente (Tarefas 5 e 6).

## Estrutura e interfaces

Todos os módulos podem ser importados como `src.<modulo>` pelos testes, usando `src/__init__.py`. `main.py` suporta a execução pelo caminho requerido. Arquivos de resultados são relativos à raiz do projeto, não ao diretório corrente.

```python
# src/buscas.py
Coord = tuple[int, int]
Grade = list[list[str]]
@dataclass
class ResultadoBusca:
    rota: list[Coord]
    custo: int | None
    passos: int | None
    nos_expandidos: int
    fronteira_max: int
    tempo_ms: float
    reaberturas: int = 0

def vizinhos(grade: Grade, estado: Coord): ...  # iterador de Coord
def bfs(grade: Grade, inicio=(0, 0), objetivo=None) -> ResultadoBusca: ...
def dfs(grade: Grade, inicio=(0, 0), objetivo=None) -> ResultadoBusca: ...
def ucs(grade: Grade, inicio=(0, 0), objetivo=None) -> ResultadoBusca: ...
def astar(grade: Grade, heuristica, inicio=(0, 0), objetivo=None) -> ResultadoBusca: ...
def manhattan(estado: Coord, objetivo: Coord) -> int: ...

# src/busca_local.py: resultados são dicionários serializáveis
def criar_modelo(grade: Grade, matricula: int, bateria_min=360) -> dict: ...
def avaliar(modelo: dict, selecionados: tuple[Coord, ...]) -> dict: ...
def subida_encosta(modelo: dict, inicial: tuple[Coord, ...], semente: int,
                   max_avaliacoes=3000) -> dict: ...
def tempera_simulada(modelo: dict, inicial: tuple[Coord, ...], semente: int,
                     max_avaliacoes=3000) -> dict: ...
def experimentar(grade: Grade, matricula: int, repeticoes=30) -> dict: ...

# src/especialista.py
@dataclass(frozen=True)
class Regra:
    nome: str
    premissas: tuple[str, ...]
    conclusao: str
def provar(objetivo: str, fatos: set[str], regras: list[Regra]) -> dict: ...
def demonstracao() -> dict: ...

# src/bayes.py
def calcular(parametros: dict) -> dict: ...
```

As reticências nas assinaturas acima indicam contratos de interface, não implementações. Os passos abaixo definem os algoritmos e os testes que devem realizá-los.

## Tarefa 1 — contrato do gerador e base reproduzível

**Arquivos:** `src/gerador_pomar.py`, `src/__init__.py`, `tests/test_gerador.py`, `.gitignore`, `requirements.txt`, `resultados/contrato_gerador.json`.

**Consome:** texto da página 2 do PDF local. **Produz:** funções originais `gerar_pomar(matricula, n=12)` e `parametros_sensor(matricula)`.

- [ ] Consultar Context7 para Matplotlib (backend sem janela e `savefig`) e Git/GitHub CLI conforme as operações necessárias; verificar autenticação sem imprimir tokens, conta de destino e existência de repositório remoto.
- [ ] Conferir raiz, iniciar repositório local e fazer commit da especificação/plano com identidade já configurada. Se a identidade não estiver configurada, solicitar os dados necessários sem inventar identidade.
- [ ] Escrever e executar testes de contrato antes da transcrição do gerador:

```python
from src.gerador_pomar import gerar_pomar, parametros_sensor

def verificar_gerador():
    a = gerar_pomar(24114036)
    assert len(a) == 12 and all(len(linha) == 12 for linha in a)
    assert a[0][0] == a[-1][-1] == '.'
    assert a == gerar_pomar(114036)
    assert a != gerar_pomar(20231045)
    assert parametros_sensor(24114036) == parametros_sensor(114036)
```

- [ ] Copiar o gerador da página 2, corrigindo apenas quebras de diagramação. Guardar SHA-256 do arquivo e conferência textual do trecho-fonte extraído para detectar mudanças posteriores.
- [ ] Rodar `python -m unittest discover -s tests -v` e `python src/gerador_pomar.py 24114036`. Testar também 20231045.
- [ ] Fixar a versão do Matplotlib que realmente foi instalada/testada; `.gitignore` exclui `.venv/`, `venv/`, `__pycache__/`, `*.pyc` e caches de testes.
- [ ] Commit: `preserva gerador do enunciado e verifica sementes`.

## Tarefa 2 — BFS, DFS, UCS e aferição independente

**Arquivos:** `src/buscas.py`, `tests/test_buscas.py`, `tests/oraculo.py`, `resultados/afericao.json`.

**Consome:** gerador e `CUSTO`. **Produz:** `ResultadoBusca`, `vizinhos`, `bfs`, `dfs`, `ucs`, `manhattan`.

- [ ] Escrever testes das propriedades do resultado e executá-los antes de implementar:

```python
def conferir_rota(g, resultado, inicio, objetivo):
    assert resultado.rota[0] == inicio
    assert resultado.rota[-1] == objetivo
    assert resultado.passos == len(resultado.rota) - 1
    assert resultado.custo == sum({'.': 1, '~': 4}[g[i][j]]
                                  for i, j in resultado.rota[1:])
    assert all(abs(a[0]-b[0])+abs(a[1]-b[1]) == 1
               for a, b in zip(resultado.rota, resultado.rota[1:]))

def casos_minimos(algoritmo):
    assert algoritmo([['.']]).custo == 0
    assert algoritmo([['.']]).passos == 0
    assert algoritmo([list('.#'), list('#.')]).custo is None
    assert algoritmo([list('.#'), list('#.')]).rota == []
    assert algoritmo([list('.~'), list('..')]).custo in (2, 5)
```

- [ ] Definir ordem Norte, Sul, Oeste, Leste e desempate FIFO por contador crescente para prioridades iguais. Testar essa convenção com a referência; se uma outra ordem for necessária para reproduzir a BFS, registrar a alteração antes dos experimentos finais.
- [ ] BFS: `deque`, visitados na descoberta, pai fixado na primeira descoberta. DFS: recursão explícita com visitados globais e pilha de quadros; fronteira é número de quadros ativos, incluindo o inicial e o do objetivo. Não elevar o limite de recursão. UCS: heap com `(g, sequencia, estado)`, relaxamento estrito, entradas obsoletas descartadas e pais atualizados ao melhorar.
- [ ] Contar expansões imediatamente antes de percorrer sucessores, excluindo objetivo; atualizar máximo da fronteira após cada inserção. Em falha por recursão preservar profundidade máxima e quantidade de expansões em uma exceção com dados.
- [ ] Implementar oráculo Bellman–Ford de teste: inicializar distâncias com infinito, distância inicial zero, relaxar todas as arestas transitáveis até não melhorar ou atingir V−1 passagens. Comparar UCS em grades pequenas e nas duas matrículas, independentemente do heap.
- [ ] Registrar resultados obtidos para 20231045 versus os esperados pelo PDF (34/55/22). Se houver divergência, conferir fonte, todos os custos e ordens possíveis de vizinhos antes de concluir que a referência é inconsistente.
- [ ] Executar `python -m unittest discover -s tests -v` e salvar rotas e contagens da aferição.
- [ ] Commit: `implementa BFS DFS UCS com contadores e afericao`.

## Tarefa 3 — A* e contraexemplo construído

**Arquivos:** `src/buscas.py`, `tests/test_astar.py`, `src/experimentos.py` (experimentos globais e bônus), `resultados/bonus_dfs.json`.

**Consome:** funções da Tarefa 2. **Produz:** `astar`, `comparar_buscas(grade) -> list[dict]`, `bonus_dfs() -> dict`.

- [ ] Testar que h=0 reproduz custo, passos, expansões e fronteira do UCS; Manhattan tem o mesmo custo ótimo nas sementes 0, 1, 114036 e 20231045.
- [ ] Construir testes de reabertura usando h admissível inconsistente: calcular h* pelo oráculo para cada estado, atribuir h=0 a parte dos estados e h=h* aos demais, e testar todos os padrões numa grade pequena com duas rotas de custos distintos. Confirmar reabertura em pelo menos um caso, preservando o caso concreto como regressão.
- [ ] A*: heap `(g+h, sequencia, g, estado)`, mapa do melhor g e mapa do g expandido. Uma melhora em estado anteriormente expandido volta à fila; entradas cujo g diverge do melhor g são obsoletas. Objetivo termina apenas em retirada válida.
- [ ] Executar h1, h2, h3 na matrícula principal. Procurar um estado transitável com `4*manhattan(estado, objetivo) > ucs(grade, estado, objetivo).custo`, registrar estado/objetivo, rota e os dois valores.
- [ ] Construir grade 5×5 com linha superior e coluna direita de `.`; demais células `~`. Com Norte/Sul/Oeste/Leste, a DFS desce e serpenteia, enquanto o ótimo percorre o topo/direita. Verificar por código `custo_dfs > 2*custo_ucs`, ajustar a construção manualmente se a ordem final for outra e explicar o motivo geométrico.
- [ ] Testar `bonus_dfs()` e recalcular os custos das duas rotas a partir da grade.
- [ ] Commit: `implementa A estrela com reabertura e contraexemplo DFS`.

## Tarefa 4 — busca local com comparação pareada

**Arquivos:** `src/busca_local.py`, `tests/test_busca_local.py`, `resultados/busca_local.csv`, `resultados/busca_local_resumo.json`, `resultados/tempera_tracos.json`.

**Consome:** gerador, `ucs`, `vizinhos`. **Produz:** as cinco funções de busca local descritas nas interfaces.

- [ ] Fixar hipóteses antes de medir: benefício sintético inteiro de 1 a 100 por talhão, gerado com `Random((matricula % 1_000_000)+2026)` em ordem lexicográfica; 12 minutos por inspeção; 1 minuto por unidade de custo de movimento; início no portão e término no ponto de coleta.
- [ ] Pré-calcular menores custos direcionados entre pontos alcançáveis usando Dijkstra para todas as origens. Respeitar assimetria do custo de entrada.
- [ ] Testar distância de movimento em `[list('.~.')]`: origem 0→1 custa 4, origem 1→0 custa 1. Testar que o mesmo conjunto em ordem diferente recebe a mesma avaliação.
- [ ] Representar seleção como tupla ordenada de 15 coordenadas distintas, excluindo início e objetivo. Ordenar a visita por vizinho mais próximo em custo real, desempate lexicográfico, e terminar no objetivo.
- [ ] Avaliação: `tempo_min = custo_movimento + 12*K`; `violacao = max(0, tempo_min-bateria_min)`; `valor = soma_beneficios - 0.5*custo_movimento - 1000*violacao`. Retornar também `viavel`, `tempo_min`, `beneficio`, `rota_visitas`, `selecionados` e `custo_movimento`.
- [ ] Testar conjunto inválido (repetidos, K diferente ou bloqueados) com `ValueError`; menos de 15 candidatos também produz erro claro. Com bateria zero, `viavel` deve ser falso e `violacao` positiva.
- [ ] Subida de encosta por melhor melhoria: avaliar trocas ordenadas, aplicar a de maior ganho estrito; terminar em máximo local ou limite de 3000 avaliações. Têmpera: proposta aleatória de troca, 3000 avaliações, temperatura geométrica de 50 a 0,05, aceitação `exp(delta/T)` para delta negativo e guarda da melhor solução.
- [ ] Mesmos 30 conjuntos iniciais para os dois métodos, sementes `matricula+indice`, guardar sementes e orçamento efetivamente gasto. Registrar por passo da têmpera delta, aceitação, valor corrente e melhor valor.
- [ ] Verificar determinismo com a mesma semente, tamanho/distinção das seleções e que melhor solução da têmpera nunca é pior que a inicial. Calcular média e `statistics.stdev`, máximo e número de planos viáveis.
- [ ] Executar 30+30 rodadas. Extrair evidência de piora aceita seguida de recuperação; relatar francamente o comparativo, mesmo sem vitória da têmpera.
- [ ] Commit: `modela bateria e compara buscas locais em 30 execucoes`.

## Tarefa 5 — encadeamento para trás e correção da base

**Arquivos:** `src/especialista.py`, `tests/test_especialista.py`, `resultados/especialista.json`, `resultados/especialista_tracos.txt`.

**Consome:** fatos simbólicos sintéticos explícitos. **Produz:** `Regra`, `provar`, `demonstracao`.

- [ ] Base inicial de sete regras: R1 sensor_positivo→suspeita; R2 armadilha_positiva→suspeita; R3 suspeita E umidade_alta→risco_alto; R4 risco_alto E intervalo_maior_14→inspecionar_prioridade_alta; R5 suspeita E intervalo_ate_14→inspecionar_prioridade_normal; R6 inspecionar_prioridade_alta→solicitar_agronomo; R7 inspecionar_prioridade_normal→solicitar_agronomo.
- [ ] Caso legítimo: sensor negativo, armadilha negativa, lesoes_visiveis, umidade_alta e intervalo_maior_14. Base inicial não prova nenhuma inspeção, embora lesões exijam avaliação. R8 lesoes_visiveis→suspeita corrige a omissão sem concluir aplicação de produto.
- [ ] Testar antes/depois: objetivo `inspecionar_prioridade_alta` deve falhar antes e ser provado depois por R8→R3→R4. Testar base sem fatos, ciclo A→B/B→A e premissa desconhecida; término finito e ausência de prova.
- [ ] Implementar prova recursiva de objetivos com trilha local para ciclos, alternativas de regras e árvore de justificativas; regras de conjunção exigem todas as premissas. Não tratar falha de prova como negação comprovada.
- [ ] Emitir rastros legíveis com objetivo tentado, regra considerada, fatos usados e conclusão. Não compartilhar conjunto de ciclos entre ramos independentes.
- [ ] Testar ausência de inspeções alta/normal simultâneas sob fatos de intervalo mutuamente exclusivos. Recusar fatos contraditórios de intervalo na entrada da demonstração.
- [ ] Commit: `implementa especialista explicavel e corrige omissao por lesoes`.

## Tarefa 6 — probabilidades e repetição de testes

**Arquivos:** `src/bayes.py`, `tests/test_bayes.py`, `resultados/bayes.json`.

**Consome:** `parametros_sensor(matricula)`. **Produz:** `calcular(parametros)` com valores numéricos, sem arredondamento prematuro.

- [ ] Escrever teste manual: p=0,01, sensibilidade=0,99, fpr=0,05, N=1000. VPP=0,0099/0,0594=1/6; falsos/semana=49,5; horas=9,9.
- [ ] Implementar `vpp = s*p/(s*p+f*(1-p))`, `falsos_100 = 100*(1-vpp)`, `falsos_semana=N*f*(1-p)`, `horas_semana=falsos_semana*12/60` e cenário s=0,999.
- [ ] Calcular dois positivos sob independência condicional: `s*s*p/(s*s*p+f*f*(1-p))`; cenário de correlação perfeita mantém o VPP original. Repetir a análise com sensibilidade de 0,99 para auditar literalmente a frase do fornecedor.
- [ ] Validar probabilidades entre zero e um, N inteiro não negativo; quando P(positivo)=0, retornar VPP indefinido como `None`, não dividir por zero. Testar p=0, p=1 e s=f=0.
- [ ] Rodar com parâmetros da matrícula e guardar todos os valores e hipóteses em JSON.
- [ ] Commit: `calcula Bayes e audita repeticao de sensores`.

## Tarefa 7 — integração, gráfico e escalabilidade

**Arquivos:** `src/main.py`, `src/experimentos.py`, `src/escalabilidade.py`, `tests/test_integracao.py`, arquivos de `resultados/` exigidos e `resultados/escalabilidade.csv`.

**Consome:** todos os módulos. **Produz:** execução única reproduzível e artefatos obrigatórios.

- [ ] Implementar `argparse`, normalização de matrícula pontuada, validação de inteiro não negativo e argumento opcional `--saida` para testar em diretório temporário. Não substituir resultados de outras execuções sem o usuário escolher a mesma pasta.
- [ ] CSV usa `csv.DictWriter`, UTF-8 e cabeçalho exigido. Gráfico usa backend Agg, barras para BFS/DFS/UCS/A* h1/h2/h3, eixo y `Nós expandidos (quantidade)` e eixo x `Estratégia / heurística`.
- [ ] Gerar grade, rotas JSON, contagem de transitáveis/alcançáveis, resumo local, rastros do especialista e Bayes. O relatório estático identifica sua semente; executar outra semente não reescreve silenciosamente as conclusões textuais.
- [ ] Teste de integração com `subprocess.run([sys.executable, 'src/main.py', '24114036', '--saida', pasta_temporaria], check=True, timeout=180)`: três artefatos obrigatórios existem, CSV tem seis linhas de estratégias e PNG tem assinatura válida. Rodar outra semente em outra pasta; conferir grade e sensor contra gerador.
- [ ] Ensaio separado: `python src/escalabilidade.py 24114036`. Para n em 12,40,100,200,400,800,…, executar cada estratégia em processo novo. Medir separadamente geração e busca; monitorar busca com deadline de 60 segundos e registrar timeout real, RecursionError ou MemoryError. Terminar processo próprio após limite e registrar código de saída.
- [ ] Capturar ambiente, limite de recursão, n, estratégia, status, segundos, profundidade DFS e contadores disponíveis. Parar progressão após primeira falha e completar os outros algoritmos nesse n se viável.
- [ ] Verificar que o benchmark usa exatamente as funções entregues, não versões artificialmente enfraquecidas. Na análise, distinguir O(V+E), O(V), heap e profundidade das fórmulas O(b^d)/O(bm) de busca em árvore.
- [ ] Rodar suite completa, comando principal e benchmark; abrir gráfico via inspeção do arquivo e conferir rótulos pelo código/artefato, sem alegar inspeção visual inexistente.
- [ ] Commit: `integra experimentos grafico e medicao de escalabilidade`.

## Tarefa 8 — relatório e anexo rastreáveis

**Arquivos:** `README.md`, `RELATORIO.md`, `ANEXO_IA.md`, `docs/ARGUICAO.md`, `docs/evidencias_ia.md`.

**Consome:** resultados efetivamente executados e transcrições reais desta conversa. **Produz:** documentação completa e auditável.

- [ ] Parte 1: PEAS em tabela com unidades, seis dimensões com citações do PDF, observabilidade/estaticidade discutidas, agente baseado em utilidade justificado pela troca custo/benefício e métrica perversa de número de alertas produzidos. Localizar talhão concreto onde repetir alertas geraria incentivo ruim; corrigir com alertas únicos confirmados, cobertura e penalidade por falso positivo.
- [ ] Parte 2: cinco componentes, total de estados, três estratégias, explicação da hipótese de custos uniformes e resultado real do ensaio de falha com relação teórica correta.
- [ ] Parte 3: tabela de A*, provas, par concreto de superestimação, comparação quantitativa h3/UCS, condição de negócio proposta, modelo local completo, 60 resultados com resumo e evidência dos rastros. Inserir bônus DFS com grade e ambas as rotas.
- [ ] Parte 4: sete regras e oitava corretiva, antes/depois, quatro parâmetros e contas com substituições, regra de validação humana por auditabilidade.
- [ ] Parte 5: cinco vereditos com pelo menos uma evidência numérica cada; esclarecer que melhoria de custo BFS→A* não demonstra que a heurística melhora a qualidade em relação a UCS. Recomendação de até oito linhas.
- [ ] Parte 6: copiar integralmente dois pares reais de mensagem/resposta; registrar ferramentas realmente usadas. Selecionar erro real ocorrido, afirmação original e teste que o contradiz. Se não houver erro conceitual comprovado, apresentar a imprecisão real mais relevante com seu contexto, sem encenar falha.
- [ ] README segue exatamente a ordem 9.2 do PDF, com tabela direta e mapa dos arquivos. Limitações indicam autorização individual e teste externo pendentes, se ainda for o caso.
- [ ] Roteiro de arguição: comando para semente nova, significado de contadores, custo vs passos, reabertura, admissibilidade e Bayes. Perguntas acompanhadas de respostas curtas apoiadas no código.
- [ ] Conferir todos os números das tabelas com CSV/JSON, todas as referências de arquivos e hash do gerador; procurar conclusões contraditórias e afirmações de autoria/execução indevidas.
- [ ] Commit: `documenta resultados auditoria e uso real de IA`.

## Tarefa 9 — revisão final e entrega verificável

**Arquivos:** `docs/VERIFICACAO.md`, PDF fora do repositório em pasta de entrega, eventuais correções com testes de regressão.

**Consome:** projeto completo. **Produz:** URL pública verificada, hash final e PDF de uma página.

- [ ] Carregar habilidades de verificação e revisão aplicáveis; revisar todas as exigências do PDF com uma matriz requisito→arquivo→evidência. Revisão de segurança concentrada em argumentos de linha de comando, subprocessos, caminhos de saída e ausência de credenciais.
- [ ] Criar ambiente virtual limpo, instalar com `pip install -r requirements.txt`, executar testes e comando documentado. Registrar que isso ocorreu no mesmo PC.
- [ ] Fazer correções necessárias em commits próprios; garantir oito ou mais commits com conteúdo real, sem fabricar datas ou usuário adicional.
- [ ] Conferir status, diff, histórico, remoto e visibilidade desejada. Criar/publicar o repositório público solicitado via `gh`, somente se não existir; se existir, investigar o conteúdo antes de integrar.
- [ ] Acessar URL sem autenticação para comprovar leitura pública. Clonar em outro diretório e repetir comando para conferir que todos os arquivos necessários estão versionados.
- [ ] Gerar `entrega_24114036.pdf` com nome, matrícula, URL clicável, hash de sete caracteres, declaração original, campo de assinatura e checklist verdadeiro. Identificar como minuta enquanto faltar conferência externa/assinatura; não imitar assinatura nem alterar declaração para atestar evento não realizado.
- [ ] Usar PyMuPDF para conferir uma página, texto de identificação, link e hash corretos. Conferir PDF após qualquer correção.
- [ ] Entregar caminhos, URL e resumo das verificações; listar apenas pendências reais que dependem do estudante/professor. Não afirmar garantia de nota.

## Revisão do plano

Cobertura: T1 contrato e sementes; T2 Parte 2 e aferição; T3 Parte 3.1–3.3 e bônus; T4 Parte 3.4; T5 Parte 4.1–4.2; T6 Parte 4.3 e auditoria probabilística; T7 artefatos e escalabilidade; T8 Partes 1–6 e README; T9 requisitos 9–12 de entrega. As assinaturas utilizadas entre tarefas estão definidas na seção de interfaces. Os cinco riscos de Review Focus têm testes nas respectivas tarefas. Requisitos externos são distinguidos de conclusão técnica.
