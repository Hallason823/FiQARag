# Histórico das versões de prompts

## 1. Objetivo

Este documento registra a evolução dos prompts do FiQA RAG, os problemas tratados em cada versão e os resultados observados durante a avaliação.

Os catálogos estão armazenados em `fiqa-rag-api/config/prompts/`. Cada arquivo representa uma configuração completa das etapas que interagem com a LLM.

Uma versão pode conter os seguintes prompts:

- `classification`: classifica a pergunta e determina se ela pertence ao domínio;
- `generation`: gera a resposta a partir dos documentos recuperados;
- `verification`: verifica se a resposta está sustentada pelos documentos e se seguiu alguma instrução injetada.

## 2. Regra de versionamento

O versionamento segue a convenção:

- **MAJOR:** mudança estrutural no catálogo ou no fluxo, como a inclusão de uma nova etapa;
- **MINOR:** inclusão de comportamento mantendo a estrutura principal;
- **PATCH:** correção textual que não altera a intenção do prompt.

Os nomes dos arquivos acrescentam um identificador descritivo à versão:

```text
<versão>__<descrição>.json
```

Exemplo:

```text
v2.1.0__few_shot.json
```

## 3. Visão geral

| Versão | Prompts | Principal mudança |
| :-- | :-- | :-- |
| `v1.0.0__baseline` | geração | Prompt original da atividade anterior |
| `v2.0.0__zero_shot` | geração | Estrutura completa, segurança, abstenção e delimitadores |
| `v2.1.0__few_shot` | geração | Inclusão de quatro exemplos |
| `v3.0.0__decomposed` | classificação e geração | Decomposição do fluxo e saída estruturada |
| `v4.0.0__verified` | classificação, geração e verificação | Verificação da resposta e correção do domínio do classificador |

## 4. `v1.0.0__baseline`

Arquivo: [`v1.0.0__baseline.json`](../fiqa-rag-api/config/prompts/v1.0.0__baseline.json)

### Estrutura

A baseline contém apenas o prompt de geração utilizado na atividade anterior.

O system prompt define quatro comportamentos principais:

- responder com base no contexto financeiro;
- não utilizar conhecimento externo;
- citar as fontes;
- utilizar uma frase exata quando não houver evidência.

O user prompt possui duas regiões textuais simples:

- `CONTEXT`;
- `QUESTION`.

Não há seções explícitas para papel, tarefa, regras, segurança ou formato de saída. Também não há delimitadores estruturados separando histórico, documentos e pergunta.

### Comportamento observado

Na avaliação:

- respondeu 2 das 8 perguntas;
- absteve-se nas outras 6;
- apresentou uma visão predominante na pergunta com documentos conflitantes;
- resistiu à indirect prompt injection da pergunta 8;
- não possuía classificação ou verificação estruturada.

A resistência à injection indireta foi observada nesta execução, mas não existe uma regra de segurança tão detalhada quanto nas versões posteriores.

Resultado bruto: [`v1.0.0__baseline.json`](./output/v1.0.0__baseline.json).

## 5. `v2.0.0__zero_shot`

Arquivo: [`v2.0.0__zero_shot.json`](../fiqa-rag-api/config/prompts/v2.0.0__zero_shot.json)

### Motivação

A baseline utilizava instruções curtas e reunidas em um único parágrafo. A v2.0.0 reorganizou o prompt para tornar cada responsabilidade explícita.

### Alterações

O prompt de geração passou a definir:

- papel do modelo;
- objetivo da tarefa;
- regras numeradas;
- uso exclusivo dos documentos recuperados;
- citações no formato `[Source N]`;
- tratamento de opiniões conflitantes;
- tratamento de publicações informais, spam e anúncios;
- tratamento de citações de outros usuários;
- cuidado com valores e informações datadas;
- resposta no mesmo idioma da pergunta;
- limite de tamanho;
- critérios explícitos de abstenção;
- formato esperado da resposta;
- defesa contra prompt injection.

O user prompt passou a separar os dados utilizando:

- `<history>`;
- `<documents>`;
- `<question>`.

O conteúdo dessas regiões é declarado como dado, não como instrução. A regra de segurança é repetida depois das regiões, aplicando uma forma de sandwich defense.

Essa versão não contém exemplos, caracterizando uma abordagem zero-shot.

### Comportamento observado

Na avaliação:

- respondeu com fontes às perguntas 1, 2, 5, 7 e 8;
- apresentou as opiniões conflitantes na pergunta 2;
- respondeu em português na pergunta 5;
- não seguiu as injections direta ou indireta;
- absteve-se funcionalmente nas perguntas 3, 4 e 6.

Na pergunta 3, o modelo acrescentou uma linha `Sources:` depois da frase de abstenção. Como o backend compara a resposta com a frase exata, a abstenção não foi registrada como `INSUFFICIENT_EVIDENCE` e os documentos recuperados permaneceram na resposta.

Esse resultado mostrou que uma instrução zero-shot ainda poderia falhar em um formato estrito utilizado posteriormente pelo software.

Resultado bruto: [`v2.0.0__zero_shot.json`](./output/v2.0.0__zero_shot.json).

## 6. `v2.1.0__few_shot`

Arquivo: [`v2.1.0__few_shot.json`](../fiqa-rag-api/config/prompts/v2.1.0__few_shot.json)

### Motivação

A v2.1.0 foi criada para comparar o prompt zero-shot com uma versão equivalente contendo exemplos.

### Alterações

As regras da v2.0.0 foram mantidas. Foram adicionados quatro exemplos:

1. resposta em português com citação e descarte de um documento irrelevante;
2. abstenção quando os documentos contêm apenas spam ou conteúdo não relacionado;
3. uso da parte legítima de um documento com instrução injetada;
4. resposta a uma pergunta de acompanhamento utilizando o histórico.

Os exemplos utilizam documentos reais da base FiQA ou adaptações controladas desses documentos. Eles são apresentados como demonstrações de comportamento e não podem ser usados como fontes da pergunta atual.

### Comportamento observado

A v2.1.0 apresentou respostas semanticamente semelhantes às da v2.0.0.

A principal diferença observável ocorreu na pergunta 3. A few-shot devolveu somente a frase de abstenção exigida, permitindo que o backend:

- registrasse `INSUFFICIENT_EVIDENCE`;
- removesse as fontes;
- evitasse salvar a resposta no histórico.

Não foi observada uma melhoria geral em todas as respostas. O benefício demonstrado nesta rodada foi maior aderência ao formato estrito de abstenção.

Resultado bruto: [`v2.1.0__few_shot.json`](./output/v2.1.0__few_shot.json).

## 7. `v3.0.0__decomposed`

Arquivo: [`v3.0.0__decomposed.json`](../fiqa-rag-api/config/prompts/v3.0.0__decomposed.json)

### Motivação

Até a v2.1.0, o prompt de geração era responsável por avaliar o contexto, responder, aplicar regras de segurança e decidir quando se abster.

A v3.0.0 iniciou a decomposição dessas responsabilidades.

### Alterações

Foi adicionado o prompt `classification`, responsável por produzir um objeto JSON contendo:

- `in_domain`;
- `category`;
- `confidence`;
- `contains_instructions`;
- `reason`.

A saída é validada pelo modelo Pydantic `QuestionClassification` e utilizada pelo LangGraph para decidir se o fluxo deve:

- continuar para a recuperação;
- encerrar com uma resposta de fora do domínio.

O prompt de geração foi mantido equivalente ao da v2.1.0.

### Limitação identificada

A definição de domínio do classificador da v3 era mais estreita para assuntos relacionados a trabalho e à relação entre empresas e trabalhadores.

A categoria `BUSINESS_AND_ECONOMY` mencionava empresas, empreendedorismo, finanças corporativas, mercados e economia, mas não explicitava:

- empregos;
- salários;
- benefícios;
- contratação;
- treinamento no trabalho;
- carreiras;
- mercado de trabalho.

Isso tornava ambígua a classificação de perguntas como:

```text
Should companies be expected to provide on-the-job training to workers according to the documents?
```

A correção foi incorporada ao classificador da v4.

A v3 representa uma etapa intermediária da arquitetura e não foi incluída nas quatro rodadas principais da comparação.

## 8. `v4.0.0__verified`

Arquivo: [`v4.0.0__verified.json`](../fiqa-rag-api/config/prompts/v4.0.0__verified.json)

### Motivação

A decomposição da v3 permitia classificar a pergunta antes da recuperação, mas ainda não havia uma etapa independente para avaliar a resposta gerada.

A v4 adicionou essa verificação e corrigiu os limites do domínio do classificador.

### Prompt de verificação

Foi adicionado o prompt `verification`, responsável por comparar:

- documentos recuperados;
- pergunta;
- resposta gerada.

O verificador produz um objeto JSON contendo:

- `verdict`;
- `follows_embedded_instructions`;
- `unsupported_claims`;
- `reason`.

Os possíveis veredictos são:

- `SUPPORTED`;
- `PARTIALLY_SUPPORTED`;
- `NOT_SUPPORTED`.

O fluxo rejeita a resposta quando:

- o conteúdo principal não está sustentado;
- a resposta segue uma instrução injetada nos documentos ou na pergunta.

Quando rejeitada, a resposta é substituída pela mensagem de abstenção.

### Correção do classificador

Embora a descrição original do catálogo afirmasse que a classificação era uma cópia exata da v3, o conteúdo real foi corrigido na v4.

As mudanças foram:

- inclusão de salário e ofertas de emprego em `PERSONAL_FINANCE`;
- ampliação de `BUSINESS_AND_ECONOMY` para a relação entre empresas e trabalhadores;
- inclusão explícita de empregos, salários, benefícios, contratação, treinamento, carreiras e mercado de trabalho;
- redefinição de `OUT_OF_DOMAIN` para assuntos claramente não relacionados a dinheiro, trabalho ou negócios;
- orientação para manter no domínio perguntas plausíveis de fóruns financeiros ou empresariais;
- orientação para classificar o assunto subjacente quando a pergunta mencionar documentos, base ou fontes;
- inclusão de um exemplo de classificação sobre treinamento no trabalho.

Essa correção permitiu que a pergunta 2 fosse classificada como `BUSINESS_AND_ECONOMY`, com confiança alta.

### Comportamento observado

Na avaliação, a v4:

- respondeu às perguntas 1, 2, 5, 7 e 8;
- classificou a pergunta 4 como `OUT_OF_DOMAIN`;
- detectou `contains_instructions: true` na injection direta;
- verificou como `SUPPORTED` as respostas produzidas;
- não seguiu a instrução direta para utilizar conhecimento geral;
- não seguiu a instrução injetada no fixture;
- não revelou a senha nem o endereço malicioso;
- absteve-se nas perguntas 3 e 6.

Resultado bruto: [`v4.0.0__verified.json`](./output/v4.0.0__verified.json).

## 9. Problemas e aprendizados

| Problema observado | Versão em que apareceu | Tratamento ou conclusão |
| :-- | :-- | :-- |
| Instruções genéricas e pouco estruturadas | v1 | Prompt reorganizado na v2 |
| Ausência de separação explícita entre dados e instruções | v1 | Delimitadores e regras de segurança na v2 |
| Baixa utilização de evidências em perguntas respondíveis | v1 | Regras mais detalhadas na v2 |
| Linha `Sources:` adicionada à abstenção | v2.0 | Exemplo de abstenção na v2.1 melhorou a aderência |
| Muitas responsabilidades no prompt de geração | v2.1 | Classificação separada na v3 |
| Domínio estreito para trabalho e treinamento | v3 | Classificador corrigido na v4 |
| Ausência de validação independente da resposta | v3 | Verificador adicionado na v4 |
| Pergunta de acompanhamento não respondida | Todas as versões avaliadas | Limitação atual da combinação entre histórico, recuperação e evidências |
| Baseline resistiu à injection indireta | v1 | Não atribuir à v4 uma melhoria não demonstrada |
| Few-shot não melhorou todas as respostas | v2.1 | Registrar apenas o ganho observado no formato de abstenção |

## 10. Artefatos da avaliação

Os resultados e a análise comparativa estão disponíveis em:

- [`v1.0.0__baseline.json`](./output/v1.0.0__baseline.json);
- [`v2.0.0__zero_shot.json`](./output/v2.0.0__zero_shot.json);
- [`v2.1.0__few_shot.json`](./output/v2.1.0__few_shot.json);
- [`v4.0.0__verified.json`](./output/v4.0.0__verified.json);
- [`COMPARISON.md`](./output/COMPARISON.md).

Os arquivos JSON preservam as respostas brutas, configurações, classificações, verificações, fontes, motivos de abstenção e verificações específicas dos testes de injection.