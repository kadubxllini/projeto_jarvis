import os
import datetime

LOGS_PATH = os.path.join(os.path.dirname(__file__), '..', 'logs', 'logs.txt')

def registrar_log(ferramenta, entrada, saida, rag_info=None):
    os.makedirs(os.path.dirname(LOGS_PATH), exist_ok=True)
    agora = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    log_texto = f"[{agora}]\n"
    log_texto += f"FERRAMENTA: {ferramenta}\n"
    log_texto += f"ENTRADA: {entrada}\n"
    
    # Se foi usado RAG
    if rag_info and rag_info != "Nenhum material específico consultado (planejamento geral).":
        log_texto += "\n\n" + "<" * 80 + "\n"
        log_texto += f"RAG: {rag_info}\n"
        log_texto += ">" * 80 + "\n\n\n"
        
    log_texto += f"SAÍDA: {saida}\n"
    log_texto += "-" * 80 + "\n\n"
    
    with open(LOGS_PATH, "a", encoding="utf-8") as f:
        f.write(log_texto)
    
    print(log_texto)