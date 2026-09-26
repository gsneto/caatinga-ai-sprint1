# Verificação técnica — 25/09/2026

## Evidências conferidas

| Exigência | Arquivo / verificação |
|---|---|
| Gerador original | Comparação com texto extraído da página 2 do PDF, ignorando whitespace de diagramação; hash UTF-8/LF em `resultados/contrato_gerador.json`. |
| Matrícula | 24114036, resto 114036; grade e sensor conferidos com o módulo original. |
| Parte 1 | Seções 1.1–1.4 do relatório, PEAS com unidades e seis dimensões. |
| Busca cega | CSV, rotas, contadores e oráculo Bellman–Ford independente. |
| Aferição | BFS 55/22, UCS 34/111 expansões, A* h2 34/90 expansões. |
| Escalabilidade | DFS n=100, RecursionError, 993 quadros, limite 1000; resultados com fase e código de saída do processo. |
| A* e heurísticas | Custos 36/36/51; contraexemplo h3=4 contra custo real 1. |
| Busca local | 30+30 execuções, 60 soluções viáveis; estatísticas recalculadas e rastros disponíveis. |
| Bônus DFS | Construção 5×5, DFS 72 versus ótimo 8. |
| Especialista | 7 regras iniciais + R8, antes/depois e árvore de prova. |
| Bayes e auditoria | Cálculos conferidos, correlação distinguida de independência. |
| Anexo IA | Dois pares textuais da conversa e erro real de fixture registrado. |
| Gráfico | PNG 1600×800, rótulos/eixos conferidos por código e OCR local. |
| Testes | **26 testes passaram**, incluindo execução integrada com duas sementes em pastas temporárias. |

## Revisão independente

Uma revisão por agente com contexto separado conferiu o código e os documentos, executou a suíte original de 24 testes e ensaiou outras 30 sementes contra Bellman–Ford. Não encontrou divergências numéricas no relatório ou nas 60 linhas de busca local.

Encontrou dois problemas no supervisor de escalabilidade: morte abrupta do filho sem resposta interrompia a coleta, e o prazo era contado a partir da leitura da mensagem pelo pai, não do início informado pelo filho. Ambos foram reproduzidos em testes que falharam antes da correção. O supervisor agora registra encerramento/código de saída, compara duração real com o prazo e grava checkpoints a cada medição. **Suíte após correção: 26/26.** O benchmark foi executado novamente e os tempos do relatório foram atualizados.

Observação menor mantida: as transcrições da IA estão contextualizadas na conversa, mas o repositório não inclui uma exportação original com identificadores de mensagem para autenticação externa. Não foi inventado um identificador.

## Escopo da revisão de segurança

Entradas são argumentos locais: matrícula e pasta de saída. A matrícula é validada e vira inteiro; não chega a um interpretador de comandos. A pasta é escolhida pelo operador e recebe nomes de arquivos fixos; sobrescrita dos resultados é documentada. Processos do benchmark executam funções locais fixas, com prazo, tratamento de morte e encerramento dos próprios filhos. Não há servidor, autenticação de terceiros, SQL ou downloads no código da aplicação. Os JSONs são dados; não há `eval`.

Nenhum segredo foi inserido intencionalmente; arquivos versionados e diff foram inspecionados antes da publicação. A dependência direta é Matplotlib 3.10.6, consultada em documentação e testada. `pip check` verificou compatibilidade de dependências. Scanners especializados de vulnerabilidades não foram executados nesta revisão; isto não é uma certificação de ausência de vulnerabilidades de terceiros.

## Decisões documentadas

- Projeto novo em pasta própria e branch `entrega`, sem checkout adicional de trabalho: não havia código anterior do usuário a preservar.
- Rotinas de progresso adaptadas a PowerShell/arquivos do ambiente Windows.
- Fixture errada de reabertura substituída por caso efetivamente verificado (registrado no anexo).
- Rastros completos comprimidos em gzip, com um exemplo legível em JSON. Exige descompressão padrão para analisar todos os passos.
- Busca local comparada sob mesmo orçamento de avaliações; o resultado não é uma prova de superioridade geral nem de máximo local da subida.

## Conferências do autor

O projeto foi clonado e executado em outro computador. A revisão pessoal final e a assinatura do PDF cabem ao autor. A automação local não atesta a assinatura nem o envio ao AVA.
