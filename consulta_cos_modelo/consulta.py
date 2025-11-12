import requests
import json
#from coletar_os_da_base.coletar_informações_os import coletar_informacoes_os
def buscar_e_extrair_dados():
    """
    Executa uma requisição HTTP para um servidor local, valida a resposta
    e extrai uma lista de 'OSFabricante' do JSON retornado.
    """
    # Detalhes da requisição, conforme fornecido nos arquivos
    url = "http://192.168.25.131:8080/COS_CSO/ControleOrdemServico"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0',
        'Accept': '*/*',
        'X-Requested-With': 'XMLHttpRequest',
        'Referer': 'http://192.168.25.131:8080/COS_CSO/BuscarOrdemServico.jsp',
        'Cookie': 'JSESSIONID=BEC68B22CB7AEA3504380273E554D23E',
        'Host': '192.168.25.131:8080'
    }

    params = {
        "Acao": "BuscarOSResumo",
        "IDUsuario": "1417",
        "IP": "192.168.24.97",
        "OSInterna": "",
        "OSFabricante": "",
        "IDunico": "",
        "Serial": "",
        "IMEI": "",
        "IDModeloProduto": "TB_Produto_IDProduto=2774",
        "TipoDeAtendimento": "",
        "Status": "",
        "DataInicial": "13/08/2024",
        "DataFinal": "13/08/2025",
        "OSManual": "",
        "SelectTipoDeServico": "",
        "TipoData1": "DataEntrada",
        "SelectTipoSeguro": ""
    }

    print(">>> Iniciando a requisição para o servidor em", url)
    
    try:
        # Executa a requisição HTTP GET real
        response = requests.get(url, headers=headers, params=params, timeout=20)
        
        # Verifica se a requisição retornou um código de erro (ex: 404, 500)
        response.raise_for_status()
        
        print(">>> Requisição bem-sucedida (Status:", response.status_code, ")")
        
        # Tenta decodificar a resposta como JSON
        dados_json = response.json()
        
        # Valida a estrutura do JSON e extrai os dados
        if 'ResumoOrdemServico' in dados_json and isinstance(dados_json['ResumoOrdemServico'], list):
            lista_os = [
                item['OSFabricante'] 
                for item in dados_json['ResumoOrdemServico'] 
                if 'OSFabricante' in item
            ]
            
            if not lista_os:
                print(">>> A chave 'ResumoOrdemServico' foi encontrada, mas está vazia ou os itens não possuem 'OSFabricante'.")
                return []

            return lista_os
        else:
            print("!!! Erro: A chave 'ResumoOrdemServico' não foi encontrada ou não é uma lista no JSON recebido.")
            return None

    # Tratamento de possíveis erros
    except requests.exceptions.Timeout:
        print("!!! Erro Crítico: A requisição demorou demais para responder (timeout).")
        print("    Verifique se o servidor está no ar e não está sobrecarregado.")
        return None
    except requests.exceptions.ConnectionError:
        print("!!! Erro Crítico: Falha na conexão.")
        print("    - Verifique se o endereço IP e a porta estão corretos.")
        print("    - Certifique-se de que este computador está na mesma rede que o servidor.")
        print("    - Verifique se há algum firewall bloqueando a conexão.")
        return None
    except requests.exceptions.RequestException as e:
        print("!!! Erro Crítico: Ocorreu um erro com a requisição HTTP:", e)
        return None
    except json.JSONDecodeError:
        print("!!! Erro Crítico: A resposta do servidor não é um JSON válido.")
        print("    Abaixo está o texto recebido do servidor:")
        print("--------------------------------------------------")
        print(response.text)
        print("--------------------------------------------------")
        return None

# --- Ponto de Entrada do Script ---
if __name__ == "__main__":
    lista_final = buscar_e_extrair_dados()
    
    if lista_final is not None:
        print("\n-------------------------------------------")
        print("--- LISTA DE OSFABRICANTE EXTRAÍDA ---")
        print("-------------------------------------------")
        # Imprime a lista de forma legível
        for os_id in lista_final:
            print(os_id)
        print("-------------------------------------------")
        print("Total de", len(lista_final), "itens encontrados.")
    else:
        print("\n>>> O script terminou com erros e não pôde extrair a lista.")