import os
from pypdf import PdfReader
import chromadb

# Salvando no disco local (ou /tmp/) para evitar database is locked
chroma_client = chromadb.PersistentClient(path="/tmp/chroma_db_jarvis")
colecao = chroma_client.get_or_create_collection(name="materiais_estudo")

def processar_pdf(nome_arquivo):
    caminho = f"./data/{nome_arquivo}"
    
    print(f"Lendo o PDF: {nome_arquivo}...")
    # strict=False ignora erros de arquivos corrompidos
    leitor = PdfReader(caminho, strict=False)
    texto_completo = ""
    for pagina in leitor.pages:
        if pagina.extract_text():
            texto_completo += pagina.extract_text() + "\n"
            
    tamanho_chunk = 1000
    chunks = [texto_completo[i:i+tamanho_chunk] for i in range(0, len(texto_completo), tamanho_chunk)]
    
    ids = [f"{nome_arquivo}_chunk_{i}" for i in range(len(chunks))]
    # Metadados para carimbar o nome do arquivo
    metadados = [{"fonte": nome_arquivo} for _ in range(len(chunks))]
    
    colecao.upsert(
        documents=chunks,
        metadatas=metadados,
        ids=ids
    )
    return f"Sucesso! {nome_arquivo} foi dividido em {len(chunks)} partes."

def buscar_no_material(pergunta):
    resultados = colecao.query(
        query_texts=[pergunta],
        n_results=2
    )
    
    textos_formatados = []
    
    if resultados['documents'] and len(resultados['documents'][0]) > 0:
        for i in range(len(resultados['documents'][0])):
            texto = resultados['documents'][0][i]
            fonte = resultados['metadatas'][0][i].get('fonte', 'Desconhecida')
            
            pedaco_completo = f"[Arquivo: {fonte}]\n{texto}"
            textos_formatados.append(pedaco_completo)

        return "\n\n".join(textos_formatados)
        
    return "Nenhum material relevante encontrado."

if __name__ == "__main__":    
    pasta_dados = "./data"
    
    if not os.path.exists(pasta_dados):
        print(f"Pasta '{pasta_dados}' não encontrada. Coloque seus PDFs dentro da pasta 'data'.")
    else:
        pdfs = [arquivo for arquivo in os.listdir(pasta_dados) if arquivo.endswith('.pdf')]
        
        if not pdfs:
            print("Nenhum PDF encontrado na pasta 'data'.")
        else:
            print(f"Encontrados {len(pdfs)} PDFs. Iniciando processamento...\n")
            for pdf in pdfs:
                print(processar_pdf(pdf))
                
            print("\nBanco vetorial alimentado com sucesso! Agora você pode rodar o main.py")