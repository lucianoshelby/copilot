from automacoes.cos.coletar_dados_cos import obter_os_correspondentes, coletar_dados_os
import requests

def filtrar_os_validas():
    resultado = []

    #try:
        #with open("OS.txt", "r", encoding="utf-8") as arquivo:
            #linhas = arquivo.readlines()
            #ordens = [linha.strip() for linha in linhas if linha.strip()]
    #except FileNotFoundError:
        ##return resultado
    ordens = buscar_os_designadas()
    for numero_os in ordens:
        dados = coletar_dados_os(numero_os)

        linha_produto = dados.get("LinhaProduto", "")
        #descricao_seguro = dados.get("descricaoSeguro", "")"""
        atendente = dados.get("atendente", "")

        if atendente == "CAIOFELIPE" and linha_produto == "HTV":
            resultado.append({'numero_da_os': numero_os, 'atendente': atendente})
            

    return resultado



import requests
import json

def buscar_os_designadas():
    url = "http://192.168.25.131:8080/COS_CSO/ControleOrdemServico"

    params = {
        "Acao": "BuscarOSDesignada",
        "CodigoTecnico": "Todos",
        "SelectTipoDeAtendimento": "Todos",
        "TipoDeServico": "'BAL','COR','RDE'",
        "Motivo": "'M10','M11','M13','M14','M15','M16','M17'",
        "SelectLinhaProduto": "Todos"
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept": "*/*",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": "http://192.168.25.131:8080/COS_CSO/OrdemServicoDesignada.jsp",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "pt-BR,pt;q=0.9",
        "Connection": "keep-alive",
        "Cookie": "JSESSIONID=14C2466B9D02736BF04E715D02345232"
    }

    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()

        # Remove espaços e quebras de linha do início da resposta
        texto_limpo = response.text.lstrip()
        dados = json.loads(texto_limpo)

        lista_os = [item["NumeroOS"] for item in dados.get("OSDesignada", []) if "NumeroOS" in item]
        return lista_os

    except Exception as e:
        print("Erro ao buscar OS:", e)
        return []

def obter_codigo_seguro(nome):
    mapa = {
        'Assurant': 'ASS',
        'Cardif': 'CAR',
        'Contigo': 'CTG',
        'Luizaseg': 'LUI',
        'Care +': 'SCA',
        'SIS': 'SIS',
        'Zurich': 'ZUR'
    }
    return mapa.get(nome, '')

def enviar_requisicoes():
    url_base = "http://192.168.25.131:8080/COS_CSO/ControleOrdemServico"
    params_base = {
        "Acao": "AlteracaoEspecialAtendimento",
        "IP": "192.168.24.97",
        "IDUsuario": "1417",
        "TipoDeAtendimento": "",
        "SelectTipoDeServico": "INH"
    }

    headers_base = {
        "Host": "192.168.25.131:8080",
        "Connection": "keep-alive",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36 Edg/135.0.0.0",
        "Accept": "*/*",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": "http://192.168.25.131:8080/COS_CSO/AdministrarOS.jsp",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "Cookie": "JSESSIONID=14C2466B9D02736BF04E715D02345232"
    }

    for os_info in filtrar_os_validas():
        numero_os = os_info['numero_da_os']
        #nome_seguradora = os_info['nome_da_seguradora']
        #tipo_seguro = obter_codigo_seguro(nome_seguradora)

        params = params_base.copy()
        params['NumeroOS'] = numero_os
        params['SelectTipoSeguro'] = ''

        response = requests.get(url_base, params=params, headers=headers_base)

        try:
            json_resp = response.json()
            if json_resp.get("Sucesso") == True:
                print(f"OS {numero_os} atualizada com sucesso.")
            else:
                print(f"OS {numero_os} falhou: {json_resp.get('Mensagem')}")
        except ValueError:
            print(f"OS {numero_os} retornou resposta inválida.")


if __name__ == "__main__":
    # Exemplo de uso
    services = enviar_requisicoes()
    print("OS Designadas:", services)