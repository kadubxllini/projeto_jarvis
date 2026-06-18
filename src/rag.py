import os
import json
from pypdf import PdfReader
import chromadb

# =====================================================
# CONFIGURAÇÃO DO CHROMA
# =====================================================

PASTA_DADOS = os.path.join(os.path.dirname(__file__), '..', 'data')
INDICE_PATH = os.path.join(PASTA_DADOS, '.rag_index.json')

chroma_client = chromadb.PersistentClient(path=os.path.join(os.path.dirname(__file__), '..', 'data', 'chroma_db'))
colecao = chroma_client.get_or_create_collection(name="materiais_estudo")

# =====================================================
# FUNÇÕES INTERNAS
# =====================================================

def _carregar_indice():
    """Carrega o índice de arquivos já processados (nome -> timestamp)."""
    if os.path.exists(INDICE_PATH):
        with open(INDICE_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def _salvar_indice(indice):
    """Salva o índice atualizado no disco."""
    with open(INDICE_PATH, 'w', encoding='utf-8') as f:
        json.dump(indice, f, indent=2)

def _processar_pdf(nome_arquivo):
    """Lê um PDF, divide em chunks e indexa no ChromaDB."""
    caminho = os.path.join(PASTA_DADOS, nome_arquivo)

    print(f"[RAG] Processando: {nome_arquivo}...")
    leitor = PdfReader(caminho, strict=False)
    texto_completo = ""
    for pagina in leitor.pages:
        if pagina.extract_text():
            texto_completo += pagina.extract_text() + "\n"

    tamanho_chunk = 1000
    chunks = [texto_completo[i:i + tamanho_chunk] for i in range(0, len(texto_completo), tamanho_chunk)]

    if not chunks:
        print(f"[RAG] Aviso: nenhum texto extraído de {nome_arquivo}.")
        return 0

    ids = [f"{nome_arquivo}_chunk_{i}" for i in range(len(chunks))]
    metadados = [{"fonte": nome_arquivo} for _ in range(len(chunks))]

    colecao.upsert(
        documents=chunks,
        metadatas=metadados,
        ids=ids
    )

    print(f"[RAG] {nome_arquivo} indexado em {len(chunks)} partes.")
    return len(chunks)

# =====================================================
# SINCRONIZAÇÃO AUTOMÁTICA
# =====================================================

def sincronizar_pdfs():
    """
    Verifica a pasta data/ e processa apenas PDFs novos ou modificados.
    Compara o timestamp de modificação de cada arquivo com o índice salvo.
    """
    if not os.path.exists(PASTA_DADOS):
        print(f"[RAG] Pasta 'data/' não encontrada. Crie-a e adicione PDFs.")
        return

    pdfs_disponiveis = [f for f in os.listdir(PASTA_DADOS) if f.endswith('.pdf')]

    if not pdfs_disponiveis:
        print("[RAG] Nenhum PDF encontrado em 'data/'. Nada a indexar.")
        return

    indice = _carregar_indice()
    pdfs_atualizados = 0

    for nome_pdf in pdfs_disponiveis:
        caminho = os.path.join(PASTA_DADOS, nome_pdf)
        mtime_atual = os.path.getmtime(caminho)
        mtime_salvo = indice.get(nome_pdf)

        if mtime_salvo is None:
            print(f"[RAG] Novo arquivo detectado: {nome_pdf}")
            _processar_pdf(nome_pdf)
            indice[nome_pdf] = mtime_atual
            pdfs_atualizados += 1

        elif mtime_atual != mtime_salvo:
            print(f"[RAG] Arquivo modificado detectado: {nome_pdf}")
            _processar_pdf(nome_pdf)
            indice[nome_pdf] = mtime_atual
            pdfs_atualizados += 1

        else:
            print(f"[RAG] Sem mudanças: {nome_pdf} (já indexado)")

    if pdfs_atualizados > 0:
        _salvar_indice(indice)
        print(f"[RAG] Sincronização concluída. {pdfs_atualizados} arquivo(s) atualizado(s).")
    else:
        print("[RAG] Todos os PDFs já estão atualizados.")

# =====================================================
# BUSCA NO MATERIAL
# =====================================================

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