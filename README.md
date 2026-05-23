# Projeto Jarvis Acadêmico 🤖📚

Projeto desenvolvido para a disciplina de Inteligência Artificial do curso de Sistemas de Informação da UFMS (Universidade Federal de Mato Grosso do Sul). 

O Jarvis é um assistente virtual de terminal focado em produtividade acadêmica. Ele é capaz de adicionar tarefas pro dia a dia, listá-las e responder a perguntas complexas baseadas em materiais de estudo fornecidos pelo usuário, utilizando a arquitetura RAG (Retrieval-Augmented Generation).

---

## 🚀 Funcionalidades

- **Gerenciamento de Tarefas (SQLite):** Adição e listagem de tarefas diárias salvas em um banco de dados relacional local.
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

* **Gerenciamento de Tarefas (SQLite):** Adição, listagem e conclusão de tarefas diárias salvas em um banco de dados relacional local pelo próprio usuário.
* **Tool Calling Customizado (JSON):** Implementação via prompt estruturado para que a IA decida acessar o banco de dados ou a base de PDFs.
* **Análise de Materiais Acadêmicos (RAG):** Leitura de documentos PDF em lote e busca vetorial por similaridade semântica para responder a perguntas precisas sobre os textos.
* **Melhorias de Aprendizado:** * *Geração de Exercícios:* O sistema lê os PDFs e cria questões inéditas de múltipla escolha com gabarito para o usuário praticar.
  * **Active Recall (Interativo):** O Jarvis elabora uma pergunta curta, aguarda a resposta do usuário, avalia se ele acertou ou errou e explica o conceito correto com base no histórico da conversa.

---

## 📝 Avaliação do Sistema (Testes RAG)

Conforme os critérios de avaliação da disciplina, o sistema foi testado com perguntas focadas nos materiais fornecidos. Abaixo está o relatório de validação das respostas geradas pelo RAG:

| ID | Pergunta Efetuada | Documento Recuperado no Log | Classificação do Sistema |
|:--:|---|---|:---:|
| 1 | *[Sua Pergunta 1]* | *[Trecho do Log]* | Correta ✅ |
| 2 | *[Sua Pergunta 2]* | *[Trecho do Log]* | Correta ✅ |
| 3 | *[Sua Pergunta 3]* | *[Trecho do Log]* | Parcialmente Correta ⚠️ |
| 4 | *[Sua Pergunta 4]* | *[Trecho do Log]* | Correta ✅ |
| 5 | *[Sua Pergunta 5]* | *[Trecho do Log]* | Incorreta ❌ |
| 6 | *[Sua Pergunta 6]* | *[Trecho do Log]* | Correta ✅ |
| 7 | *[Sua Pergunta 7]* | *[Trecho do Log]* | Correta ✅ |
| 8 | *[Sua Pergunta 8]* | *[Trecho do Log]* | Parcialmente Correta ⚠️ |
| 9 | *[Sua Pergunta 9]* | *[Trecho do Log]* | Correta ✅ |
| 10| *[Sua Pergunta 10]*| *[Trecho do Log]* | Correta ✅ |
