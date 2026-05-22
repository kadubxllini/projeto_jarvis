from openai import OpenAI
import json
import banco_dados
import rag

# Conecta na IA (Gemma-3.12b-it) usando a API Key fornecida
client = OpenAI(
    base_url='https://llm.liaufms.org/v1/gemma-3-12b-it',
    api_key='Cxt2ftLF7d3mHS2JdiFqB-eSDAQeZvFATPXPs02lV9A'
)

# --- 1. O CARDÁPIO COMPLETO DE FERRAMENTAS ---
minhas_ferramentas = [
    {
        "type": "function",
        "function": {
            "name": "adicionar_tarefa",
            "description": "Adiciona uma nova tarefa na lista de afazeres.",
            "parameters": {
                "type": "object",
                "properties": {"descricao": {"type": "string"}},
                "required": ["descricao"]
            }
        }
    },
    {
        "type": "function",
        "function": {"name": "listar_tarefas", "description": "Busca e lista todas as tarefas pendentes."}
    },
    {
        "type": "function",
        "function": {
            "name": "concluir_tarefa",
            "description": "Marca uma tarefa como concluída pelo seu ID.",
            "parameters": {
                "type": "object",
                "properties": {"id_tarefa": {"type": "string"}},
                "required": ["id_tarefa"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "buscar_material_rag",
            "description": "Busca informações ou explicações nos materiais/PDFs do usuário.",
            "parameters": {
                "type": "object",
                "properties": {"pergunta": {"type": "string"}},
                "required": ["pergunta"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "gerar_exercicios",
            "description": "Gera exercícios de múltipla escolha sobre um assunto.",
            "parameters": {
                "type": "object",
                "properties": {"assunto": {"type": "string"}},
                "required": ["assunto"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "fazer_pergunta",
            "description": "Elabora uma pergunta para testar o conhecimento do usuário (Active Recall).",
            "parameters": {
                "type": "object",
                "properties": {"assunto": {"type": "string"}},
                "required": ["assunto"]
            }
        }
    }
]

# --- 2. CONFIGURAÇÃO DA MEMÓRIA ---
prompt_sistema = """Você é o Jarvis, um assistente acadêmico. Você responde a perguntas baseadas nos materiais do usuário e o auxilia com suas tarefas.
REGRA DE AVALIAÇÃO (ACTIVE RECALL):
Se você acabou de fazer uma pergunta para o usuário e ele respondeu, aja como um professor. Avalie a resposta dele, diga se ele acertou ou errou, e explique o conceito correto."""

historico_chat = [
    {"role": "system", "content": prompt_sistema}
]

def conversar_com_jarvis(mensagem_usuario):
    global historico_chat
    
    historico_chat.append({"role": "user", "content": mensagem_usuario})

    # --- ROTEADOR (O Backend decide a Tool) ---
    prompt_roteador = """Analise a última mensagem do usuário. Escolha APENAS UMA das opções abaixo que melhor descreve a intenção dele:
    - adicionar_tarefa
    - listar_tarefas
    - concluir_tarefa
    - buscar_material_rag
    - gerar_exercicios
    - fazer_pergunta
    - nenhuma

    Responda APENAS com o nome exato da opção, sem aspas, pontos ou textos adicionais."""

    resposta_roteador = client.chat.completions.create(
        model='google/gemma-3-12b-it',
        messages=[{"role": "system", "content": prompt_roteador}, {"role": "user", "content": mensagem_usuario}],
        temperature=0.0 # Condição pro roteador não inventar respostas
    )
    
    ferramenta_escolhida = resposta_roteador.choices[0].message.content.strip().lower()
    
    ferramentas_validas = ["adicionar_tarefa", "listar_tarefas", "concluir_tarefa", "buscar_material_rag", "gerar_exercicios", "fazer_pergunta"]

    # --- NAMED FUNCTION CALLING ---
    if ferramenta_escolhida in ferramentas_validas:
        print(f"[LOG] Roteador ativou o Named Function Calling para: {ferramenta_escolhida}")
        
        resposta_parametros = client.chat.completions.create(
            model='google/gemma-3-12b-it',
            messages=historico_chat,
            tools=minhas_ferramentas,
            tool_choice={"type": "function", "function": {"name": ferramenta_escolhida}}
        )

        tool_call = resposta_parametros.choices[0].message.tool_calls[0]
        
        argumentos = json.loads(tool_call.function.arguments) if tool_call.function.arguments else {}

        # --- EXECUTA A AÇÃO NO PYTHON ---
        if ferramenta_escolhida == "adicionar_tarefa":
            resultado = banco_dados.adicionar_tarefa(argumentos.get("descricao"))
            resposta_final = f"Jarvis: {resultado}"
            
        elif ferramenta_escolhida == "listar_tarefas":
            resultado = banco_dados.listar_tarefas()
            resposta_final = f"Jarvis:\n{resultado}"
            
        elif ferramenta_escolhida == "concluir_tarefa":
            resultado = banco_dados.concluir_tarefa(argumentos.get("id_tarefa"))
            resposta_final = f"Jarvis: {resultado}"
            
        elif ferramenta_escolhida == "buscar_material_rag":
            pergunta = argumentos.get("pergunta")
            trechos = rag.buscar_no_material(pergunta)
            print(f"[LOG] Trechos recuperados:\n{trechos[:300]}...\n")
            prompt_rag = f"Baseado ÚNICA E EXCLUSIVAMENTE nestes trechos do material:\n{trechos}\n\nResponda à pergunta: {pergunta}"
            resposta_rag = client.chat.completions.create(model='google/gemma-3-12b-it', messages=[{"role": "user", "content": prompt_rag}])
            resposta_final = f"Jarvis: {resposta_rag.choices[0].message.content}"

        elif ferramenta_escolhida == "gerar_exercicios":
            assunto = argumentos.get("assunto")
            trechos = rag.buscar_no_material(assunto)
            prompt_rag = f"Baseado nestes trechos:\n{trechos}\n\nCrie 3 exercícios de múltipla escolha sobre '{assunto}'. Coloque o gabarito no final."
            resposta_rag = client.chat.completions.create(model='google/gemma-3-12b-it', messages=[{"role": "user", "content": prompt_rag}])
            resposta_final = f"Jarvis:\n{resposta_rag.choices[0].message.content}"

        elif ferramenta_escolhida == "fazer_pergunta":
            assunto = argumentos.get("assunto")
            trechos = rag.buscar_no_material(assunto)
            prompt_rag = f"Baseado nestes trechos:\n{trechos}\n\nFaça UMA pergunta direta para testar o conhecimento do usuário sobre '{assunto}'. NÃO dê a resposta."
            resposta_rag = client.chat.completions.create(model='google/gemma-3-12b-it', messages=[{"role": "user", "content": prompt_rag}])
            resposta_final = f"Jarvis:\n{resposta_rag.choices[0].message.content}"

        # Salva na memória e imprime
        historico_chat.append({"role": "assistant", "content": resposta_final})
        return resposta_final

    # --- BATE-PAPO NORMAL OU AVALIAÇÃO DE RESPOSTA ---
    else:
        print("\n[LOG] Nenhuma ferramenta ativada. Gerando resposta em texto livre...\n")
        resposta_normal = client.chat.completions.create(
            model='google/gemma-3-12b-it',
            messages=historico_chat
        )
        texto_livre = resposta_normal.choices[0].message.content
        historico_chat.append({"role": "assistant", "content": texto_livre})
        return f"Jarvis: {texto_livre}"

# --- EXECUTANDO O JARVIS ---
if __name__ == "__main__":
    print("Jarvis iniciado! (Digite 'sair' para encerrar)")
    
    while True:
        texto_usuario = input("\nVocê: ")
        
        if texto_usuario.lower() == 'sair':
            print("Encerrando o Jarvis...")
            break

        resposta = conversar_com_jarvis(texto_usuario)
        print(resposta)