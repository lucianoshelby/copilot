import pandas as pd
import sys

# --- CONFIGURAÇÃO ---
# ATENÇÃO: Altere os nomes das variáveis abaixo para que correspondam
# EXATAMENTE aos nomes dos cabeçalhos na sua planilha Excel.
CAMINHO_PANILHAS = "C:/Users/Gestão MX/Documents/Copilot/smart_buffer/planilhas/"

# --- Nomes das Colunas ---
COLUNA_OS = "OS Interna"           # Coluna A (Chave do Dicionário)
COLUNA_CATEGORIA = "Linha"         # Coluna H (Coletar)
COLUNA_TIPO_SERVICO = "Tipo Serviço" # Coluna I (Coletar)
COLUNA_STATUS = "Motivo"           # Coluna K (Filtrar)
COLUNA_DATA = "Pronto"             # Coluna X (Coletar)


# --- DEFINIÇÃO DOS FILTROS ---

# Lista de status de reparo desejados (Filtro da Coluna K)
# Este é o ÚNICO filtro que será aplicado.
STATUS_VALIDOS = [
    "Entregue para Cliente",
    "Reparado",
    "Reparado - Cliente Informado",
    "Reparado - Contato Sem Sucesso"
]


def coletar_ordens_filtradas(nome_arquivo: str) -> dict:
    """
    Lê uma planilha Excel, aplica um filtro de status e retorna um
    dicionário com dados abrangentes de cada OS.

    Argumentos:
        nome_arquivo (str): O nome do arquivo (ex: "planilha.xls").

    Retorna:
        dict: Um dicionário onde as chaves são as OS e os valores são
              dicionários contendo os dados coletados (Data, Linha, Tipo Serviço).
              Ex: {12345: {'Pronto': '10/11/2025', 'Linha': 'Celular', 'Tipo Serviço': 'Garantia'}}
    """
    
    caminho_arquivo = CAMINHO_PANILHAS + nome_arquivo.split("/")[-1]
    print(f"Iniciando processamento do arquivo: {caminho_arquivo}")
    try:
        # 1. Ler a planilha (usando o motor 'xlrd' para arquivos .xls)
        df = pd.read_excel(caminho_arquivo, engine='xlrd')

        # 2. LIMPEZA AUTOMÁTICA DOS CABEÇALHOS
        df.columns = df.columns.str.strip()

        # 3. Garantir que as colunas de dados e filtro sejam texto E LIMPAR
        df[COLUNA_STATUS] = df[COLUNA_STATUS].astype(str).str.strip()
        df[COLUNA_CATEGORIA] = df[COLUNA_CATEGORIA].astype(str).str.strip()
        df[COLUNA_TIPO_SERVICO] = df[COLUNA_TIPO_SERVICO].astype(str).str.strip()

        # 4. Aplicar o FILTRO ÚNICO (Coluna K - Status)
        print("Aplicando filtro de Status ('Motivo')...")
        filtro_status = df[COLUNA_STATUS].isin(STATUS_VALIDOS)

        # 5. Aplicar filtro e criar uma cópia para evitar avisos
        # Usamos .copy() para garantir que não estamos modificando uma 'fatia' do dataframe
        df_filtrado = df[filtro_status].copy()

        if df_filtrado.empty:
            print("Nenhum dado encontrado após aplicar os filtros.")
            return {}

        print(f"Encontradas {len(df_filtrado)} ordens de serviço correspondentes.")

        # --- ETAPA 6: FORMATAR A DATA ---
        
        # 6.1. Converter a coluna de data para o formato datetime
        datas_dt = pd.to_datetime(df_filtrado[COLUNA_DATA], errors='coerce')

        # 6.2. Formatar as datas para o padrão "DD/MM/AAAA"
        datas_formatadas = datas_dt.dt.strftime('%d/%m/%Y').fillna('')
        
        # 6.3. Atualizar a coluna de data no dataframe filtrado com os valores formatados
        df_filtrado[COLUNA_DATA] = datas_formatadas

        # --- ETAPA 7: CRIAR O DICIONÁRIO ABRANGENTE ---
        
        # 7.1. Definir a 'OS Interna' (COLUNA_OS) como o índice (a chave do dicionário)
        df_final = df_filtrado.set_index(COLUNA_OS)
        
        # 7.2. Selecionar apenas as colunas que queremos no resultado final
        colunas_para_coletar = [
            COLUNA_DATA,
            COLUNA_CATEGORIA,
            COLUNA_TIPO_SERVICO
        ]
        
        # 7.3. Converter o dataframe para um dicionário
        # 'index' -> orienta o pandas para criar um dicionário onde
        # a chave é o índice (OS) e o valor é outro dicionário
        # contendo {nome_da_coluna: valor}
        resultado_dict = df_final[colunas_para_coletar].to_dict('index')

        return resultado_dict

    except FileNotFoundError:
        print(f"Erro Crítico: Arquivo não encontrado no caminho '{caminho_arquivo}'")
        return {}
    except KeyError as e:
        print(f"Erro Crítico: Coluna não encontrada: {e}.")
        print("Isso geralmente acontece por dois motivos:")
        print(" 1. O nome da coluna na seção 'CONFIGURAÇÃO' do script está diferente do nome (limpo) na planilha.")
        print(" 2. A planilha não contém essa coluna.")
        return {}
    except Exception as e:
        print(f"Ocorreu um erro inesperado durante o processamento: {e}")
        return {}

# --- EXEMPLO DE USO ---
# (O código abaixo permanece o mesmo e funcionará com o novo formato)
if __name__ == "__main__":
    
    # --------------------------------------------------------------------
    # >> COLOQUE O NOME DO SEU ARQUIVO AQUI <<
    # O caminho base já está em CAMINHO_PANILHAS
    # --------------------------------------------------------------------
    
    NOME_DO_ARQUIVO = "teste1.xls"

    # --------------------------------------------------------------------

    print(f"Iniciando coleta de ordens de serviço...\n")
    
    ordens_coletadas = coletar_ordens_filtradas(NOME_DO_ARQUIVO)

    if ordens_coletadas:
        print(f"\n--- SUCESSO ---")
        print(f"Total de {len(ordens_coletadas)} ordens de serviço coletadas.")
        
        # O print(ordens_coletadas) agora mostrará o dicionário aninhado
        print("\nAmostra dos dados (pode ser grande):")
        print(ordens_coletadas)
        
        # Exemplo de como acessar um item (se você souber uma OS)
        # os_exemplo = 12345 # Troque pelo número de uma OS real
        # if os_exemplo in ordens_coletadas:
        #     print(f"\nExemplo de acesso à OS {os_exemplo}:")
        #     print(ordens_coletadas[os_exemplo])
        #     print(f"Linha do produto: {ordens_coletadas[os_exemplo]['Linha']}")

    else:
        print("\n--- FINALIZADO ---")
        print("Nenhuma ordem de serviço foi encontrada com os critérios definidos.")