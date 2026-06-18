import os
import datetime

LOGS_PATH = os.path.join(os.path.dirname(__file__), '..', 'logs', 'logs.txt')

def registrar_log(ferramenta, entrada, saida):
    os.makedirs(os.path.dirname(LOGS_PATH), exist_ok=True)
    agora = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(LOGS_PATH, "a", encoding="utf-8") as f:
        f.write(f"[{agora}]\n")
        f.write(f"FERRAMENTA: {ferramenta}\n")
        f.write(f"ENTRADA: {entrada}\n")
        f.write(f"SAÍDA: {saida}\n")
        f.write("-" * 80 + "\n")