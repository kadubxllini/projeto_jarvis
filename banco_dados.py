import sqlite3

def conectar():
    conn = sqlite3.connect('jarvis_academico.db')
    conn.row_factory = sqlite3.Row
    return conn

def inicializar_banco():
    conn = conectar()
    cursor = conn.cursor()
    # Tabela Tarefas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tarefas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            descricao TEXT NOT NULL,
            concluida BOOLEAN NOT NULL CHECK (concluida IN (0, 1)) DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

# --- FUNÇÕES DAS TAREFAS (Funcionalidade 3.3) ---

def adicionar_tarefa(descricao):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO tarefas (descricao) VALUES (?)', (descricao,))
    conn.commit()
    conn.close()
    return f"Tarefa '{descricao}' adicionada com sucesso."

def listar_tarefas():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM tarefas WHERE concluida = 0')
    tarefas = cursor.fetchall()
    conn.close()
    
    if not tarefas:
        return "Nenhuma tarefa pendente."
    
    lista = "Tarefas pendentes:\n"
    for t in tarefas:
        lista += f"ID: {t['id']} | {t['descricao']}\n"
    return lista

def concluir_tarefa(tarefa_id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('UPDATE tarefas SET concluida = 1 WHERE id = ?', (tarefa_id,))
    conn.commit()
    conn.close()
    return f"Tarefa {tarefa_id} marcada como concluída."

inicializar_banco()