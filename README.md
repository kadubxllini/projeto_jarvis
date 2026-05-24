# Projeto Jarvis Acadêmico 🤖📚

Projeto desenvolvido para a disciplina de Inteligência Artificial do curso de Sistemas de Informação da UFMS (Universidade Federal de Mato Grosso do Sul). 

O Jarvis é um assistente virtual de terminal focado em produtividade acadêmica. Ele é capaz de adicionar tarefas pro dia a dia, listá-las e responder a perguntas complexas baseadas em materiais de estudo fornecidos pelo usuário, utilizando a arquitetura RAG (Retrieval-Augmented Generation).

---

## 🚀 Funcionalidades

- **Gerenciamento de Tarefas (SQLite):** Adição, edição e listagem de tarefas diárias salvas em um banco de dados relacional local.
- **Análise de Materiais Acadêmicos (RAG):** Leitura de documentos PDF em lote e busca vetorial por similaridade semântica para responder a perguntas precisas sobre os textos.
- **Tool Calling Customizado (JSON):** Implementação de uma mecânica de acionamento de ferramentas via formatação estrita de JSON no prompt de sistema, permitindo que o modelo decida quando acessar o banco de dados ou a base de PDFs de forma autônoma.

---

## 🛠️ Tecnologias Utilizadas

- **Linguagem:** Python 3.x
- **LLM:** Gemma-3-12b-it (via API local/institucional)
- **Banco de Dados Vetorial:** ChromaDB (para busca semântica dos textos)
- **Banco de Dados Relacional:** SQLite (para as tarefas)
- **Processamento de PDF:** PyPDF2

---

## 📁 Estrutura do Projeto

O repositório contém apenas os arquivos essenciais para o funcionamento. Arquivos pesados ou temporários (como o banco de dados vetorial) são gerados localmente durante a execução.

```text
├── .gitignore
├── banco_dados.py       # Lógica do SQLite (Tarefas)
├── main.py              # Loop principal e comunicação com a LLM
├── rag.py               # Lógica de extração e vetorização de PDFs
├── requirements.txt     # Dependências do projeto
└── README.md
```

## ⚙️ Como Instalar e Executar
Siga os passos abaixo para rodar o projeto na sua máquina:

**1. Clone o repositório:**
```bash
git clone https://github.com/kadubxllini/projeto_jarvis.git
cd projeto_jarvis
```

**2. Crie e ative um ambiente virtual:**
```bash
python -m venv venv
# No Windows:
venv\Scripts\activate
# No Linux/Mac:
source venv/bin/activate
```

**3. Instale as dependências:**
```bash
pip install -r requirements.txt
```

**4. Prepare o Banco Vetorial (RAG):**
Coloque os seus arquivos .pdf acadêmicos dentro dea pasta data.
```bash
# Após colocar os PDFs na pasta, rode:
python rag.py
```
*(Isso criará a pasta chroma_db localmente com os dados processados).*

**5. Inicie o Assistente:**
```bash
python main.py
```
*(Digite sua pergunta no terminal. Para encerrar, digite "sair").*

## 🤖 Uso de Inteligência Artificial
Conforme os requisitos do projeto da disciplina, declaro o uso das seguintes ferramentas de IA como suporte durante o desenvolvimento:

- **Google Gemini:** Utilizado como suporte técnico e arquitetural, auxiliando na criação da lógica de contorno via JSON para o Tool Calling e na estruturação do banco de dados vetorial (ChromaDB).

- **GitHub Copilot:** Utilizado como assistente de codificação, auxiliando na sugestão de linhas e blocos de código em tempo real durante o desenvolvimento do projeto.

## 🚀 Funcionalidades

* **Gerenciamento de Tarefas (SQLite):** Adição, edição, listagem e conclusão de tarefas diárias salvas em um banco de dados relacional local pelo próprio usuário.
* **Tool Calling Customizado (JSON):** Implementação via prompt estruturado para que a IA decida acessar o banco de dados ou a base de PDFs.
* **Análise de Materiais Acadêmicos (RAG):** Leitura de documentos PDF em lote e busca vetorial por similaridade semântica para responder a perguntas precisas sobre os textos.
* **Melhorias de Aprendizado:** * *Geração de Exercícios:* O sistema lê os PDFs e cria questões inéditas de múltipla escolha com gabarito para o usuário praticar.
  * **Active Recall (Interativo):** O Jarvis elabora uma pergunta curta, aguarda a resposta do usuário, avalia se ele acertou ou errou e explica o conceito correto com base no histórico da conversa.

---

## 📝 Avaliação do Sistema (Testes RAG)

Conforme os critérios de avaliação da disciplina, o sistema foi testado com perguntas focadas nos materiais fornecidos. Abaixo está o relatório de validação das respostas geradas pelo RAG:

OBS: No teste 6 e 7, foram feitas perguntas que não estão no pdf, mas contém conteúdo semelhante, pra avaliar se a LLM respondia mesmo assim ou não.

| ID | Pergunta Efetuada | Documento Recuperado no Log | Classificação do Sistema | OBS |
|:--:|---|---|:---:|---|
| 1 | Na função de inserção de uma Lista Encadeada em C, qual é a finalidade da linha de código `No* novo = (No*) malloc(sizeof(No));` e o que ela faz na memória? | `(b) Usando a função do item (a), escreva um programa que receba um número inteiro n > 0... 2 No * novo = (No *) malloc (sizeof(No));` | Correta ✅ | - |
| 2 | Ao implementar a remoção (pop) em uma estrutura de Pilha em C, qual condição lógica é testada no comando `if (pilha->inicio == NULL)` e qual mensagem é exibida se essa condição for verdadeira? | `dessa avaliação seja verdadeiro, o primeiro bloco de instruções será executado e, ao término desse bloco...` | Parcialmente Correta ⚠️ | Pegou a parte errada no RAG devido a palavras genéricas, mas não respondeu o que não devia devido ao conteúdo não estar no trecho recuperado. |
| 3 | Segundo o material de C sobre Strings e Funções, qual comando deve ser utilizado para limpar o buffer do teclado (stdin) e evitar erros durante a leitura de caracteres compostos? | `Limpando o buffer do teclado Às vezes, podem ocorrer erros durante a leitura de caracteres ou strings do teclado... setbuf(stdin, NULL)` | Correta ✅ | - |
| 4 | Em uma Heap Binária representada internamente por um Array (Vetor), se um nó ancestral está na posição `i`, quais são as fórmulas matemáticas exatas para encontrar a posição do Filho Esquerdo (FE) e do Filho Direito (FD)? | `elementos desde que ambos sejam menores ou maiores que A. Heap Binária vs Fila Ligada... Filho esquerdo (FE) e direito (FD) de um nó;` | Correta ✅ | - |
| 5 | De acordo com os conceitos de Programação Orientada a Objetos, qual é a diferença prática entre o escopo de uma "variável local" e uma "variável de instância" (atributo)? | `Revisão de variáveis durante a execução de programas podemos usar compartimentos de memória para armazenamento de informações...` | Parcialmente Correta ⚠️ | Pegou a parte errada no RAG devido a palavras genéricas, mas não respondeu o que não devia devido ao conteúdo não estar no trecho recuperado. |
| 6 | No material de Python, no exemplo que conta os espaços de um texto (`for letra in texto: if letra == " ": cont += 1`), o que a estrutura de repetição `for` está fazendo dinamicamente com a cadeia de caracteres armazenada na variável `texto`? | `Ordene esses valores de modo que, ao final, o menor valor esteja armazenado na variável x, o valor intermediário esteja armazenado na variável y...` | Correta ✅ | Puxou o chunk esperado e não respondeu a pergunta (tendo em vista que o conteúdo da pergunta não estava no pdf), mesmo sendo conteúdos semelhantes. |
| 7 | No exemplo em Python sobre "Troca de conteúdos", o comando `x, y = y, x` é executado se a condição `if x > y:` for verdadeira. O que esse comando faz na prática com os valores das variáveis sem precisar de uma terceira variável temporária? | `de uma variável pode ser escolhido pelo(a) programador(a) de modo a refletir de alguma forma o seu conteúdo...` | Correta ✅ | Puxou o chunk esperado e não respondeu a pergunta (tendo em vista que o conteúdo da pergunta não estava no pdf), mesmo sendo conteúdos semelhantes. |
| 8 | Como o material define a fórmula matemática para calcular o fatorial de um número inteiro positivo `n` (denotado por `n!`) e qual é o valor adotado por definição para `0!`? | `= n · (n − 1) · (n − 2) · · · 2 · 1. Dessa forma, 5! = 5 · 4 · 3 · 2 · 1 = 120. Por definição, 0! = 1.` | Correta ✅ | - |
| 9 | Na linguagem SQL, ao realizar uma consulta que compara cadeias de caracteres usando as palavras-chave `LIKE` ou `ILIKE`, qual é a diferença na substituição feita pelo caractere coringa `%` (porcentagem) e pelo caractere `_` (underscore)? | `A estrutura de repetição for serve para iterar sobre algum conjunto de dados. Até agora, o único conjunto de dados que conseguimos iterar é as letras de uma cadeia de caracteres (string)` | Parcialmente Correta ⚠️ | Buscou um trecho completamente diferente do que foi pedido (provavelmente pelo uso massivo de caracteres especiais como % e _), porém, não alucinou e respondeu o que achou no pdf, reconheceu que não tinha nada a ver e retornou falta de material disponível. |
| 10 | Em comandos DML no SQL, qual é a diferença entre a operação de remoção feita pelo `DELETE FROM` (sem a cláusula WHERE) e a operação `TRUNCATE TABLE` com o modificador `CASCADE`? | `DML • DELETE FROM ... WHERE ... –Remove dados de tabelas já existentes... Truncate Table • O comando truncate table é utilizado para apagar todos os registros de uma tabela` | Correta ✅ | - |
