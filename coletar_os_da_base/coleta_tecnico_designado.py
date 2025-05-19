import sys
sys.path.insert(0, 'C:\\Users\\Gestão MX\\Documents\\Copilot\\')
from login_gspn.cookies_manager import obter_cookies_validos_recentes
import requests
import json
from datetime import datetime


def coletar_os_tecnico_designado(year):
    """
    Coleta a lista de números de Ordens de Serviço (OS) com status
    'Técnico Designado' (ST025) para um ano específico no portal GSPN.

    Args:
        year (int or str): O ano para o qual a consulta deve ser feita.

    Returns:
        list: Uma lista de strings contendo os números das Ordens de Serviço
              encontradas. Retorna uma lista vazia em caso de erro ou se
              nenhuma OS for encontrada.
    """
    print(f"\n=== Coletando OS em 'Técnico Designado' para o ano: {year} ===")

    # 1. Obter Cookies
    cookies = obter_cookies_validos_recentes()
    if not cookies:
        print("Falha: Não foi possível obter cookies.")
        return [] # Retorna lista vazia em caso de erro

    # 2. Definir URL e Headers
    target_url = "https://biz6.samsungcsportal.com/gspn/operate.do"
    # Headers baseados no arquivo 'baixar services em tecnico designado.txt'
    headers = {
        'Content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'X-Requested-With': 'XMLHttpRequest',
        'X-Prototype-Version': '1.7.2',
        'Origin': 'https://biz6.samsungcsportal.com',
        'Referer': 'https://biz6.samsungcsportal.com/svctracking/monitor/SVCJobSummarybyStatus.jsp?search_status=&searchContent=&menuBlock=&menuUrl=&naviDirValue=', # Referer estático para esta consulta
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36',
        'Accept': 'text/javascript, text/html, application/xml, text/xml, */*',
        'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
    }

    # 3. Definir Payload
    # Payload baseado no arquivo, com 'year' dinâmico
    payload_data = {
        'cmd': 'SVCPendingListCmd',
        'ascCode': '0002446971', # Este pode precisar ser dinâmico também? Usando o do exemplo.
        'STATUS': 'ST025', # Código para "Técnico Designado"
        'REASON': '',
        'STATUS_NAME': '',
        'REASON_NAME': '',
        'AGING_FROM': '0',
        'AGING_TO': '999999',
        'ACCOUNT': '0002446971', # Igual a ascCode no exemplo
        'SAP_LANG': 'P', # Linguagem Português
        'WTY_FLAG': '',
        'PAGE': 'SOMonitoringByStatus',
        'SubSvcType': '',
        'ASC_CODE': '0002446971', # Repetido no exemplo
        'SERVICE_TYPE': 'CI', # Tipo de Serviço (Counter In?)
        'cic_product': 'HHP', # Tipo de produto (Hand Held Phone?)
        'product': '',
        'year': str(year), # Campo dinâmico, convertido para string
        'wty_type': ''
    }
    print(f"Payload a ser enviado: {payload_data}")

    # 4. Enviar Requisição POST
    lista_os_encontradas = []
    try:
        print("\nEnviando requisição para coletar OS...")
        response = requests.post(
            target_url,
            headers=headers,
            cookies=cookies,
            data=payload_data,
            verify=False # requests codifica como x-www-form-urlencoded
        )
        print(f"Status Code Coleta OS: {response.status_code}")
        response.raise_for_status() # Verifica erro HTTP

        # 5. Processar Resposta JSON
        try:
            # Limpeza similar às funções anteriores pode ser necessária se houver lixo
            response_text_clean = response.text.strip()
            # Exemplo de limpeza (ajustar se necessário):
            if response_text_clean and response_text_clean[0] != '{':
                 json_start_index = response_text_clean.find('{')
                 if json_start_index != -1:
                      response_text_clean = response_text_clean[json_start_index:]
            if response_text_clean.endswith('\n0'): # Exemplo comum de finalizador
                 response_text_clean = response_text_clean[:-2].strip()

            data = json.loads(response_text_clean)
            # print(f"Resposta completa (JSON): {json.dumps(data, indent=2)}") # Descomente para depuração detalhada

            # Verifica se a resposta indica sucesso e contém a lista esperada
            if data.get("error") is False and "etSvcInfo" in data and isinstance(data["etSvcInfo"], list):
                lista_svc_info = data["etSvcInfo"]
                print(f"Encontrados {len(lista_svc_info)} registros na resposta.")

                # Extrai os números das OS
                for item in lista_svc_info:
                    if isinstance(item, dict):
                        numero_os = item.get("SERVICE_ORDER_NO")
                        if numero_os:
                            lista_os_encontradas.append(numero_os)
                        else:
                            print("Aviso: Item na lista 'etSvcInfo' não contém 'SERVICE_ORDER_NO'.")
                    else:
                        print("Aviso: Item na lista 'etSvcInfo' não é um dicionário.")

                print(f"Total de {len(lista_os_encontradas)} números de OS coletados.")

            elif data.get("error") is True:
                 print(f"Erro indicado na resposta JSON: {data}")
            else:
                 print("Erro: Resposta JSON não contém 'error: false' ou a lista 'etSvcInfo' esperada.")
                 print(f"Resposta recebida: {data}")


        except json.JSONDecodeError as json_err:
            print(f"Erro ao decodificar JSON da resposta: {json_err}")
            print(f"Texto da resposta recebida: {response.text}")
        except Exception as e:
             print(f"Erro inesperado ao processar a resposta: {e}")


    except requests.exceptions.RequestException as req_err:
        print(f"Erro na requisição: {req_err}")
        if hasattr(req_err, 'response') and req_err.response is not None:
                print(f"Response Status: {req_err.response.status_code}")
    except Exception as e:
        print(f"Um erro inesperado ocorreu: {e}")

    # 6. Retornar a lista de OS encontradas (pode estar vazia)
    return lista_os_encontradas

# --- Exemplo de Uso ---
if __name__ == "__main__":
    ano_atual = datetime.now().year
    # Você pode solicitar o ano ao usuário ou definir um valor fixo
    ano_consulta = 2025
    if not ano_consulta:
        ano_consulta = ano_atual
    else:
        try:
            ano_consulta = int(ano_consulta)
        except ValueError:
            print("Ano inválido, usando o ano atual.")
            ano_consulta = ano_atual

    # Chama a função para coletar as OSs
    lista_ordens_servico = coletar_os_tecnico_designado(ano_consulta)

    if lista_ordens_servico:
        print(f"\n--- Ordens de Serviço encontradas (Status ST025 - Técnico Designado) para {ano_consulta} ---")
        for os_num in lista_ordens_servico:
            print(os_num)
    else:
        print(f"\nNenhuma Ordem de Serviço encontrada para o status ST025 no ano {ano_consulta} ou ocorreu um erro.")
