"""Regressions for persistent tasks and agenda, without an AI provider."""
import sqlite3
import importlib.util
from contextlib import closing
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

# The package initializer starts the AI imports. Load the persistence module on
# its own so these regressions never require credentials or a model download.
spec = importlib.util.spec_from_file_location('jarvis_database', Path(__file__).resolve().parents[1] / 'src' / 'database.py')
database = importlib.util.module_from_spec(spec)
spec.loader.exec_module(database)


class DatabaseTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = str(Path(self.temp.name) / 'jarvis.db')
        self.override = patch.object(database, 'DB_PATH', self.path)
        self.override.start()
        self.addCleanup(self.override.stop)
        database.inicializar_banco()

    def row(self, query, args=()):
        with closing(sqlite3.connect(self.path)) as conn:
            return conn.execute(query, args).fetchone()

    def test_task_edit_and_completion_persist(self):
        database.adicionar_tarefa('Revisar SQL')
        task_id = self.row('SELECT id FROM tarefas')[0]
        database.editar_tarefa(task_id, 'Revisar joins')
        self.assertIn('Revisar joins', database.listar_tarefas())
        database.concluir_tarefa(task_id)
        self.assertNotIn('Revisar joins', database.listar_tarefas())
        self.assertEqual(self.row('SELECT descricao, concluida FROM tarefas'), ('Revisar joins', 1))

    def test_user_text_is_saved_without_becoming_sql(self):
        text = "Estudar 'joins'; DROP TABLE tarefas; --"
        database.adicionar_tarefa(text)
        self.assertEqual(self.row('SELECT descricao FROM tarefas')[0], text)
        database.adicionar_tarefa('Outra tarefa')
        self.assertEqual(self.row('SELECT count(*) FROM tarefas')[0], 2)

    def test_agenda_edit_query_and_delete(self):
        database.adicionar_evento('Prova', '20-11-2026')
        event_id = self.row('SELECT id FROM agenda')[0]
        database.editar_evento(event_id, nova_data='21-11-2026')
        self.assertIn('Prova', database.consultar_agenda('21-11-2026'))
        self.assertNotIn('Prova', database.consultar_agenda('20-11-2026'))
        database.editar_evento(event_id, nova_descricao='Prova de SQL')
        self.assertEqual(self.row('SELECT descricao, data FROM agenda'), ('Prova de SQL', '21-11-2026'))
        database.apagar_evento(event_id)
        self.assertEqual(self.row('SELECT count(*) FROM agenda')[0], 0)

    def test_initialization_preserves_existing_records(self):
        database.adicionar_tarefa('Manter tarefa')
        database.inicializar_banco()
        self.assertEqual(self.row('SELECT count(*) FROM tarefas')[0], 1)

    def test_edit_missing_event_does_not_create_one(self):
        self.assertIn('não encontrado', database.editar_evento(999, nova_descricao='Ausente'))
        self.assertEqual(self.row('SELECT count(*) FROM agenda')[0], 0)
