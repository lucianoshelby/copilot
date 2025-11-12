# gerenciador_db.py

import psycopg2
from psycopg2 import sql # Para construir queries SQL de forma segura, se necessário
from psycopg2.extras import DictCursor # Para retornar linhas como dicionários
import json # Para parsear a string JSON de produtos
import base64 # Para decodificar a senha do banco de dados
import os

# --- Configurações do Banco de Dados ---
# Mantenha suas credenciais seguras. Em um projeto real, use variáveis de ambiente.
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "banco_de_clientes" # O nome do banco que você criou
DB_USER = "postgres" # O usuário padrão que você usou na instalação
DB_PASS_B64 = "QFNoYWRheTIyNDg="
DB_PASS =  base64.b64decode(DB_PASS_B64)

def get_db_connection():
    """Estabelece e retorna uma conexão com o banco de dados."""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASS
        )
        return conn
    except psycopg2.Error as e:
        print(f"Erro ao conectar ao PostgreSQL: {e}")
        return None

def salvar_dados_clientes(lista_de_clientes_dict):
    """
    Salva uma lista de clientes no banco de dados.
    Se um cliente com o mesmo 'codigo_cliente' já existir, seus dados são atualizados.
    A lista de produtos é substituída pela nova lista fornecida.
    """
    conn = get_db_connection()
    if not conn:
        print("Não foi possível conectar ao banco de dados.")
        return False

    sucesso_geral = True
    clientes_processados = 0
    clientes_com_erro = []

    for cliente_data in lista_de_clientes_dict:
        try:
            with conn.cursor() as cur:
                # Início da transação para este cliente
                # 1. Inserir ou atualizar o cliente na tabela Clientes
                query_cliente = sql.SQL("""
                    INSERT INTO Clientes (
                        codigo_cliente_original, nome, telefone1, telefone2, telefone3,
                        email, cidade, estado
                    ) VALUES (
                        %(codigo_cliente)s, %(nome)s, %(telefone1)s, %(telefone2)s, %(telefone3)s,
                        %(email)s, %(cidade)s, %(estado)s
                    )
                    ON CONFLICT (codigo_cliente_original) DO UPDATE SET
                        nome = EXCLUDED.nome,
                        telefone1 = EXCLUDED.telefone1,
                        telefone2 = EXCLUDED.telefone2,
                        telefone3 = EXCLUDED.telefone3,
                        email = EXCLUDED.email,
                        cidade = EXCLUDED.cidade,
                        estado = EXCLUDED.estado,
                        data_atualizacao = CURRENT_TIMESTAMP
                    RETURNING id;
                """)
                cur.execute(query_cliente, cliente_data)
                cliente_id_db = cur.fetchone()[0] # Pega o ID do cliente inserido/atualizado

                # 2. Processar a lista de produtos
                if cliente_id_db and 'produtos' in cliente_data and cliente_data['produtos']:
                    try:
                        # A lista de produtos vem como uma string JSON, precisamos parseá-la
                        lista_produtos_str = cliente_data['produtos']
                        # Adicionar tratamento para caso já seja uma lista (embora seu exemplo mostre string)
                        if isinstance(lista_produtos_str, str):
                            lista_codigos_produtos = json.loads(lista_produtos_str)
                        elif isinstance(lista_produtos_str, list):
                            lista_codigos_produtos = lista_produtos_str
                        else:
                            lista_codigos_produtos = []
                            print(f"WARN: Formato de produtos inesperado para {cliente_data.get('codigo_cliente')}: {type(lista_produtos_str)}")

                    except json.JSONDecodeError as e:
                        print(f"Erro ao decodificar JSON de produtos para o cliente {cliente_data.get('codigo_cliente')}: {e}")
                        print(f"String JSON problemática: {cliente_data['produtos']}")
                        lista_codigos_produtos = []
                        # Você pode querer tratar esse erro de forma diferente, talvez pulando o cliente

                    if lista_codigos_produtos:
                        # Remover produtos antigos associados a este cliente para garantir que a nova lista substitua a antiga
                        cur.execute("DELETE FROM Clientes_Produtos WHERE cliente_id = %s;", (cliente_id_db,))

                        # Inserir os novos produtos
                        query_insert_produto = sql.SQL("""
                            INSERT INTO Clientes_Produtos (cliente_id, codigo_produto_adquirido)
                            VALUES (%s, %s)
                            ON CONFLICT (cliente_id, codigo_produto_adquirido) DO NOTHING;
                        """) # ON CONFLICT é uma segurança extra, mas o DELETE anterior já limpa.
                        for codigo_produto in lista_codigos_produtos:
                            cur.execute(query_insert_produto, (cliente_id_db, codigo_produto))

                conn.commit() # Efetiva as alterações para ESTE cliente
                clientes_processados += 1
                # print(f"Cliente {cliente_data.get('codigo_cliente')} salvo/atualizado com sucesso.")

        except psycopg2.Error as e:
            if conn:
                conn.rollback() # Desfaz alterações para ESTE cliente em caso de erro
            print(f"Erro de banco de dados ao processar cliente {cliente_data.get('codigo_cliente')}: {e}")
            clientes_com_erro.append(cliente_data.get('codigo_cliente'))
            sucesso_geral = False
        except Exception as e: # Captura outros erros (ex: KeyError, JSONDecodeError se não tratado antes)
            if conn:
                conn.rollback()
            print(f"Erro inesperado ao processar cliente {cliente_data.get('codigo_cliente')}: {e}")
            clientes_com_erro.append(cliente_data.get('codigo_cliente'))
            sucesso_geral = False
    
    if conn:
        conn.close()

    print(f"\n--- Resumo do Processamento ---")
    print(f"Total de clientes na entrada: {len(lista_de_clientes_dict)}")
    print(f"Clientes processados com sucesso: {clientes_processados}")
    if clientes_com_erro:
        print(f"Clientes com erro ({len(clientes_com_erro)}): {', '.join(filter(None, clientes_com_erro))}")
    
    return sucesso_geral


def consultar_cliente_por_codigo(codigo_cliente_original):
    """Consulta um cliente específico pelo seu código original e seus produtos."""
    conn = get_db_connection()
    if not conn:
        return None

    cliente_info = None
    try:
        # Usar DictCursor para facilitar o acesso aos campos pelo nome
        with conn.cursor(cursor_factory=DictCursor) as cur:
            # 1. Buscar dados do cliente
            cur.execute("SELECT * FROM Clientes WHERE codigo_cliente_original = %s;", (codigo_cliente_original,))
            cliente_db = cur.fetchone()

            if cliente_db:
                cliente_info = dict(cliente_db) # Converte o resultado do DictCursor para um dicionário Python
                
                # 2. Buscar produtos do cliente
                cur.execute("SELECT codigo_produto_adquirido FROM Clientes_Produtos WHERE cliente_id = %s;", (cliente_info['id'],))
                produtos_db = cur.fetchall()
                cliente_info['produtos'] = [row['codigo_produto_adquirido'] for row in produtos_db]
            else:
                print(f"Cliente com código {codigo_cliente_original} não encontrado.")

    except psycopg2.Error as e:
        print(f"Erro de banco de dados ao consultar cliente {codigo_cliente_original}: {e}")
    finally:
        if conn:
            conn.close()
    return cliente_info


def listar_clientes(limite=100, offset=0):
    """Lista clientes com paginação."""
    conn = get_db_connection()
    if not conn:
        return []
    
    clientes = []
    try:
        with conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute("SELECT id, codigo_cliente_original, nome, email, cidade, estado FROM Clientes ORDER BY nome LIMIT %s OFFSET %s;", (limite, offset))
            for row in cur.fetchall():
                clientes.append(dict(row))
    except psycopg2.Error as e:
        print(f"Erro de banco de dados ao listar clientes: {e}")
    finally:
        if conn:
            conn.close()
    return clientes


def consultar_clientes_por_prefixo_produto(prefixo_produto, limite=100, offset=0):
    """Busca clientes que possuem produtos começando com o prefixo dado, com paginação."""
    conn = get_db_connection()
    if not conn:
        return []

    clientes_encontrados = []
    try:
        with conn.cursor(cursor_factory=DictCursor) as cur:
            query = sql.SQL("""
                SELECT DISTINCT c.id, c.codigo_cliente_original, c.nome, c.email, c.cidade, c.estado
                FROM Clientes c
                JOIN Clientes_Produtos cp ON c.id = cp.cliente_id
                WHERE cp.codigo_produto_adquirido LIKE %s
                ORDER BY c.nome
                LIMIT %s OFFSET %s;
            """)
            cur.execute(query, (prefixo_produto + '%', limite, offset))
            for row in cur.fetchall():
                clientes_encontrados.append(dict(row))
    except psycopg2.Error as e:
        print(f"Erro ao buscar clientes por prefixo de produto: {e}")
    finally:
        if conn:
            conn.close()
    return clientes_encontrados


def deletar_cliente_por_codigo(codigo_cliente_original):
    """Deleta um cliente pelo seu código original. A deleção cascata removerá as entradas em Clientes_Produtos."""
    conn = get_db_connection()
    if not conn:
        return False, 0

    linhas_afetadas = 0
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM Clientes WHERE codigo_cliente_original = %s;", (codigo_cliente_original,))
            linhas_afetadas = cur.rowcount # Número de linhas deletadas na tabela Clientes
            conn.commit()
            if linhas_afetadas > 0:
                print(f"Cliente com código {codigo_cliente_original} deletado com sucesso.")
                return True, linhas_afetadas
            else:
                print(f"Nenhum cliente encontrado com o código {codigo_cliente_original} para deletar.")
                return False, 0
    except psycopg2.Error as e:
        if conn:
            conn.rollback()
        print(f"Erro de banco de dados ao deletar cliente {codigo_cliente_original}: {e}")
        return False, 0
    finally:
        if conn:
            conn.close()

# --- Exemplo de Uso ---
if __name__ == "__main__":
    # Seus dados de exemplo (uma lista contendo um dicionário)
    dados_para_salvar = [
        {
            "codigo_cliente": "6022147136",
            "nome": "LUCIANO ROSA DE OLIVEIRA",
            "telefone1": "62994065932",
            "telefone2": "62994065932",
            "telefone3": "62994065932",
            "email": "luciano2212@hotmail.com",
            "cidade": "GOIÂNIA",
            "estado": "Goiás",
            # Note que 'produtos' é uma STRING que representa um JSON array
            "produtos": "[\"AR12TVHZDWKNAZ\", \"SM-S908EZKSZTO\", \"AR12TVHZDWKYAZ\", \"UN55MU6100GXZD\"]"
        },
        {
            "codigo_cliente": "7033158247",
            "nome": "MARIA APARECIDA SILVA",
            "telefone1": "62987654321",
            "telefone2": None, # Exemplo de campo opcional não preenchido
            "telefone3": None,
            "email": "maria.silva@example.com",
            "cidade": "APARECIDA DE GOIÂNIA",
            "estado": "Goiás",
            "produtos": "[\"SM-S908EZKSZTO\", \"SM-G781BZBJZTO\"]"
        },
        {
            "codigo_cliente": "8044169358",
            "nome": "PEDRO ALVES COSTA",
            "telefone1": "62912345678",
            "telefone2": None,
            "telefone3": None,
            "email": "pedro.costa@example.com",
            "cidade": "GOIÂNIA",
            "estado": "Goiás",
            "produtos": "[]" # Cliente sem produtos ou lista vazia
        }
    ]

    print("--- Testando salvar_dados_clientes ---")
    salvar_dados_clientes(dados_para_salvar)
    print("\n")

    print("--- Testando consultar_cliente_por_codigo (LUCIANO) ---")
    cliente_luciano = consultar_cliente_por_codigo("6022147136")
    if cliente_luciano:
        print(f"Detalhes de LUCIANO: {json.dumps(cliente_luciano, indent=4, ensure_ascii=False)}")
    print("\n")

    print("--- Testando listar_clientes (primeiros 2) ---")
    primeiros_clientes = listar_clientes(limite=2)
    if primeiros_clientes:
        for cliente in primeiros_clientes:
            print(json.dumps(cliente, indent=2, ensure_ascii=False))
    print("\n")

    print("--- Testando consultar_clientes_por_prefixo_produto ('SM-S908') ---")
    clientes_com_sms908 = consultar_clientes_por_prefixo_produto("SM-S908")
    if clientes_com_sms908:
        print(f"Clientes com produtos SM-S908*: ({len(clientes_com_sms908)})")
        for cliente in clientes_com_sms908:
            print(f"  {cliente['nome']} ({cliente['codigo_cliente_original']})")
    else:
        print("Nenhum cliente encontrado com produtos começando com 'SM-S908'.")
    print("\n")

    # Atualizando um cliente existente e mudando seus produtos
    dados_luciano_att = [{
            "codigo_cliente": "6022147136",
            "nome": "LUCIANO R. DE OLIVEIRA (ATT)", # Nome atualizado
            "telefone1": "62999998888", # Telefone atualizado
            "telefone2": None,
            "telefone3": None,
            "email": "luciano_att@hotmail.com", # Email atualizado
            "cidade": "GOIÂNIA",
            "estado": "GO", # Estado atualizado
            "produtos": "[\"NOVO_PRODUTO_1\", \"NOVO_PRODUTO_2\"]" # Lista de produtos totalmente nova
        }]
    print("--- Testando ATUALIZAR dados_clientes (LUCIANO) ---")
    salvar_dados_clientes(dados_luciano_att)
    cliente_luciano_apos_att = consultar_cliente_por_codigo("6022147136")
    if cliente_luciano_apos_att:
        print(f"Detalhes de LUCIANO (APÓS ATT): {json.dumps(cliente_luciano_apos_att, indent=4, ensure_ascii=False)}")
    print("\n")

    print("--- Testando deletar_cliente_por_codigo (PEDRO) ---")
    sucesso_delete, num_deletado = deletar_cliente_por_codigo("8044169358")
    print(f"Sucesso ao deletar Pedro: {sucesso_delete}, Número de registros principais deletados: {num_deletado}")
    
    cliente_pedro_apos_delete = consultar_cliente_por_codigo("8044169358") # Deve retornar None
    if not cliente_pedro_apos_delete:
        print("Cliente Pedro não encontrado após deleção, como esperado.")
    print("\n")

    print("--- Testando cliente inexistente ---")
    cliente_inexistente = consultar_cliente_por_codigo("0000000000") # Deve retornar None
    print("\n")

    print("--- Testando salvar cliente sem produtos ---")
    cliente_sem_produtos = [{
            "codigo_cliente": "9999999999",
            "nome": "CLIENTE SEM PRODUTOS",
            "telefone1": "111111111",
            "email": "semprod@example.com",
            "cidade": "SÃO PAULO",
            "estado": "SP",
            "produtos": "[]" # Lista de produtos vazia
    }]
    salvar_dados_clientes(cliente_sem_produtos)
    consulta_sem_produtos = consultar_cliente_por_codigo("9999999999")
    if consulta_sem_produtos:
         print(f"Detalhes CLIENTE SEM PRODUTOS: {json.dumps(consulta_sem_produtos, indent=4, ensure_ascii=False)}")