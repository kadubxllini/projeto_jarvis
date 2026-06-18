from openai import OpenAI
import json
import datetime
import os
from dotenv import load_dotenv

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
# IA ESCOLHE A FERRAMENTA
# =====================================================

def escolher_ferramenta(msg, historico_chat):

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
- Perguntas sobre o que tem na agenda, eventos, compromissos, provas ou "o que tenho hoje/amanhã/essa semana" -> consultar_agenda

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

    return ferramenta

# =====================================================
# EXTRAÇÃO DOS ARGUMENTOS
# =====================================================

def extrair_argumentos(ferramenta, msg):

    data_hoje = datetime.date.today().strftime('%d-%m-%Y')

    exemplos = {
        "adicionar_tarefa": '{"descricao": "<texto da tarefa extraído da mensagem>"}',
        "editar_tarefa": '{"id_tarefa": "<número do id>", "nova_descricao": "<novo texto da tarefa>"}',
        "listar_tarefas": '{}',
        "concluir_tarefa": '{"id_tarefa": "<número do id extraído da mensagem>"}',
        "adicionar_evento": '{"descricao": "<descrição do evento>", "data": "<data no formato DD-MM-YYYY>"}',
        "editar_evento": '{"id_evento": "<número do id>", "nova_descricao": "<novo texto ou null se não mudar>", "nova_data": "<nova data DD-MM-YYYY ou null se não mudar>"}',
        "consultar_agenda": '{"data_inicio": "<DD-MM-YYYY ou null>", "data_fim": "<DD-MM-YYYY ou null>"}',
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

        return json.loads(texto)

    except Exception as e:

        return None