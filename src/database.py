import sqlite3
import datetime
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'jarvis_academico.db')

def conectar():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# --- CRIAÇÃO DO BANCO DE DADOS ---
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
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS agenda (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            descricao TEXT NOT NULL,
            data DATE NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# --- FUNÇÕES DA AGENDA (Funcionalidade 3.2) ---

def adicionar_evento(descricao, data):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO agenda (descricao, data) VALUES (?, ?)', (descricao, data))
    conn.commit()
    conn.close()
    return f"Evento '{descricao}' agendado para {data}."

def editar_evento(evento_id, nova_descricao=None, nova_data=None):
    conn = conectar()
    cursor = conn.cursor()
    
    cursor.execute('SELECT descricao, data FROM agenda WHERE id = ?', (evento_id,))
    evento_atual = cursor.fetchone()
    
    if not evento_atual:
        conn.close()
        return f"Erro: Evento {evento_id} não encontrado."
        
    desc = nova_descricao if nova_descricao else evento_atual['descricao']
    dt = nova_data if nova_data else evento_atual['data']
    
    cursor.execute('UPDATE agenda SET descricao = ?, data = ? WHERE id = ?', (desc, dt, evento_id))
    conn.commit()
    conn.close()
    return f"Evento {evento_id} atualizado para: '{desc}' no dia {dt}."

def consultar_agenda(data_inicio=None, data_fim=None):
    conn = conectar()
    cursor = conn.cursor()

    if not data_inicio:
        hoje_str = datetime.date.today().strftime('%d-%m-%Y')
        cursor.execute('SELECT * FROM agenda WHERE data >= ? ORDER BY data ASC', (hoje_str,))
    elif data_fim:
        cursor.execute('SELECT * FROM agenda WHERE data BETWEEN ? AND ? ORDER BY data ASC', (data_inicio, data_fim))
    else:
        cursor.execute('SELECT * FROM agenda WHERE data = ? ORDER BY data ASC', (data_inicio,))

    eventos = cursor.fetchall()
    conn.close()

    if not eventos:
        return "Nenhum evento encontrado no banco."
    
    lista = "Eventos encontrados:\n"
    for e in eventos:
        lista += f"- ID: {e['id']} | Data: {e['data']} | O que: {e['descricao']}\n"
    return lista

def apagar_evento(evento_id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM agenda WHERE id = ?', (evento_id,))
    conn.commit()
    conn.close()
    return f"Evento {evento_id} apagado com sucesso da agenda."

# --- FUNÇÕES DAS TAREFAS (Funcionalidade 3.3) ---

def adicionar_tarefa(descricao):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO tarefas (descricao) VALUES (?)', (descricao,))
    conn.commit()
    conn.close()
    return f"Tarefa '{descricao}' adicionada com sucesso."

def editar_tarefa(tarefa_id, nova_descricao):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('UPDATE tarefas SET descricao = ? WHERE id = ?', (nova_descricao, tarefa_id))
    conn.commit()
    conn.close()
    return f"Tarefa {tarefa_id} atualizada para: '{nova_descricao}'."

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