# Pull, Otimização e Avaliação de Prompts com LangChain e LangSmith

Desafio do MBA de Engenharia de Software com IA (Full Cycle): puxar prompts de baixa
qualidade do LangSmith Prompt Hub, refatorá-los com técnicas avançadas de Prompt
Engineering, publicar as versões otimizadas e avaliar a qualidade com 5 métricas
customizadas (Helpfulness, Correctness, F1-Score, Clarity, Precision), atingindo
mínimo de 0.8 (80%) em todas.

**Autor:** Igor Veras Lima · **Handle LangSmith Hub:** `igorvlima`

## Técnicas Aplicadas (Fase 2)

O prompt `prompts/bug_to_user_story_v2.yml` foi refatorado aplicando:

### 1. Few-shot Learning (obrigatória)
- **Por quê:** exemplos concretos de entrada/saída eliminam ambiguidade sobre o
  formato esperado. Um modelo com 2 exemplos completos reproduz estrutura, tom e
  nível de detalhe com muito mais consistência do que seguindo apenas instruções.
- **Como:** 2 exemplos completos no `system_prompt` — um bug simples (e-commerce,
  botão de carrinho) e um bug médio com contexto técnico (dashboard com endpoint).
  Cada exemplo mostra o relato de bug (entrada) e a user story completa formatada
  (saída), incluindo Critérios de Aceitação em Dado/Quando/Então.

### 2. Role Prompting
- **Por quê:** definir uma persona (Product Manager Sênior) ativa o conhecimento
  tácito do modelo sobre boas práticas ágeis, fazendo-o produzir user stories com
  foco em valor de negócio, testabilidade e qualidade, em vez de respostas genéricas.
- **Como:** o system prompt abre com a persona ("Você é um Product Manager Sênior
  com 10+ anos de experiência em metodologias ágeis..."), e as regras de
  comportamento reforçam decisões típicas de um PM (persona específica no "Como um",
  benefício de negócio claro, critérios verificáveis).

### 3. Chain of Thought (CoT)
- **Por quê:** converter bug em user story exige raciocínio em etapas: identificar a
  persona afetada, classificar o tipo de bug (UI/UX, validação, lógica,
  infraestrutura), decidir o nível de detalhe. Raciocínio estruturado melhora a
  qualidade da análise, principalmente nos bugs médios e complexos do dataset.
- **Como:** o prompt define um processo de 4 passos ("Passo 1 — Analise o relato...
  Passo 2 — Identifique o tipo...") e instrui o modelo a executar o raciocínio
  internamente, sem expô-lo na resposta final — a saída continua limpa e formatada.

### 4. Skeleton of Thought
- **Por quê:** estruturar a resposta em um esqueleto fixo de seções (
  `## User Story`, `## Critérios de Aceitação`, `## Contexto Técnico` opcional)
  garante clareza e consistência entre exemplos, o que é medido diretamente pela
  métrica de Clarity.
- **Como:** o formato de saída é obrigatório e fixo (seções Markdown), com bullets
  nos critérios começando por Dado/Quando/Então/E, espelhando o ground truth do
  dataset.

### Outras melhorias em relação ao v1
- **System vs User adequado:** o v1 duplicava `{bug_report}` no system e no user
  prompt; o v2 deixa o system_prompt com instruções e regras apenas, e o user_prompt
  só com o relato de bug e o pedido de geração.
- **Tratamento de edge cases:** regras explícitas para bugs com múltiplos problemas
  (cobrir todos), bugs ambíguos (escolher interpretação mais razoável, não inventar
  dados), bugs com contexto técnico (preservar em seção própria), bugs simples vs
  complexos (nível de detalhe proporcional).
- **Regras de comportamento explícitas:** proibição de inventar detalhes, persona
  específica (nunca "um usuário" genérico), critérios mensuráveis e verificáveis
  (nunca "deve funcionar bem"), resposta apenas com a user story final (sem texto
  extra antes/depois).

## Resultados Finais

### Comparação v1 vs v2

| Critério | v1 (original) | v2 (otimizado) |
|---|---|---|
| Persona | Genérica ("um assistente") | Product Manager Sênior experiente |
| Formato de saída | Livre, sem estrutura | Seções fixas Markdown (estrutura condicional por complexidade) |
| Exemplos (few-shot) | Nenhum | 3 exemplos completos (simples, médio, complexo) |
| Raciocínio | Direto, sem etapas | CoT interno em 4 passos |
| Edge cases | Não tratados | Regras explícitas (fidelidade de valores/atores, exaustividade, acessibilidade, integração) |
| System vs User | `{bug_report}` duplicado | Separado corretamente |
| Idioma | Livre | pt-BR |

### Métricas obtidas (avaliação final no LangSmith)

Resultado da iteração 3 do `src/evaluate.py` (experimento `igorvlima-bug_to_user_story_v2-8e88ed12`):

| Métrica | Score | Estado |
|---|---|---|
| Helpfulness | 0.90 | ✓ |
| Correctness | 0.87 | ✓ |
| F1-Score | 0.85 | ✓ |
| Clarity | 0.89 | ✓ |
| Precision | 0.90 | ✓ |

**MÉDIA GERAL: 0.8825 — ✅ APROVADO (todas as métricas ≥ 0.8, não apenas a média)**

Execução de confirmação (experimento `igorvlima-bug_to_user_story_v2-7f77a329`, mesma versão do prompt):
F1-Score 0.87 ✓ | Clarity 0.91 ✓ | Precision 0.90 ✓ | Helpfulness 0.90 ✓ | Correctness 0.89 ✓ — média 0.8928 ✅
(duas execuções consecutivas aprovadas, resultado estável)

Histórico de iteração (F1-Score era a métrica bloqueante):
- Iteração 1 (2 few-shots simples): F1 = 0.77 ✗ → diagnósticos: valores generalizados ("HTTP 2xx" vs "HTTP 200"), ator trocado, omissão de seções da referência
- Iteração 2 (+regras de fidelidade, +3º few-shot complexo, estrutura condicional): F1 = 0.79 ✗ → faltavam critérios técnicos explícitos e a seção "Critérios Técnicos"
- Iteração 3 (+seção Critérios Técnicos para médios/complexos, regra meta-vs-estado atual, acessibilidade e integração): F1 = 0.85 ✓

### Evidências no LangSmith
- Dataset de avaliação compartilhado (15 exemplos): https://smith.langchain.com/public/ec0d6df0-f9b3-4637-aac7-bfcb426036ec/d
- Experimento final (scores ≥ 0.8 em todos os exemplos): https://smith.langchain.com/o/6a1b3b66-ebb8-48de-b9bf-bb73f0d9fd7a/datasets/8096daec-a9c8-4a46-a125-842e09df51d3/compare?selectedSessions=f7641f49-316c-4c1c-98cc-9f475c49becd
- Prompt público: https://smith.langchain.com/prompts/bug_to_user_story_v2/b00a3c5f

Screenshots (assets/screenshots/):

1. Dataset com a tabela de experimentos (nota média por métrica ≥ 0.8):
   ![Dataset e experimentos](assets/screenshots/01-dataset-experimentos-notas.png)

2. Dataset de avaliação com os 15 exemplos:
   ![Dataset 15 exemplos](assets/screenshots/02-dataset-15-exemplos.png)

3. Experimento — topo com médias e total de runs (15/15):
   ![Experimento notas topo](assets/screenshots/03-experimento-notas-topo.png)

4. Experimento — exemplos com Inputs, Reference Outputs, Outputs e notas individuais por métrica:
   ![Exemplos e notas](assets/screenshots/04-experimento-exemplos-notas.png)

5. Prompt público `igorvlima/bug_to_user_story_v2` com tags das técnicas:
   ![Prompt público](assets/screenshots/05-prompt-publico.png)

> Nota: o tracing detalhado de cada exemplo pode ser consultado no link do experimento
> acima (coluna Outputs → link do run) ou no dashboard de Tracing do projeto.

## Infraestrutura: LLMs via OpenRouter

Em vez de usar OpenAI ou Gemini diretamente, este projeto usa a **OpenRouter**
(API compatível com OpenAI) apontando para os modelos mais baratos disponíveis que
cumprem o desafio:

```ini
LLM_PROVIDER=openai
OPENAI_API_KEY=<chave da OpenRouter>
OPENAI_BASE_URL=https://openrouter.ai/api/v1
LLM_MODEL=deepseek/deepseek-v4.1-flash     # geração das user stories
EVAL_MODEL=deepseek/deepseek-v4.1-flash    # LLM-as-judge (3 juízes)
```

Justificativa: `deepseek/deepseek-v4.1-flash` oferece o melhor custo-benefício
(US$ 0,028/M tokens de entrada e US$ 0,12/M de saída) com excelente capacidade de
seguir instruções e gerar JSON — requisito para as métricas LLM-as-judge. O custo
total do desafio fica abaixo de US$ 0,10 (vs. US$ 1–5 estimados no enunciado).

## Como Executar

### Pré-requisitos
- Python 3.10+
- Conta gratuita no LangSmith (https://smith.langchain.com) + API Key
- Handle público do LangSmith Hub criado (ver seção abaixo)
- Chave da OpenRouter (https://openrouter.ai/keys)

### Setup
```bash
python3 -m venv venv
source venv/bin/activate           # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

Preencha o `.env`:
```ini
LANGSMITH_TRACING=true
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
LANGSMITH_API_KEY=<sua chave>
LANGSMITH_PROJECT=mba-ia-pull-evaluation-prompt
USERNAME_LANGSMITH_HUB=igorvlima

OPENAI_API_KEY=<chave da OpenRouter>
OPENAI_BASE_URL=https://openrouter.ai/api/v1
LLM_PROVIDER=openai
LLM_MODEL=deepseek/deepseek-v4.1-flash
EVAL_MODEL=deepseek/deepseek-v4.1-flash
```

### Handle do LangSmith Hub (primeira vez)
O handle (`igorvlima`) não existe por padrão — é criado na primeira publicação:
1. Em LangSmith → **Prompts**, crie um prompt qualquer (ex: "teste")
2. Clique nos **três pontinhos** (ao lado do Playground) → **Make Public**
3. Na tela **Choose your public handle**, defina o handle (definitivo)
4. Coloque esse valor em `USERNAME_LANGSMITH_HUB` no `.env`

### Execução (ordem oficial)
```bash
# 1. Pull do prompt semente de baixa qualidade
python src/pull_prompts.py

# 2. Refatorar o prompt (arquivo prompts/bug_to_user_story_v2.yml)

# 3. Validar com pytest
pytest tests/test_prompts.py -v

# 4. Push do prompt otimizado (público, com metadados)
python src/push_prompts.py

# 5. Avaliar: cria experimento no LangSmith, roda os 15 exemplos e
#    grava as 5 notas como feedback por exemplo
python src/evaluate.py
```

Cada execução do passo 5 cria um experimento novo, permitindo comparar iterações
lado a lado no dashboard. Itere até todas as métricas ≥ 0.8.

## Estrutura do projeto

```
mba-ia-pull-evaluation-prompt/
├── .env.example              # Template das variáveis de ambiente
├── requirements.txt          # Dependências Python
├── README.md                 # Este arquivo
├── prompts/
│   ├── bug_to_user_story_v1.yml  # Prompt inicial (puxado do Hub)
│   └── bug_to_user_story_v2.yml  # Prompt otimizado (este desafio)
├── datasets/
│   └── bug_to_user_story.jsonl   # 15 exemplos de bugs (pronto)
├── src/
│   ├── pull_prompts.py       # Pull do LangSmith (implementado)
│   ├── push_prompts.py       # Push ao LangSmith (implementado)
│   ├── evaluate.py           # Avaliação automática (pronto)
│   ├── metrics.py            # 5 métricas LLM-as-judge (pronto)
│   └── utils.py              # Funções auxiliares (pronto)
└── tests/
    └── test_prompts.py       # 6 testes de validação (implementado)
```

## Observações
- Os arquivos marcados como "pronto" (src/evaluate.py, src/metrics.py, src/utils.py,
  datasets/) não foram alterados.
- `src/pull_prompts.py` e `src/push_prompts.py` foram implementados a partir do
  esqueleto fornecido.
- `tests/test_prompts.py` implementa os 6 testes obrigatórios + 1 teste extra
  usando a validação utilitária do projeto (7 testes no total).