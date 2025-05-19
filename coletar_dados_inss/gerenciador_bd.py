import sqlite3
import json

def criar_tabela():
    """Cria a tabela de clientes no banco de dados SQLite se ela não existir."""
    try:
        conn = sqlite3.connect('clientes.db')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clientes (
                codigo_cliente TEXT UNIQUE,
                nome TEXT,
                telefone1 TEXT,
                telefone2 TEXT,
                telefone3 TEXT,
                email TEXT,
                cidade TEXT,
                estado TEXT,
                produtos TEXT
            )
        ''')
        conn.commit()
        print("Tabela 'clientes' criada ou já existente.")
    except sqlite3.Error as e:
        print(f"Erro ao criar tabela: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    criar_tabela()