import requests
import sys 
sys.path.insert(0, 'C:\\Users\\Gestão MX\\Documents\\Copilot\\automacoes')
import os
import uuid
from datetime import datetime, timedelta
from pprint import pprint # Usado para imprimir bonito no final
from coletar_pecas import enriquecer_dados_das_os
from automacoes.cos.login_cos import carregar_sessao
# --- IMPORTS DOS SEUS MÓDULOS ---
# (Descomente e ajuste os nomes dos arquivos conforme necessário)

# Módulo que lê a planilha e filtra
# (Importa a pasta base de planilhas)
# from processador_os import CAMINHO_PANILHAS

# Módulo que enriquece os dados (este já chama 'coletar_ordens_filtradas')
# from enriquecedor_os import enriquecer_dados_das_os

# Módulo que carrega sua sessão de cookies
# from seu_modulo_sessao import carregar_sessao

# -----------------------------------------------------------------
# --- SIMULAÇÃO (STUBS) ---
# (APENAS PARA TESTE. Remova/substitua pelas suas funções reais)
# -----------------------------------------------------------------
# Simula a pasta de planilhas do seu outro módulo
CAMINHO_PANILHAS = "C:/Users/Gestão MX/Documents/Copilot/smart_buffer/planilhas/"



# --- CONFIGURAÇÃO DO DOWNLOADER ---
BASE_URL = "http://192.168.25.131:8080/COS_CSO/ControleOrdemServicoGSPN"

# Cabeçalhos fixos (extraídos do seu .txt)
REQUEST_HEADERS = {
    "Host": "192.168.25.131:8080",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Referer": "http://192.168.25.131:8080/COS_CSO/BuscarDownloadOrdemServico.jsp",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8"
    # O Cookie é adicionado via session.cookies
}

# Parâmetros fixos (extraídos do seu .txt)
STATIC_PARAMS = {
    "Acao": "BuscarTodosDadosOS",
    "DataInicialEntrega": "",
    "DataFinalEntrega": "",
    "TipoData1": "DataPronto",
    "TipoData2": "DataEntrega"
    # DataInicial e DataFinal são adicionados dinamicamente
}

# Limite de dias por requisição
MAX_DIAS_POR_REQUISICAO = 30 # Usamos 30 para segurança (limite é 31)


def _dividir_intervalo_datas(data_inicio: datetime, data_fim: datetime) -> list:
    """
    Divide um intervalo de datas em pedaços de no máximo 'MAX_DIAS_POR_REQUISICAO' dias.
    """
    intervalos = []
    data_atual = data_inicio
    
    while data_atual <= data_fim:
        # Define o fim do pedaço atual
        data_fim_chunk = data_atual + timedelta(days=MAX_DIAS_POR_REQUISICAO)
        
        # Garante que o fim do pedaço não ultrapasse a data final solicitada
        if data_fim_chunk > data_fim:
            data_fim_chunk = data_fim
            
        intervalos.append((data_atual, data_fim_chunk))
        
        # Prepara o início do próximo pedaço
        data_atual = data_fim_chunk + timedelta(days=1)
        
    return intervalos

def _baixar_planilha(data_inicio_str: str, data_fim_str: str, session, consulta_id: str, chunk_num: int) -> str:
    """
    Baixa uma única planilha do sistema e a salva localmente.
    """
    print(f"  Baixando Chunk {chunk_num}: {data_inicio_str} a {data_fim_str}...")
    
    # 1. Prepara os parâmetros da requisição
    params_dinamicos = {
        **STATIC_PARAMS, # Copia os parâmetros estáticos
        "DataInicial": data_inicio_str,
        "DataFinal": data_fim_str
    }
    
    # 2. Gera um nome de arquivo único
    data_nome = data_inicio_str.replace('/', '-')
    nome_arquivo = f"consulta_{consulta_id}_chunk{chunk_num}_{data_nome}.xls"
    caminho_completo_arquivo = os.path.join(CAMINHO_PANILHAS, nome_arquivo)
    
    # Garante que o diretório de planilhas existe
    os.makedirs(CAMINHO_PANILHAS, exist_ok=True)
    
    try:
        # 3. Faz a requisição HTTP GET
        response = requests.get(
            BASE_URL,
            params=params_dinamicos,
            headers=REQUEST_HEADERS,
            cookies=session.cookies,
            timeout=120 # Timeout de 2 minutos
        )
        
        # Verifica se a requisição foi bem-sucedida
        response.raise_for_status() # Lança um erro se o status for 4xx ou 5xx
        
        # 4. Salva o conteúdo (os bytes) no arquivo
        with open(caminho_completo_arquivo, 'wb') as f:
            f.write(response.content)
            
        print(f"  -> Salvo como: {nome_arquivo}")
        
        # Retorna o NOME do arquivo, pois o 'enriquecedor_os' espera só o nome
        return nome_arquivo 
        
    except requests.exceptions.RequestException as e:
        print(f"  -> ERRO ao baixar o arquivo: {e}")
        return None

def _calcular_estatisticas(dados_os: dict) -> tuple:
    """Calcula estatísticas gerais da consulta."""
    total_os = len(dados_os)
    total_pecas_geral = 0
    
    for os_info in dados_os.values():
        pecas_processadas = os_info.get('pecas_processadas', {})
        if pecas_processadas:
            for peca_info in pecas_processadas.values():
                total_pecas_geral += peca_info.get('quantidade', 0)
                
    return total_os, total_pecas_geral

def executar_nova_consulta(data_inicio_str: str, data_fim_str: str, usuario= "Luciano Oliveira") -> dict:
    """
    Função principal que orquestra todo o processo de consulta.
    
    Argumentos:
        data_inicio_str (str): Data inicial no formato "DD/MM/AAAA".
        data_fim_str (str): Data final no formato "DD/MM/AAAA".
        usuario (str): Nome do usuário para carregar a sessão.

    Retorna:
        dict: Um dicionário estruturado com os dados da consulta.
    """
    
    # 1. Validação e preparação das datas
    try:
        data_inicio_dt = datetime.strptime(data_inicio_str, '%d/%m/%Y')
        data_fim_dt = datetime.strptime(data_fim_str, '%d/%m/%Y')
        if data_inicio_dt > data_fim_dt:
            print("Erro: A Data Inicial não pode ser maior que a Data Final.")
            return {}
    except ValueError:
        print("Erro: Formato de data inválido. Use 'DD/MM/AAAA'.")
        return {}
        
    # 2. Gera um ID único para esta consulta
    consulta_id = str(uuid.uuid4()).split('-')[0] # Pega só a primeira parte
    print(f"Iniciando nova consulta ID: {consulta_id} (de {data_inicio_str} a {data_fim_str})")
    
    # 3. Carrega a sessão (cookies)
    try:
        session = carregar_sessao(usuario)
    except Exception as e:
        print(f"Erro Crítico: Falha ao carregar a sessão para o usuário {usuario}. Erro: {e}")
        return {}

    # 4. Divide o intervalo de datas em pedaços
    intervalos = _dividir_intervalo_datas(data_inicio_dt, data_fim_dt)
    print(f"Intervalo de datas dividido em {len(intervalos)} chunk(s) de no máx. {MAX_DIAS_POR_REQUISICAO} dias.")
    
    dados_completos_da_consulta = {}
    
    # 5. Loop principal: Baixar e Processar cada pedaço
    for i, (inicio_chunk, fim_chunk) in enumerate(intervalos):
        chunk_num = i + 1
        data_inicio_chunk_str = inicio_chunk.strftime('%d/%m/%Y')
        data_fim_chunk_str = fim_chunk.strftime('%d/%m/%Y')
        
        print(f"\n--- Processando Chunk {chunk_num}/{len(intervalos)} ---")
        
        # 5.1. Baixar a planilha
        nome_arquivo_baixado = _baixar_planilha(
            data_inicio_chunk_str, 
            data_fim_chunk_str, 
            session, 
            consulta_id, 
            chunk_num
        )
        
        if not nome_arquivo_baixado:
            print(f"Falha ao baixar o Chunk {chunk_num}. Pulando para o próximo.")
            continue
            
        # 5.2. Processar a planilha (Extrair + Enriquecer)
        # (Esta função é do módulo 'enriquecedor_os.py')
        try:
            dados_do_chunk = enriquecer_dados_das_os(nome_arquivo_baixado)
            
            # 5.3. Unir os resultados
            # .update() adiciona/sobrescreve chaves. Se houver OS duplicada
            # entre chunks (improvável), a do último chunk prevalece.
            dados_completos_da_consulta.update(dados_do_chunk)
            print(f"Chunk {chunk_num} processado. {len(dados_do_chunk)} OSs adicionadas.")

            # 5.4. Opcional: Limpar a planilha baixada
            # try:
            #     os.remove(os.path.join(CAMINHO_PANILHAS, nome_arquivo_baixado))
            #     print(f"Arquivo temporário '{nome_arquivo_baixado}' removido.")
            # except OSError as e:
            #     print(f"Aviso: Não foi possível remover o arquivo temporário. Erro: {e}")

        except Exception as e:
            print(f"ERRO CRÍTICO ao processar o arquivo '{nome_arquivo_baixado}'. Erro: {e}")
            # Você pode decidir se quer parar tudo ou apenas pular este chunk
            continue # Aqui, estamos pulando

    # 6. Finalização: Calcular estatísticas e estruturar o resultado
    print("\n--- Consulta Concluída. Gerando relatório final... ---")
    
    total_os, total_pecas = _calcular_estatisticas(dados_completos_da_consulta)
    
    # Esta é a estrutura final que você salvará no banco de dados
    resultado_final_consulta = {
        "id_consulta": consulta_id,
        "data_execucao": datetime.now().isoformat(),
        "usuario_consulta": usuario,
        "data_inicio_filtro": data_inicio_str,
        "data_fim_filtro": data_fim_str,
        "estatisticas": {
            "total_os_coletadas": total_os,
            "total_pecas_geral": total_pecas
        },
        "dados_das_os": dados_completos_da_consulta
    }
    
    return resultado_final_consulta


# --- EXEMPLO DE USO ---
if __name__ == "__main__":
    
    USUARIO = "Luciano Oliveira"
    
    # Exemplo 1: Intervalo curto (1 chunk)
    # DATA_INICIAL = "01/10/2025"
    # DATA_FINAL = "30/10/2025"
    
    # Exemplo 2: Intervalo longo (requer 2 chunks)
    DATA_INICIAL = "01/11/2025"
    DATA_FINAL = "30/11/2025"

    resultado_da_consulta = executar_nova_consulta(DATA_INICIAL, DATA_FINAL, USUARIO)
    
    if resultado_da_consulta:
        print("\n\n--- RESULTADO FINAL DA CONSULTA ---")
        
        # Imprime as estatísticas
        print(f"ID da Consulta: {resultado_da_consulta['id_consulta']}")
        print(f"Período: {resultado_da_consulta['data_inicio_filtro']} a {resultado_da_consulta['data_fim_filtro']}")
        print(f"Total de OSs Coletadas: {resultado_da_consulta['estatisticas']['total_os_coletadas']}")
        print(f"Total de Peças Utilizadas: {resultado_da_consulta['estatisticas']['total_pecas_geral']}")
        
        print("\n--- DADOS DAS OS (amostra) ---")
        # Imprime os dados das OS de forma legível
        pprint(resultado_da_consulta['dados_das_os'])
    else:
        print("\n\n--- CONSULTA FINALIZADA SEM DADOS ---")