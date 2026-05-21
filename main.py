from openai import OpenAI

# Substitua a api_key pelo token completo que o professor forneceu, caso esse da print esteja cortado
client = OpenAI(
    base_url='https://llm.liaufms.org/v1/gemma-3-12b-it', 
    api_key='Cxt2ftLF7d3mHS2JdiFqB-eSDAQeZvFATPXPs02lV9A' 
)

print("Tentando conectar com o Jarvis...")

resp = client.chat.completions.create(
    model='google/gemma-3-12b-it',
    messages=[{'role': 'user', 'content': 'Oi, Jarvis! Está me ouvindo? Responda em uma frase.'}]
)

print("\nResposta do Jarvis:")
print(resp.choices[0].message.content)