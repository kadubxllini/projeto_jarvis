import os
from pypdf import PdfReader
import chromadb

chroma_client = chromadb.PersistentClient(path="./chroma_db")
colecao = chroma_client.get_or_create_collection(name="materiais_estudo")

def processar_pdf(nome_arquivo):
    caminho = f"./data/{nome_arquivo}"
    
    print(f"Lendo o PDF: {nome_arquivo}...")
    leitor = PdfReader(caminho)
    texto_completo = ""
    for pagina in leitor.pages:
        if pagina.extract_text():
            texto_completo += pagina.extract_text() + "\n"
            
    # Dividindo o texto em chunks para o Chroma
    tamanho_chunk = 1000
    chunks = [texto_completo[i:i+tamanho_chunk] for i in range(0, len(texto_completo), tamanho_chunk)]
    
    # Criando IDs únicos para cada chunk
    ids = [f"{nome_arquivo}_chunk_{i}" for i in range(len(chunks))]
    
   # Armazenando os chunks no Chroma
    colecao.add(
        documents=chunks,
        ids=ids
    )
    return f"Sucesso! {nome_arquivo} foi dividido em {len(chunks)} partes."

def buscar_no_material(pergunta):
    # O Chroma pega a sua pergunta, transforma em vetor e acha os pedaços mais parecidos
    resultados = colecao.query(
        query_texts=[pergunta],
        n_results=2 # Traz os 2 pedaços mais relevantes
    )
    
    # Retorna os trechos encontrados
    if resultados['documents'] and resultados['documents'][0]:
         return "\n---\n".join(resultados['documents'][0])
    return "Nenhum material relevante encontrado."

# --- TESTANDO O RAG ---
# --- ALIMENTANDO O BANCO VETORIAL ---
if __name__ == "__main__":    
    pasta_dados = "./data"
    
    # Verifica se a pasta existe
    if not os.path.exists(pasta_dados):
        print(f"Pasta '{pasta_dados}' não encontrada. Coloque seus PDFs dentro da pasta 'data'.")
    else:
        pdfs = [arquivo for arquivo in os.listdir(pasta_dados) if arquivo.endswith('.pdf')]
        
        if not pdfs:
            print("Nenhum PDF encontrado na pasta 'data'.")
        else:
            print(f"Encontrados {len(pdfs)} PDFs. Iniciando processamento...\n")
            # Roda a função para cada PDF encontrado
            for pdf in pdfs:
                print(processar_pdf(pdf))
                
            print("\nBanco vetorial alimentado com sucesso! Agora você pode rodar o main.py")