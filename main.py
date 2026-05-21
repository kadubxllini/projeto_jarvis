from openai import OpenAI
import json
import banco_dados
import rag

# Conecta na IA (Gemma-3.12b-it) usando a API Key fornecida
client = OpenAI(
    base_url='https://llm.liaufms.org/v1/gemma-3-12b-it', 
    api_key='Cxt2ftLF7d3mHS2JdiFqB-eSDAQeZvFATPXPs02lV9A' 
)

# Explicando as ferramentas para a IA (o cardápio)
minhas_ferramentas = [
    {
        "type": "function",
        "function": {
            "name": "adicionar_tarefa",
            "description": "Adiciona uma nova tarefa na lista de afazeres do usuário.",
            "parameters": {
                "type": "object",
                "properties": {
                    "descricao": {
                        "type": "string",
                        "description": "A descrição da tarefa que precisa ser feita."
                    }
                },
                "required": ["descricao"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "listar_tarefas",
            "description": "Busca e lista todas as tarefas pendentes do usuário."
        }
    }
]

def conversar_com_jarvis(mensagem_usuario):
    
    prompt_sistema = """Você é o Jarvis. Você tem acesso ao banco de dados do usuário.
SE o usuário pedir para adicionar uma tarefa, responda com este JSON:
{"acao": "adicionar_tarefa", "descricao": "texto da tarefa"}
SE o usuário pedir para listar tarefas, responda com este JSON:
{"acao": "listar_tarefas"}
SE o usuário fizer perguntas sobre documentos, PDFs, materiais, filmes ou notas de avaliação, responda APENAS com este JSON:
{"acao": "buscar_material_rag", "pergunta": "a pergunta exata do usuário"}
Caso contrário, responda normalmente."""
    
    mensagens = [
        {"role": "system", "content": prompt_sistema},
        {"role": "user", "content": mensagem_usuario}
    ]

    resposta_ia = client.chat.completions.create(
        model='google/gemma-3-12b-it',
        messages=mensagens
    )

    retorno_texto = resposta_ia.choices[0].message.content.strip()

    # --- A MÁGICA NOVA ESTÁ AQUI ---
    # Procura onde começa o "{" e onde termina o "}" na resposta da IA
    inicio_json = retorno_texto.find("{")
    fim_json = retorno_texto.rfind("}")

    # Se ele achou as duas chaves na resposta...
    if inicio_json != -1 and fim_json != -1:
        # Extrai só a parte do texto que é o JSON
        trecho_json = retorno_texto[inicio_json:fim_json+1]
        
        try:
            argumentos = json.loads(trecho_json)
            nome_funcao = argumentos.get("acao")
            
            print(f"[LOG] A IA decidiu chamar a ferramenta: {nome_funcao}")
            
            if nome_funcao == "adicionar_tarefa":
                descricao = argumentos.get("descricao")
                resultado_ferramenta = banco_dados.adicionar_tarefa(descricao)
                print(f"[LOG] Resultado do banco:\n{resultado_ferramenta}")
                return "Ação executada com sucesso!"
                
            elif nome_funcao == "listar_tarefas":
                resultado_ferramenta = banco_dados.listar_tarefas()
                print(f"[LOG] Resultado do banco:\n{resultado_ferramenta}")
                return "Ação executada com sucesso!"
            
            elif nome_funcao == "buscar_material_rag":
                pergunta = argumentos.get("pergunta")
                
                trechos_encontrados = rag.buscar_no_material(pergunta)
                print(f"[LOG] Trechos recuperados:\n{trechos_encontrados[:300]}...\n")
                
                prompt_rag = f"Baseado ÚNICA E EXCLUSIVAMENTE nestes trechos do material:\n{trechos_encontrados}\n\nResponda à pergunta: {pergunta}"
                
                resposta_final = client.chat.completions.create(
                    model='google/gemma-3-12b-it',
                    messages=[{"role": "user", "content": prompt_rag}]
                )
                return f"Jarvis: {resposta_final.choices[0].message.content}"
                
        except json.JSONDecodeError:
            pass
            
    # Se não tinha JSON ou deu erro, devolve o que a IA falou
    return f"Jarvis: {retorno_texto}"

# --- EXECUTANDO O JARVIS ---
if __name__ == "__main__":
    print("Jarvis iniciado! (Digite 'sair' para encerrar)")
    
    while True:
        # Fica aguardando você digitar algo no terminal
        texto_usuario = input("\nVocê: ")
        
        # Condição para parar o loop e fechar o programa
        if texto_usuario.lower() == 'sair':
            print("Encerrando o Jarvis...")
            break
            
        # Envia o que você digitou para a IA e imprime a resposta
        resposta = conversar_com_jarvis(texto_usuario)
        print(resposta)