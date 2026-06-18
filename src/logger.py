import datetime

# =====================================================
# REGISTRO DE LOGS
# =====================================================

def registrar_log(ferramenta, entrada, saida):
    agora = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open("logs.txt", "a", encoding="utf-8") as f:
        f.write(f"[{agora}]\n")
        f.write(f"FERRAMENTA: {ferramenta}\n")
        f.write(f"ENTRADA: {entrada}\n")
        f.write(f"SAÍDA: {saida}\n")
        f.write("-" * 80 + "\n")