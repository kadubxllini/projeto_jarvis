from openai import OpenAI
import os
import datetime
from dotenv import load_dotenv
import src.database as database
import src.rag as rag
from src.tools import escolher_ferramenta, extrair_argumentos
from src.logger import registrar_log

# =====================================================
# CONFIGURAÇÃO DO CLIENTE
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
        
        registrar_log("avaliar_resposta_active_recall", msg, resposta)
        
        return resposta

    ferramenta = escolher_ferramenta(msg, historico_chat)

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

        registrar_log(ferramenta, msg, texto)

        return texto

    # =================================================
    # EXTRAÇÃO DOS ARGUMENTOS
    # =================================================

    argumentos = extrair_argumentos(ferramenta, msg)

    if argumentos is None:
        return "Erro ao gerar argumentos."

    trechos_usados = None

    # =================================================
    # TAREFAS: ADICIONAR, EDITAR, LISTAR, CONCLUIR
    # =================================================

    # --- ADICIONAR TAREFA ---

    if ferramenta == "adicionar_tarefa":

        resposta = database.adicionar_tarefa(
            argumentos.get("descricao")
        )

    # --- EDITAR TAREFA ---

    elif ferramenta == "editar_tarefa":

        resposta = database.editar_tarefa(
            argumentos.get("id_tarefa"),
            argumentos.get("nova_descricao")
        )
        
    # --- LISTAR TAREFAS ---

    elif ferramenta == "listar_tarefas":

        resposta = database.listar_tarefas()

    # --- CONCLUIR TAREFA ---

    elif ferramenta == "concluir_tarefa":

        resposta = database.concluir_tarefa(
            argumentos.get("id_tarefa")
        )

    # =================================================
    # AGENDA: ADICIONAR, EDITAR, CONSULTAR, APAGAR
    # =================================================

    # --- AGENDA: ADICIONAR ---

    elif ferramenta == "adicionar_evento":
        resposta = database.adicionar_evento(
            argumentos.get("descricao"),
            argumentos.get("data")
        )

    # --- AGENDA: EDITAR ---

    elif ferramenta == "editar_evento":
        resposta = database.editar_evento(
            argumentos.get("id_evento"),
            argumentos.get("nova_descricao"),
            argumentos.get("nova_data")
        )

    # --- AGENDA: CONSULTAR ---

    elif ferramenta == "consultar_agenda":
        data_inicio = argumentos.get("data_inicio")
        data_fim = argumentos.get("data_fim")
        
        dados_brutos = database.consultar_agenda(data_inicio, data_fim)

        prompt = f"""
Baseado nos dados do banco de dados:
{dados_brutos}

Sua resposta deve ser APENAS a listagem dos eventos encontrados. 
Formate cada item estritamente no padrão abaixo, uma linha por evento, sem saudações ou explicações:
ID: número | Data: YYYY-MM-DD | O que: descrição do evento

Se o banco de dados indicar que não há eventos ou estiver vazio, responda apenas: 
Nenhum evento encontrado.
"""
        resposta_llm = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}]
        )
        resposta = resposta_llm.choices[0].message.content

    # --- AGENDA: APAGAR ---

    elif ferramenta == "apagar_evento":
        resposta = database.apagar_evento(
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
        trechos_usados = trechos

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
        trechos_usados = trechos

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
        trechos_usados = trechos

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
    # PLANEJAMENTO DE ESTUDOS
    # =================================================

    elif ferramenta == "planejar_estudos":
        
        assunto = argumentos.get("assunto")
        
        tarefas_pendentes = database.listar_tarefas()
        
        hoje = datetime.date.today()
        fim_semana = hoje + datetime.timedelta(days=7)
        agenda_semana = database.consultar_agenda(
            hoje.strftime('%Y-%m-%d'),
            fim_semana.strftime('%Y-%m-%d')
        )
        
        trechos_rag = "Nenhum material específico consultado (planejamento geral)."
        if assunto and str(assunto).lower() != "null":
            trechos_rag = rag.buscar_no_material(assunto)
            trechos_usados = trechos

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
    # SALVA NA MEMÓRIA E NO LOG
    # =================================================

    historico_chat.append({
        "role": "assistant",
        "content": resposta
    })

    registrar_log(ferramenta, msg, resposta, trechos_usados)

    return resposta