
import sys
sys.path.insert(0, 'C:\\Users\\Gestão MX\\Documents\\Copilot')
from automacoes.cos.coletar_dados_cos import coletar_dados_os
from smart_buffer.extrair_os_planilha import coletar_ordens_filtradas
# --- IMPORTAÇÕES (VOCÊ IRÁ ADICIONAR) ---
# Adicione aqui os imports dos seus outros módulos
# Exemplo:
# from processador_os import coletar_ordens_filtradas
# from seu_modulo_de_coleta import coletar_dados_os
# -----------------------------------------------


def _processar_lista_de_pecas(lista_pecas_bruta: list) -> dict:
    """
    Função auxiliar para contar e agrupar peças de uma lista bruta.
    
    Argumentos:
        lista_pecas_bruta (list): A lista do dicionário "pecas_usadas".

    Retorna:
        dict: Um dicionário processado onde a chave é o 'codigo' da peça.
              Ex: {'GH82-35145A': {'descricao': 'KIT UB COMPLETO', 'quantidade': 2}}
    """
    pecas_contadas = {}
    
    # Verifica se a lista não é None ou vazia
    if not lista_pecas_bruta:
        return pecas_contadas

    for peca in lista_pecas_bruta:
        # Usamos .get() para evitar erros caso a chave 'codigo' não exista
        codigo = peca.get('codigo')
        
        # Ignora entradas sem código
        if not codigo:
            continue
        
        # Se o código já foi contado, apenas incrementa a quantidade
        if codigo in pecas_contadas:
            pecas_contadas[codigo]['quantidade'] += 1
        
        # Se for a primeira vez que vemos este código
        else:
            # Pegamos a descrição (com um valor padrão caso não exista)
            descricao = peca.get('descricao', 'Descrição não encontrada')
            pecas_contadas[codigo] = {
                'descricao': descricao,
                'quantidade': 1
            }
            
    return pecas_contadas


def enriquecer_dados_das_os(nome_arquivo_excel: str) -> dict:
    """
    Orquestra a coleta de dados, combinando dados da planilha
    com dados de peças de outra fonte (via 'coletar_dados_os').
    
    Remove OSs que não tiveram peças utilizadas.

    Argumentos:
        nome_arquivo_excel (str): O nome do arquivo Excel para processar.

    Retorna:
        dict: O dicionário completo com os dados da planilha
              enriquecidos com os dados das peças processadas.
    """
    
    # ETAPA 1: Coletar os dados base da planilha
    print("ETAPA 1: Coletando dados base da planilha Excel...")
    try:
        # Esta função é do seu outro módulo ('processador_os.py')
        dados_base = coletar_ordens_filtradas(nome_arquivo_excel)
    except NameError:
        print("\n*** ERRO DE IMPORTAÇÃO ***")
        print("A função 'coletar_ordens_filtradas' não foi importada.")
        print("Verifique se você importou 'processador_os.py' neste script.")
        return {}
    except Exception as e:
        print(f"Falha ao ler o Excel. Erro: {e}")
        return {}
        
    if not dados_base:
        print("Nenhuma OS encontrada na planilha. Encerrando.")
        return {}

    print(f"Encontradas {len(dados_base)} OSs. Partindo para a ETAPA 2 (enriquecimento)...")

    # --- NOVO ---
    # Lista para guardar as chaves das OSs que devem ser removidas
    os_para_remover = [] 
    # --- FIM NOVO ---

    # ETAPA 2: Iterar sobre cada OS e buscar os dados das peças
    total_os = len(dados_base)
    for i, (os_numero, os_info) in enumerate(dados_base.items()):
        
        # O 'os_info' é o dicionário que já contém {'Pronto': ..., 'Linha': ...}
        # Convertemos para string para o print e para a função
        os_str = str(os_numero) 
        print(f"  Processando OS: {os_str} ({i+1}/{total_os})...", end="")
        
        try:
            # Esta é a sua função que já existe (passando como string)
            dados_completos_os = coletar_dados_os(os_str)
            
            # Extrai a lista de peças
            lista_pecas_bruta = dados_completos_os.get("pecas_usadas")
            
            # --- LÓGICA DE REMOÇÃO (MODIFICADA) ---
            # 'not lista_pecas_bruta' checa se é None OU uma lista vazia []
            if not lista_pecas_bruta:
                print(" -> Nenhuma peça usada. Marcando para remoção.")
                os_para_remover.append(os_numero) # Adiciona a chave original
                continue # Pula para a próxima OS
            # --- FIM DA LÓGICA DE REMOÇÃO ---

            # Processa e conta as peças (só executa se a lista não for vazia)
            pecas_processadas = _processar_lista_de_pecas(lista_pecas_bruta)
            
            # Adiciona o dicionário de peças processadas à OS
            os_info['pecas_processadas'] = pecas_processadas
            print(" -> Sucesso.")

        except NameError:
            print("\n*** ERRO DE IMPORTAÇÃO ***")
            print("A função 'coletar_dados_os' não foi importada.")
            print("Verifique se você importou seu módulo de coleta neste script.")
            return {} # Interrompe o processo
        
        except Exception as e:
            # Se a coleta de UMA OS falhar, registra o erro e continua
            print(f" -> FALHA. Erro: {e}")
            os_info['pecas_processadas'] = {"erro": f"Falha ao coletar peças: {e}"}

    # --- ETAPA 3: REMOÇÃO (NOVA) ---
    if os_para_remover:
        print(f"\nETAPA 3: Removendo {len(os_para_remover)} OSs sem utilização de peças...")
        for os_numero in os_para_remover:
            # Remove a OS do dicionário principal
            del dados_base[os_numero]
        print("Remoção concluída.")
    # --- FIM ETAPA 3 ---

    print("\nEnriquecimento de dados finalizado.")
    return dados_base

# --- EXEMPLO DE USO ---
if __name__ == "__main__":
    
    # Este bloco só roda se você executar este arquivo diretamente
    # (ex: python enriquecedor_os.py)
    
    print("Iniciando processo de enriquecimento...")
    
    NOME_DO_ARQUIVO = "teste1.xls" # O mesmo nome de arquivo do exemplo anterior
    
    # Chama a função principal deste módulo
    dados_finais = enriquecer_dados_das_os(NOME_DO_ARQUIVO)
    
    if dados_finais:
        print(f"\n--- SUCESSO GERAL ---")
        for chave, valor in dados_finais.items():
            print(f'{chave}: {valor}')
        
    else:
        print("\n--- PROCESSO FINALIZADO SEM DADOS ---")