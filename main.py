from openai import OpenAI
import json
import banco_dados
import rag
import datetime

# =====================================================
# CONFIGURAÇÃO DO SERVIDOR
# =====================================================

client = OpenAI(
    base_url="https://llm.liaufms.org/v1/gemma-3-12b-it",
    api_key="Cxt2ftLF7d3mHS2JdiFqB-eSDAQeZvFATPXPs02lV9A"
)

MODEL = "google/gemma-3-12b-it"

# =====================================================
# MEMÓRIA
# =====================================================

# Pegar a data de hoje para usar como referência pra agenda
data_hoje = datetime.date.today().strftime('%Y-%m-%d')

prompt_sistema = f"""
Você é Jarvis, um assistente acadêmico.

A data exata de hoje é {data_hoje}. 
Use esta data como base absoluta para calcular qualquer dia que o usuário pedir (como "hoje", "amanhã", "próxima segunda", etc).

Você:
- conversa naturalmente
- ajuda nos estudos
- responde perguntas sobre PDFs
- gera exercícios
- faz active recall
- avalia respostas do usuário

Você possui memória da conversa.
"""

historico_chat = [
    {
        "role": "system",
        "content": prompt_sistema
    }
]

# =====================================================
# IA ESCOLHE A FERRAMENTA
# =====================================================

def escolher_ferramenta(msg):

    global historico_chat

    contexto = historico_chat[-6:]

    contexto_formatado = ""

    for item in contexto:

        contexto_formatado += f"""
{item['role']}:
{item['content']}
"""

    prompt = f"""
Você é um roteador de ferramentas.

Na MAIORIA das vezes, a resposta correta é:
"chat"

Use ferramentas APENAS quando necessário.

Ferramentas disponíveis:

- adicionar_tarefa
- editar_tarefa
- listar_tarefas
- concluir_tarefa
- adicionar_evento
- consultar_agenda
- buscar_material_rag
- gerar_exercicios
- fazer_pergunta
- chat

REGRAS IMPORTANTES:

- Conversas normais -> chat
- Cumprimentos -> chat
- Perguntas pessoais -> chat
- Perguntas sobre memória -> chat
- Perguntas simples -> chat

Use "fazer_pergunta" APENAS quando o usuário quiser ser testado.

Use "buscar_material_rag" APENAS quando o usuário quiser explicações baseadas nos PDFs.

Contexto recente:
{contexto_formatado}

Mensagem atual:
"{msg}"

Responda apenas o nome da ferramenta.
"""

    resposta = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0
    )

    ferramenta = resposta.choices[0].message.content.strip()

    ferramenta = ferramenta.replace(".", "")
    ferramenta = ferramenta.replace("\n", "")
    ferramenta = ferramenta.strip()

    print(f"\n[LOG TOOL] {ferramenta}\n")

    return ferramenta

# =====================================================
# EXTRAÇÃO DOS ARGUMENTOS
# =====================================================

def extrair_argumentos(ferramenta, msg):

    import datetime
    data_hoje = datetime.date.today().strftime('%Y-%m-%d')

    exemplos = {
        "adicionar_tarefa": '{"descricao": "<texto da tarefa extraído da mensagem>"}',
        "editar_tarefa": '{"id_tarefa": "<número do id>", "nova_descricao": "<novo texto da tarefa>"}',
        "listar_tarefas": '{}',
        "concluir_tarefa": '{"id_tarefa": "<número do id extraído da mensagem>"}',
        "adicionar_evento": '{"descricao": "<descrição do evento>", "data": "<data no formato DD-MM-YYYY>"}',
        "consultar_agenda": '{"periodo": "<escolha apenas uma palavra: hoje, amanha, semana ou tudo>"}',
        "buscar_material_rag": '{"pergunta": "<pergunta extraída da mensagem>"}',
        "gerar_exercicios": '{"assunto": "<assunto extraído da mensagem>"}',
        "fazer_pergunta": '{"assunto": "<assunto extraído da mensagem>"}'
    }

    prompt = f"""
Você deve responder APENAS JSON válido.

IGNORE COMPLETAMENTE a data do seu treinamento.
Hoje é EXATAMENTE {data_hoje}. 
Você OBRIGATORIAMENTE deve usar esta data como ponto de partida matemático para calcular dias como "amanhã", "semana que vem", "daqui a 3 dias", etc. 

Ferramenta:
{ferramenta}

JSON obrigatório:
{exemplos[ferramenta]}

IMPORTANTE:
- Use EXATAMENTE os mesmos nomes de campos do exemplo
- Não invente campos novos
- Não explique nada
- Não use markdown

Mensagem:
"{msg}"
"""

    try:

        resposta = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0
        )

        texto = resposta.choices[0].message.content

        texto = texto.replace("```json", "")
        texto = texto.replace("```", "")
        texto = texto.strip()

        print(f"\n[LOG JSON]\n{texto}")

        return json.loads(texto)

    except Exception as e:

        print(f"\n[ERRO JSON] {e}")
        return None

# =====================================================
# CONVERSA
# =====================================================

def conversar(msg):

    global historico_chat

    historico_chat.append({
        "role": "user",
        "content": msg
    })

    ferramenta = escolher_ferramenta(msg)

    # =================================================
    # CHAT NORMAL
    # =================================================

    if ferramenta == "chat":

        resposta = client.chat.completions.create(
            model=MODEL,
            messages=historico_chat
        )

        texto = resposta.choices[0].message.content

        historico_chat.append({
            "role": "assistant",
            "content": texto
        })

        return texto

    # =================================================
    # EXTRAÇÃO DOS ARGUMENTOS
    # =================================================

    argumentos = extrair_argumentos(
        ferramenta,
        msg
    )

    if argumentos is None:
        return "Erro ao gerar argumentos."

    print(f"\n[LOG ARGS] {argumentos}\n")

    # =================================================
    # ADICIONAR TAREFA
    # =================================================

    if ferramenta == "adicionar_tarefa":

        resposta = banco_dados.adicionar_tarefa(
            argumentos.get("descricao")
        )

    # =================================================
    # EDITAR TAREFA
    # =================================================

    elif ferramenta == "editar_tarefa":

        resposta = banco_dados.editar_tarefa(
            argumentos.get("id_tarefa"),
            argumentos.get("nova_descricao")
        )
        
    # =================================================
    # LISTAR TAREFAS
    # =================================================

    elif ferramenta == "listar_tarefas":

        resposta = banco_dados.listar_tarefas()

    # =================================================
    # CONCLUIR TAREFA
    # =================================================

    elif ferramenta == "concluir_tarefa":

        resposta = banco_dados.concluir_tarefa(
            argumentos.get("id_tarefa")
        )

    # =================================================
    # AGENDA: ADICIONAR
    # =================================================

    elif ferramenta == "adicionar_evento":
        resposta = banco_dados.adicionar_evento(
            argumentos.get("descricao"),
            argumentos.get("data")
        )

    # =================================================
    # AGENDA: CONSULTAR
    # =================================================

    elif ferramenta == "consultar_agenda":
        periodo = argumentos.get("periodo")
        dados_brutos = banco_dados.consultar_agenda(periodo)

        print(f"\n[LOG AGENDA]\n{dados_brutos}\n")

        prompt = f"""
Baseado nos dados que o banco de dados retornou:
{dados_brutos}

Responda à pergunta do usuário de forma natural e direta:
"{msg}"
"""
        resposta_llm = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}]
        )
        resposta = resposta_llm.choices[0].message.content

    # =================================================
    # BUSCAR MATERIAL RAG
    # =================================================

    elif ferramenta == "buscar_material_rag":

        pergunta = argumentos.get("pergunta")

        if not pergunta:
            return "Não consegui identificar a pergunta."

        trechos = rag.buscar_no_material(pergunta)

        print(f"\n[LOG RAG]\n{trechos[:500]}")

        prompt = f"""
Baseado APENAS nestes trechos:
{trechos}

Responda:
{pergunta}
"""

        resposta_llm = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        resposta = resposta_llm.choices[0].message.content

    # =================================================
    # GERAR EXERCÍCIOS
    # =================================================

    elif ferramenta == "gerar_exercicios":

        assunto = argumentos.get("assunto")

        if not assunto:
            return "Não consegui identificar o assunto dos exercícios."

        trechos = rag.buscar_no_material(assunto)

        prompt = f"""
    
Baseado APENAS nestes trechos:
{trechos}


O usuário pediu o seguinte pedido:
{msg}

Crie os exercícios de acordo com o que o usuário pediu acima (quantidade, modelo, etc):
{assunto}

Com gabarito.
"""

        resposta_llm = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        resposta = resposta_llm.choices[0].message.content

    # =================================================
    # ACTIVE RECALL
    # =================================================

    elif ferramenta == "fazer_pergunta":

        assunto = argumentos.get("assunto")

        if not assunto:
            return "Não consegui identificar o assunto da pergunta."

        trechos = rag.buscar_no_material(assunto)

        prompt = f"""
Baseado APENAS nestes trechos:
{trechos}

Faça UMA pergunta sobre:
{assunto}

Não dê a resposta.
"""

        resposta_llm = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        resposta = resposta_llm.choices[0].message.content

    # =================================================
    # FERRAMENTA INVÁLIDA
    # =================================================

    else:

        resposta = "Ferramenta inválida."

    # =================================================
    # SALVA NA MEMÓRIA
    # =================================================

    historico_chat.append({
        "role": "assistant",
        "content": resposta
    })

    return resposta

# =====================================================
# LOOP PRINCIPAL
# =====================================================

print("Jarvis iniciado!")

while True:

    msg = input("\nVocê: ")

    if msg.lower() == "sair":
        break

    resposta = conversar(msg)
    print("=" * 50)
    print(f"\nJarvis: {resposta}")