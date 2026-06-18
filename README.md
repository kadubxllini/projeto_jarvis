# Projeto Jarvis Acadêmico 🤖📚

Projeto desenvolvido para a disciplina de Inteligência Artificial do curso de Sistemas de Informação da UFMS (Universidade Federal de Mato Grosso do Sul). 

O Jarvis é um assistente virtual com interface web (desenvolvida em Gradio) focado em produtividade acadêmica. Ele é capaz de gerenciar tarefas e compromissos do dia a dia e responder a perguntas complexas com base em materiais de estudo fornecidos pelo usuário, utilizando a arquitetura RAG (Retrieval-Augmented Generation).

---

## 🚀 Funcionalidades

* **Interface Web Amigável (Gradio):** Chatbot interativo lado a lado com um painel de consultas rápidas via IA para ver tarefas e compromissos de forma rápida.
* **Gerenciamento de Tarefas (SQLite):** Adição, edição, listagem e conclusão de tarefas pendentes salvas em um banco de dados local.
* **Agenda Acadêmica (SQLite):** Agendamento, edição, remoção e consulta de eventos/compromissos. Conta com injeção dinâmica da data atual no prompt, permitindo que a IA faça cálculos temporais exatos (como calcular datas relativas a "amanhã" ou "próxima segunda") sem sofrer com limitações de ano do seu treinamento original.
* **Planejamento de Estudos (SQLite + RAG):** Integração inteligente para criar um plano de ação personalizado. O Jarvis cruza as tarefas pendentes, os compromissos da agenda e os materiais de estudo relevantes (RAG) baseados no assunto solicitado para sugerir prioridades e tópicos de foco.
* **Tool Calling Customizado (JSON):** Tomada de decisão estruturada por prompt para que a IA decida dinamicamente quando acessar as tarefas, a agenda ou realizar uma busca na base de PDFs.
* **Análise de Materiais Acadêmicos (RAG):** Sincronização automática e leitura de documentos PDF em lote com busca vetorial por similaridade semântica para responder a perguntas precisas sobre os textos.
* **Melhorias de Aprendizado:**
  * **Geração de Exercícios:** O sistema lê os PDFs e cria questões personalizadas com gabarito baseado estritamente na base de conhecimento fornecida.
  * **Active Recall (Interativo):** O Jarvis formula uma pergunta curta baseada nos PDFs, aguarda a resposta do usuário, avalia e classifica a resposta (como Correta, Parcialmente Correta ou Incorreta) explicando os conceitos corretos.
* **Registro de Auditoria (Logs locais):** Todas as interações (ferramentas selecionadas, argumentos extraídos, mensagens do usuário e respostas obtidas) são registradas no arquivo local `logs/logs.txt` para fins de depuração e histórico.

---

## 🛠️ Tecnologias Utilizadas

- **Linguagem:** Python 3.x
- **LLM:** Qwen 2.5 14B Instruct AWQ (via API local/institucional da UFMS)
- **Interface Gráfica:** Gradio
- **Banco de Dados Vetorial:** ChromaDB (para busca semântica dos textos)
- **Banco de Dados Relacional:** SQLite (para gerenciamento de tarefas e agenda)
- **Processamento de PDF:** pypdf
- **Cliente de API LLM:** openai (SDK Python, apontado para a API local)
- **Gerenciamento de Ambiente:** python-dotenv

---

## 📁 Estrutura do Projeto

O repositório contém apenas os arquivos essenciais para o funcionamento. Arquivos pesados ou de armazenamento local (como o banco de dados SQLite e o banco de dados vetorial do Chroma) são criados de forma automática e local na primeira execução.

```text
├── data/                # Pasta contendo os PDFs de entrada
│   ├── chroma_db/       # Banco de dados vetorial do Chroma (gerado automaticamente)
│   └── .rag_index.json  # Índice de sincronização dos PDFs (gerado automaticamente)
├── logs/
│   └── logs.txt         # Histórico de logs de interações (gerado automaticamente)
├── src/
│   ├── __init__.py
│   ├── agent.py         # Lógica do agente, tomada de decisão e fluxo de conversa
│   ├── database.py      # Operações de CRUD de tarefas e agenda no SQLite
│   ├── logger.py        # Registro de logs local em arquivo
│   ├── rag.py           # Configuração do ChromaDB, indexação e busca RAG
│   └── tools.py         # Mapeamento de intenções e extração de argumentos
├── .env                 # Variáveis de ambiente (API_KEY)
├── .gitignore
├── jarvis_academico.db  # Banco de dados SQLite (gerado automaticamente)
├── main.py              # Inicialização do banco, RAG e interface Gradio
├── requirements.txt     # Dependências do projeto
└── README.md
```

---

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

**4. Insira a API Key:**
Crie um arquivo `.env` na raiz do projeto com a chave da API fornecida:
```env
API_KEY=seu_token_aqui
```

**5. Prepare os Materiais de Estudo (RAG):**
Crie uma pasta chamada `data` na raiz do projeto (se já não existir) e coloque os seus arquivos `.pdf` acadêmicos dentro dela.

**6. Inicie o Assistente:**
```bash
python main.py
```
*(O sistema irá inicializar o banco de dados, indexar/sincronizar os PDFs da pasta `data` automaticamente e abrir um servidor local do Gradio. Basta clicar no link gerado no terminal para usar a interface web).*

---

## 📂 Sobre o Dataset

- **Origem:** Arquivos em PDF contendo material acadêmico da UFMS.
- **Conteúdo:** Teoria e código sobre C, Python, Programação Orientada a Objetos e SQL.

## ⚠️ Limitações dos Dados (PDF)

- **Perda de formatação:** A extração do texto cru quebra a indentação (o que pode dificultar a semântica do código em Python).
- **Perda de símbolos:** Caracteres especiais de programação (como `%`, `_`, `{}`) muitas vezes são ignorados na extração dependendo do encoding.
- **Elementos visuais:** Gráficos, diagramas de arquitetura/memória e tabelas complexas não são compreendidos pela extração simples de texto.

## ⚙️ Estratégia de Chunking e Impacto no RAG

- **Como foi feito:** Divisão em pedaços (chunks) de tamanho fixo. O sistema recupera 2 chunks por busca, enviando o contexto para a IA.
- **Ponto Positivo (Zero Alucinação):** O contexto maior força o grounding. Se a resposta não está no texto, a IA avisa em vez de inventar.
- **Ponto Negativo (Busca de Código):** A busca semântica (vetorial) tem dificuldade em localizar trechos exatos de código isolados no meio de explicações teóricas.

---

## 🤖 Uso de Inteligência Artificial

Conforme os requisitos do projeto da disciplina, declaro o uso das seguintes ferramentas de IA como suporte durante o desenvolvimento:

- **Google Gemini:** Utilizado como suporte técnico e arquitetural, auxiliando na criação da lógica de contorno via JSON para o Tool Calling e na estruturação do banco de dados vetorial (ChromaDB).
- **Anthropic Claude:** Utilizado no início do desenvolvimento para auxiliar na modelagem do esqueleto do projeto e discussão de ideias de arquitetura.
- **GitHub Copilot:** Utilizado como assistente de codificação, auxiliando na sugestão de linhas e blocos de código em tempo real durante o desenvolvimento do projeto.

---

## 📝 Avaliação do Sistema (Testes RAG)

*Esta seção está em branco e será atualizada após a realização dos novos testes do sistema.*
