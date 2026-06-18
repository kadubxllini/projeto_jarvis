from openai import OpenAI
import json
import banco_dados
import rag
import datetime
import os
from dotenv import load_dotenv

# =====================================================
# CONFIGURAÇÃO DO SERVIDOR
# =====================================================

load_dotenv()
client = OpenAI(
    base_url="https://llm.liaufms.org/v1/qwen2-5-14b-instruct-awq",
    api_key=os.getenv("API_KEY")
)

MODEL = "Qwen/Qwen2.5-14B-Instruct-AWQ"

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

estado_jarvis = "normal"
pergunta_ativa = ""
assunto_ativo = ""

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
- editar_evento
- consultar_agenda
- apagar_evento
- buscar_material_rag
- gerar_exercicios
- fazer_pergunta
- planejar_estudos
- chat

REGRAS IMPORTANTES:

- Conversas normais -> chat
- Cumprimentos -> chat
- Perguntas pessoais -> chat
- Perguntas sobre memória -> chat
- Perguntas simples -> chat
- Para organizar o tempo, perguntar o que priorizar ou montar planos de estudo -> planejar_estudos

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
        "editar_evento": '{"id_evento": "<número do id>", "nova_descricao": "<novo texto ou null se não mudar>", "nova_data": "<nova data YYYY-MM-DD ou null se não mudar>"}',
        "consultar_agenda": '{"periodo": "<escolha apenas uma palavra: hoje, amanha, semana ou tudo>"}',
        "apagar_evento": '{"id_evento": "<número do id>"}',
        "buscar_material_rag": '{"pergunta": "<pergunta extraída da mensagem>"}',
        "gerar_exercicios": '{"assunto": "<assunto extraído da mensagem>"}',
        "fazer_pergunta": '{"assunto": "<assunto extraído da mensagem>"}',
        "planejar_estudos": '{"assunto": "<assunto específico para focar, ou null se for geral>"}'
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

    global historico_chat, estado_jarvis, pergunta_ativa, assunto_ativo

    historico_chat.append({
        "role": "user",
        "content": msg
    })

    # INTERCEPTA A MENSAGEM SE ESTIVER NO MODO AVALIAÇÃO
    if estado_jarvis == "esperando_resposta":
        trechos = rag.buscar_no_material(assunto_ativo)
        
        prompt_avaliacao = f"""
Você fez a seguinte pergunta de Active Recall para o usuário:
"{pergunta_ativa}"

O usuário respondeu:
"{msg}"

Baseado APENAS nestes materiais de estudo:
{trechos}

Avalie a resposta do usuário. Classifique explicitamente como: Correta, Parcialmente Correta ou Incorreta.
Depois, dê o feedback explicando o motivo com base nos materiais.
"""
        resposta_llm = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt_avaliacao}]
        )
        
        resposta = resposta_llm.choices[0].message.content
        
        # Reseta o estado para voltar a conversar normalmente
        estado_jarvis = "normal"
        pergunta_ativa = ""
        assunto_ativo = ""
        
        historico_chat.append({
            "role": "assistant",
            "content": resposta
        })
        
        return resposta

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
    # TAREFAS: ADICIONAR, EDITAR, LISTAR, CONCLUIR
    # =================================================

    # --- ADICIONAR TAREFA ---

    if ferramenta == "adicionar_tarefa":

        resposta = banco_dados.adicionar_tarefa(
            argumentos.get("descricao")
        )

    # --- EDITAR TAREFA ---

    elif ferramenta == "editar_tarefa":

        resposta = banco_dados.editar_tarefa(
            argumentos.get("id_tarefa"),
            argumentos.get("nova_descricao")
        )
        
    # --- LISTAR TAREFAS ---

    elif ferramenta == "listar_tarefas":

        resposta = banco_dados.listar_tarefas()

    # --- CONCLUIR TAREFA ---

    elif ferramenta == "concluir_tarefa":

        resposta = banco_dados.concluir_tarefa(
            argumentos.get("id_tarefa")
        )

    # =================================================
    # AGENDA: ADICIONAR, EDITAR, CONSULTAR, APAGAR
    # =================================================

    # --- AGENDA: ADICIONAR ---

    elif ferramenta == "adicionar_evento":
        resposta = banco_dados.adicionar_evento(
            argumentos.get("descricao"),
            argumentos.get("data")
        )

    # --- AGENDA: EDITAR ---

    elif ferramenta == "editar_evento":
        resposta = banco_dados.editar_evento(
            argumentos.get("id_evento"),
            argumentos.get("nova_descricao"),
            argumentos.get("nova_data")
        )

    # --- AGENDA: CONSULTAR ---

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

    # --- AGENDA: APAGAR ---

    elif ferramenta == "apagar_evento":
        resposta = banco_dados.apagar_evento(
            argumentos.get("id_evento")
        )

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

        estado_jarvis = "esperando_resposta"
        pergunta_ativa = resposta
        assunto_ativo = assunto

    # =================================================
    # PLANEJAMENTO DE ESTUDOS (Funcionalidade 3.4)
    # =================================================

    elif ferramenta == "planejar_estudos":
        
        assunto = argumentos.get("assunto")
        
        tarefas_pendentes = banco_dados.listar_tarefas()
        agenda_semana = banco_dados.consultar_agenda("semana")
        
        trechos_rag = "Nenhum material específico consultado (planejamento geral)."
        if assunto and str(assunto).lower() != "null":
            trechos_rag = rag.buscar_no_material(assunto)

        print("\n[LOG PLANO] Cruzando dados: Tarefas + Agenda + Materiais...\n")

        prompt = f"""
Você é um mentor acadêmico estratégico.

TAREFAS PENDENTES DO USUÁRIO:
{tarefas_pendentes}

AGENDA DA SEMANA DO USUÁRIO:
{agenda_semana}

MATERIAIS DE ESTUDO (RAG):
{trechos_rag}

O usuário pediu:
"{msg}"

Sua missão:
Crie um plano de ação claro e direto. Diga o que ele deve priorizar cruzando as tarefas com a agenda. Se houver materiais de estudo, use-os para dar dicas do que focar no conteúdo.
"""

        resposta_llm = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}]
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

import gradio as gr

# =====================================================
# INTERFACE GRADIO
# =====================================================

def responder(mensagem, historico):
    """
    Função que o Gradio chama a cada nova mensagem.
    'mensagem' é o que você digitou.
    'historico' é o que já foi falado (o Gradio gerencia isso).
    """
    # Chama a sua função original 'conversar' que processa a lógica
    resposta = conversar(mensagem)
    return resposta

# Configuração da interface estilo Chat
interface = gr.ChatInterface(
    fn=responder,
    title="Jarvis Acadêmico",
    description="Assistente para estudos e organização."
)

if __name__ == "__main__":
    print("Iniciando interface Gradio...")
    interface.launch()