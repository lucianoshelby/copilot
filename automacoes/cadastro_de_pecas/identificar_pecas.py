import requests
import json
import time
import sys
sys.path.insert(0, 'C:\\Users\\Gestão MX\\Documents\\Copilot')
from login_gspn.cookies_manager import obter_cookies_validos_recentes


def baixar_lista_pecas_mx(modelo, cookies):
    """
    Realiza uma requisição POST para o portal da Samsung para obter a lista de peças
    de um modelo específico, filtra os resultados e retorna os códigos de peça relevantes.

    Args:
        modelo (str): O modelo do produto a ser pesquisado (ex: "SM-S918BLGSZTO").
        cookies (str): A string de cookies necessária para a autenticação da requisição.

    Returns:
        list: Uma lista de strings contendo os códigos de peça (matnr) que começam
              com "GH" e possuem um valor no campo "salpr". Retorna uma lista vazia
              se a requisição falhar ou nenhum item corresponder aos critérios.
    """
    # [cite_start]URL do endpoint para a requisição POST [cite: 12]
    url = "https://biz6.samsungcsportal.com/gspn/operate.do"

    # [cite_start]Headers da requisição, replicados do arquivo de exemplo [cite: 12, 13]
    # O cookie é inserido dinamicamente a partir do argumento da função
    headers = {
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Accept": "text/javascript, text/html, application/xml, text/xml, */*",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": "https://biz6.samsungcsportal.com/master/part/PartListByModelVersion.jsp",
        "Origin": "https://biz6.samsungcsportal.com",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0",
        
    }

    # [cite_start]Payload (corpo) da requisição, com o modelo sendo um campo dinâmico [cite: 13]
    payload = {
        "cmd": "PartListByModelVersionCmd",
        "numPerPage": "5000", # Valor alto para garantir que todas as peças sejam retornadas
        "currPage": "0",
        "CicCorpCode": "C820",
        "Version": "0001",
        "serialNumber": "",
        "piExtFlag": "X",
        "marketingName": "",
        "Model": modelo,
        "serialHA": "",
        "partNo": "",
        "partDesc": "",
        "partLoc": ""
    }

    codigos_filtrados = []

    try:
        response = requests.post(url, headers=headers, data=payload, cookies=cookies, verify=False)
        response.raise_for_status()

        # --- SEÇÃO CORRIGIDA ---
        # A resposta pode conter caracteres inválidos ou chunk-data antes do JSON.
        # A abordagem robusta é encontrar o início do objeto JSON, que é o caractere '{'.
        raw_text = response.text
        start_index = raw_text.find('{')

        if start_index != -1:
            # Cortamos a string a partir do início do JSON para garantir a limpeza
            json_string = raw_text[start_index:]
            data = json.loads(json_string)
            
            # [cite_start]Processa a lista de peças se a chave 'dataLists' existir [cite: 4]
            if 'dataLists' in data and isinstance(data['dataLists'], list):
                for item in data['dataLists']:
                    # [cite_start]Coleta o preço (salpr) e o código da peça (matnr) [cite: 4]
                    preco = item.get("salpr", "")
                    codigo_peca = item.get("matnr", "")

                    # Verifica as condições: preço existe e código começa com "GH"
                    if preco and codigo_peca.startswith("GH"):
                        codigos_filtrados.append(codigo_peca)
        else:
            print("Erro: JSON não encontrado na resposta do servidor.")
            # print("Resposta recebida:", raw_text) # Descomente para depuração

    except requests.exceptions.RequestException as e:
        print(f"Ocorreu um erro na requisição: {e}")
    except json.JSONDecodeError as e:
        print(f"Ocorreu um erro ao processar a resposta JSON: {e}")
        # print("String que falhou no parse:", json_string) # Descomente para depuração

    return codigos_filtrados


def identificar_pecas(lista_pecas_brutas):
    """
    Adiciona o nome em português baseado em regras de identificação do nome em inglês.

    Args:
        lista_pecas (list): Lista de dicionários contendo pelo menos as chaves 'codigo' e 'nome'.

    Returns:
        list: A mesma lista de dicionários com a chave adicional 'nome_portugues'.
    """
    #pecas_identificadas = []
    
    # Mapeamento de nomes para categorias para facilitar a atribuição


    for peca in lista_pecas_brutas:
        codigo = peca.get('codigo').upper()
        nome_ingles = peca.get('nome').upper()
        
        nome_portugues = "Nome desconhecido"
        

        # A ordem das verificações é importante, das mais específicas para as mais genéricas.
        
        if "PBA" in nome_ingles and "MAIN" in nome_ingles:
            nome_portugues = "PLACA PRINCIPAL"
        if "SCREEN" in nome_ingles and "OLED" in nome_ingles:
            nome_portugues = "DISPLAY"
        if "CON TO CON" in nome_ingles or "CTC" in nome_ingles:
            nome_portugues = "FLAT"
        if "SMT" in nome_ingles and "OCTA" in nome_ingles:
            nome_portugues = "DISPLAY COMPLETO"
        if "ASSY CAMERA" in nome_ingles:
            nome_portugues = "CAMERA"
        if "OLED" in nome_ingles and ("WQHD" in nome_ingles or "UB" in nome_ingles) and "SMT" not in nome_ingles:
            nome_portugues = "DISPLAY SOMENTE OCTA"
        if (codigo.startswith("GH96") or codigo.startswith("GH81")) and ("CAMERA" in nome_ingles and "WIDE" in nome_ingles and "ULTRA" not in nome_ingles) or ("CAMERA" in nome_ingles and "1/1" in nome_ingles and "VT" not in nome_ingles):
            nome_portugues = "CAMERA PRINCIPAL"
        if (codigo.startswith("GH96") or codigo.startswith("GH81")) and "CAMERA" in nome_ingles and "VT" in nome_ingles:
            nome_portugues = "CAMERA FRONTAL"
        if (codigo.startswith("GH96") or codigo.startswith("GH81")) and ("CAMERA" in nome_ingles and ("UW" in nome_ingles or "ULTRA" in nome_ingles)):
            nome_portugues = "CAMERA ULTRA WIDE"
        if (codigo.startswith("GH96") or codigo.startswith("GH81")) and ("CAMERA" in nome_ingles and ("TELE 10X" in nome_ingles or "10X" in nome_ingles)):
            nome_portugues = "CAMERA 10X"
        if (codigo.startswith("GH96") or codigo.startswith("GH81")) and "CAMERA" in nome_ingles and "3x" in nome_ingles:
            nome_portugues = "CAMERA 3X"
        if ("KIT" in nome_ingles and "OLED" in nome_ingles) or ("REPAIR KIT-SCREEN" in nome_ingles) or ("KIT" in nome_ingles and "DECO" in nome_ingles):
            nome_portugues = "KIT DE REPARO UB"
        if "KIT" in nome_ingles and "B/C" in nome_ingles:
            nome_portugues = "KIT REPARO TAMPA"
        if "CAMERA" in nome_ingles and "MACRO" in nome_ingles:
            nome_portugues = "CAMERA MACRO"
        if "DATA LINK CABLE" in nome_ingles:
            nome_portugues = "CABO USB"
        if "ANT COIL-NFC" in nome_ingles:
            nome_portugues = "ANTENA NFC"
        if "ANTENNA" in nome_ingles and "UWB" in nome_ingles:
            nome_portugues = "ANTENA UWB"
        if "ANTENNA" in nome_ingles and "NFC" in nome_ingles:
            nome_portugues = "MANTA NFC"
        if codigo.startswith("GH44"):
            nome_portugues = "CARREGADOR"
        if "CON TO CON FPCB-FRC" in nome_ingles:
            nome_portugues = "FLAT DE REDE"
        if ("SIDE" in nome_ingles and "KEY" in nome_ingles) and "BRACKET" not in nome_ingles:
            nome_portugues = "CIRCUITO DE TECLAS"
        if "SPEN DET" in nome_ingles:
            nome_portugues = "SENSOR DA S-PEN"
        if "COVER-SPEN" in nome_ingles:
            nome_portugues = "COBERTURA DA S-PEN"
        if "DECORATION-EJECTOR" in nome_ingles:
            nome_portugues = "CHAVE EJETORA DE CHIP"
        if "WINDOW" in nome_ingles and "UW" in nome_ingles and "TAPE" not in nome_ingles:
            nome_portugues = "LENTE CAMERA ULTRA-WIDE (SEM COLA)"
        if "WINDOW" in nome_ingles and "WIDE" in nome_ingles and "TAPE" not in nome_ingles:
            nome_portugues = "LENTE CAMERA PRINCIPAL (SEM COLA)"
        if "WINDOW" in nome_ingles and "TELE 10X" in nome_ingles and "TAPE" not in nome_ingles:
            nome_portugues = "LENTE CAMERA 10X (SEM COLA)"
        if "WINDOW" in nome_ingles and "TELE 3X" in nome_ingles and "TAPE" not in nome_ingles:
            nome_portugues = "LENTE CAMERA 3X (SEM COLA)"
        if "O-RING" in nome_ingles:
            nome_portugues = "ANEL DE VEDAÇÃO PCI-SUB"
        if ("MOTOR" in nome_ingles or "VIBRATOR" in nome_ingles) and "TAPE" not in nome_ingles:
            nome_portugues = "VIBRACALL"
        if "SPONGE VT" in nome_ingles:
            nome_portugues = "ESPUMA CAMERA FRONTAL"
        if ("TAPE BACK COVER" in nome_ingles) or ("TAPE" in nome_ingles and "BG" in nome_ingles):
            nome_portugues = "COLA TAMPA AVULSA"
        if "TAPE UB WP" in nome_ingles or "DOUBLE FACE-WINDOW" in nome_ingles:
            nome_portugues = "COLA UB AVULSA"
        if "TAPE MAIN WINDOW" in nome_ingles:
            nome_portugues = "COLA DISPLAY"
        if "TAPE UB BONDING WP" in nome_ingles:
            nome_portugues = "COLA FINA UB AVULSA"
        if "BATT ASSY" in nome_ingles or "BATTERY" in nome_ingles and "TAPE" not in nome_ingles:
            nome_portugues = "BATERIA"
        if "PBA-UB" in nome_ingles and "CTC" in nome_ingles:
            nome_portugues = "FLAT UB"
        if "PBA-IF" in nome_ingles and "CTC" in nome_ingles:
            nome_portugues = "FLAT PCI-SUB"
        if ("DECO" in nome_ingles and "CAM" in nome_ingles and "TAPE" not in nome_ingles) or ("METAL UNIT-CAMERA" in nome_ingles and "TAPE" not in nome_ingles):
            nome_portugues = "ESTRUTURA DE LENTES DAS CAMERAS"
        if "SUB PBA" in nome_ingles and "ANT" not in nome_ingles:
            nome_portugues = "PLACA SUB"
        if "STYLUS PEN" in nome_ingles:
            nome_portugues = "CANETA S-PEN"
        if ("SPEAKER" in nome_ingles or "SPK" in nome_ingles) and "RUBBER" not in nome_ingles and "UPPER" not in nome_ingles and "BRACKET" not in nome_ingles and "MESH" not in nome_ingles and "REWORK" not in nome_ingles and "CON TO CON" not in nome_ingles:
            nome_portugues = "SPEAKER"
        if ("METAL FRONT" in nome_ingles  or "FRONT MODULE" in nome_ingles or "CASE" in nome_ingles) and "BRACKET" not in nome_ingles:
            nome_portugues = "ARO"
        if "REPAIR KIT" in nome_ingles and "SUB UB" in nome_ingles:
            nome_portugues = "KIT DE REPARO SUB UB"
        if "MEA ANTENNA-MID" in nome_ingles:
            nome_portugues = "MANTA NFC COMPLETA COM ANTENA"
        if "RUBBER-MIC BTM" in nome_ingles or "SPONGE MIC BTM" in nome_ingles:
            nome_portugues = "VEDAÇÃO MIC INFERIOR"
        if "SIM TRAY" in nome_ingles:
            nome_portugues = "GAVETA DE CHIP"
        if "RUBBER-SPK BTM" in nome_ingles or "SPK MESH" in nome_ingles:
            nome_portugues = "TELINHA DO SPEAKER"
        if "COAXIAL CABLE" in nome_ingles and "BLUE" in nome_ingles:
            nome_portugues = "CABO COAXIAL AZUL"
        if "COAXIAL CABLE" in nome_ingles and "RED" in nome_ingles:
            nome_portugues = "CABO COAXIAL VERMELHO"
        if "COAXIAL CABLE" in nome_ingles and "BLACK" in nome_ingles:
            nome_portugues = "CABO COAXIAL PRETO"
        if "COAXIAL CABLE" in nome_ingles and "WHITE" in nome_ingles:
            nome_portugues = "CABO COAXIAL BRANCO"
        if "COAXIAL CABLE" in nome_ingles and "GREEN" in nome_ingles:
            nome_portugues = "CABO COAXIAL VERDE"
        if "COAXIAL CABLE" in nome_ingles and "YELLOW" in nome_ingles:
            nome_portugues = "CABO COAXIAL AMARELO"
        if "COAXIAL CABLE" in nome_ingles and "GRAY" in nome_ingles:
            nome_portugues = "CABO COAXIAL CINZA"
        if "US FP" in nome_ingles:
            nome_portugues = "SENSOR BIOMETRICO"
        if ("COVER" in nome_ingles and "REAR" in nome_ingles) or ("COVER" in nome_ingles and "B/G" in nome_ingles) or ("COVER" in nome_ingles and "B/C" in nome_ingles) or ("COVER" in nome_ingles and "BACK" in nome_ingles) or ("COVER" in nome_ingles and "BG" in nome_ingles):
            nome_portugues = "TAMPA TRASEIRA"
        if "MIC" in nome_ingles and "FPCB" in nome_ingles:
            nome_portugues = "MICROFONE"
        if "STAND COVER" in nome_ingles:
            nome_portugues = "CAPA SEM TECLADO"
        if "KEYBOARD COVER" in nome_ingles and "STAND" not in nome_ingles:
            nome_portugues = "TECLADO"
        if "MEA BRACKET-FRONT" in nome_ingles:
            nome_portugues = "BRACKET FRONTAL"
        if "SUB UB" in nome_ingles and "BRACKET" not in nome_ingles and "CAP" not in nome_ingles and "TAPE" not in nome_ingles and "REPAIR" not in nome_ingles:
            nome_portugues = "DISPLAY SUB UB"
        if "IF PBA-CTC FPCB" in nome_ingles:
            nome_portugues = "FLAT PCI-SUB E UB"
        if ("OLED" in nome_ingles and "FHD" in nome_ingles) or "MAIN UB" in nome_ingles and "FILM" not in nome_ingles and "TAPE" not in nome_ingles:
            nome_portugues = "DISPLAY SOMENTE OCTA"
        if "PROTECTOR FILM" in nome_ingles and "MAIN" in nome_ingles:
            nome_portugues = "PELICULA"
        if "SPEAKER" in nome_ingles and "UPPER" in nome_ingles:
            nome_portugues = "RECEIVER"
        if "CH SET" in nome_ingles and "RIGHT" in nome_ingles:
            nome_portugues = "FONE R"
        if "CH SET" in nome_ingles and "LEFT" in nome_ingles:
            nome_portugues = "FONE L"
        if "CRADLE" in nome_ingles and "UPPER" not in nome_ingles and "LOWER" not in nome_ingles:
            nome_portugues = "CASE FONES"
        peca["nome_portugues"] = nome_portugues

    return lista_pecas_brutas

"""def obter_nome_ingles(codigos, cookies, codigos_ja_pesquisados=[]):
    ""
    Clona uma requisição para obter o nome de peças da Samsung em inglês.

    Args:
        codigos: Uma lista de códigos de peças da Samsung.
        cookies: Um dicionário de cookies para a sessão de requisição.

    Returns:
        Uma lista de dicionários, cada um contendo o 'código' e o 'nome' em inglês da peça.
    ""
    resultados = []
    url = "https://biz6.samsungcsportal.com/gspn/operate.do"

    headers = {
        "X-Prototype-Version": "1.7.2",
        "sec-ch-ua-platform": '"Windows"',
        "sec-ch-ua": '"Not)A;Brand";v="8", "Chromium";v="138", "Microsoft Edge";v="138"',
        "sec-ch-ua-mobile": "?0",
        "X-Requested-With": "XMLHttpRequest",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0",
        "Accept": "text/javascript, text/html, application/xml, text/xml, */*",
        "Content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Origin": "https://biz6.samsungcsportal.com",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "Referer": "https://biz6.samsungcsportal.com/master/part/GeneralPartInfo.jsp?search_status=&searchContent=&menuBlock=&menuUrl=&naviDirValue=",
    }

    for codigo in codigos:
        # Altera o 'Referer' com o código da peça atual
        #headers["Referer"] = f"https://biz6.samsungcsportal.com/master/part/GeneralPartInfo.jsp?dataMode=D&partNo={codigo}"
        if modelos_ja_pesquisados and codigo in modelos_ja_pesquisados:
            continue
        if codigo.startswith(("GH96", "GH82", "GH59", "GH81", "GH98", "GH97")):
            # Altera o payload com o código da peça atual
            payload = {
                "cmd": "GeneralPartDetailCmd",
                "numPerPage": "100",
                "currPage": "0",
                "material": codigo,
                "fileType": "B",
                "popupYn": "Y",
                "CorpCode": "C820",
                "partNo": codigo,
                "partDesc": "",
                "location": ""
            }

            try:
                # [cite_start]A resposta da requisição original indica o Content-Type como text/json [cite: 1][cite_start], porém o conteúdo real é um payload de formulário[cite: 3, 4].
                # A biblioteca requests lida com a codificação de dados para application/x-www-form-urlencoded quando o argumento `data` é usado.
                response = requests.post(url, headers=headers, cookies=cookies, data=payload, verify=False)
                response.raise_for_status()  # Lança um erro para respostas com códigos de status ruins (4xx ou 5xx)

                # [cite_start]A resposta esperada é um JSON [cite: 1, 2]
                dados_resposta = response.json()

                if dados_resposta.get("success") and dados_resposta.get("peData"):
                    # [cite_start]O nome em inglês está no campo "materialDescEn" [cite: 2]
                    nome_em_ingles = dados_resposta["peData"].get("materialDescEn")
                    resultados.append({"codigo": codigo, "nome": nome_em_ingles})
                else:
                    resultados.append({"codigo": codigo, "nome": "Não encontrado"})
                time.sleep(1)  # Adiciona um atraso entre as requisições
                codigos_ja_pesquisados.append(codigo)
            except requests.exceptions.RequestException as e:
                print(f"Ocorreu um erro na requisição para o código {codigo}: {e}")
                resultados.append({"codigo": codigo, "nome": "Erro na requisição"})
            except json.JSONDecodeError:
                print(f"Não foi possível decodificar a resposta JSON para o código {codigo}.")
                resultados.append({"codigo": codigo, "nome": "Erro de decodificação JSON"})


    return resultados"""


def obter_dados_pecas(codigos, cookies, detalhado=False):
    url = "https://biz6.samsungcsportal.com/gspn/operate.do"

    headers = {
        "X-Prototype-Version": "1.7.2",
        "X-Requested-With": "XMLHttpRequest",
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
        "Content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Referer": "https://biz6.samsungcsportal.com/master/part/GeneralPartInfo.jsp?search_status=&searchContent=&menuBlock=&menuUrl=&naviDirValue="
    }

    resultados = []
    codigos_ja_pesquisados = set()
    codigos_alternativos = set()
    fila_codigos = list(codigos)

    while fila_codigos:
        codigo = fila_codigos.pop(0)

        if codigo in codigos_ja_pesquisados:
            continue

        if not codigo.startswith(("GH96", "GH82", "GH59", "GH81", "GH98", "GH97", "GH44")) and detalhado == False:
            continue

        payload = {
            "cmd": "GeneralPartDetailCmd",
            "numPerPage": "100",
            "currPage": "0",
            "material": codigo,
            "fileType": "B",
            "popupYn": "Y",
            "CorpCode": "C820",
            "partNo": codigo,
            "partDesc": "",
            "location": ""
        }

        try:
            response = requests.post(url, headers=headers, cookies=cookies, data=payload, verify=False)
            response.raise_for_status()
            dados = response.json()
            codigos_ja_pesquisados.add(codigo)

            if dados.get("success") and dados.get("peData"):
                peData = dados["peData"]
                resultado = {
                    "codigo": codigo,
                    "nome": peData.get("materialDescEn", "Desconhecido"),
                    "disponivel": peData.get("stockAvailDesc", "").strip().upper() == "YES",
                    "dna": peData.get("salesStatus", "").strip().upper() == "DNA STOCK = 0",
                    "alternativo": codigo in codigos_alternativos
                }
                resultados.append(resultado)

                # Verifica e coleta códigos alternativos
                alternativos = dados.get("ptAltmList", [])
                for alt in alternativos:
                    alt_codigo = alt.get("material")
                    if alt_codigo and alt_codigo not in codigos_ja_pesquisados and alt_codigo not in codigos_alternativos:
                        codigos_alternativos.add(alt_codigo)
                        fila_codigos.append(alt_codigo)

            else:
                resultados.append({
                    "codigo": codigo,
                    "nome": "Não encontrado",
                    "disponivel": False,
                    "dna": False,
                    "alternativo": codigo in codigos_alternativos
                })

        except Exception as e:
            print(f"Erro ao consultar o código {codigo}: {e}")
            resultados.append({
                "codigo": codigo,
                "nome": "Erro",
                "disponivel": False,
                "dna": False,
                "alternativo": codigo in codigos_alternativos
            })

        time.sleep(1)

    return resultados

def categorizar_pecas(lista_pecas):
    """
    Categoriza as peças com base em critérios específicos.

    Args:
        lista_pecas (list): Lista de dicionários com informações das peças.

    Returns:
        list: Lista de dicionários com a chave 'categoria' adicionada.
    """
    for peca in lista_pecas:
        codigo = peca.get('codigo', '').upper()
        nome = peca.get("nome", "").upper()
        nome_pt = peca.get("nome_portugues", "").upper()

        if "NOME DESCONHECIDO" in nome:
            peca["categoria"] = "Não encontrado"
        elif nome_pt == "PLACA PRINCIPAL":
            peca["categoria"] = "Placa Principal"
        elif nome_pt == "DISPLAY" or nome_pt == "DISPLAY SOMENTE OCTA":
            peca["categoria"] = "Display"
        elif nome_pt == "SUB DISPLAY":
            peca["categoria"] = "Sub Display"
        elif codigo.startswith("GH98"):
            peca["categoria"] = "Peça cosmética"
        elif nome_pt == "TAMPA TRASEIRA":
            peca["categoria"] = "Peça cosmética"
        elif "CAMERA" in nome_pt and "ESPUMA" not in nome_pt and "LENTE" not in nome_pt:
            peca["categoria"] = "Camera"
        elif nome_pt == "ARO":
            peca["categoria"] = "ARO"
        elif "FONE L" in nome_pt:
            peca["categoria"] = "Fone L"
        elif "FONE R" in nome_pt:
            peca["categoria"] = "Fone R"
        elif "CASE FONES" in nome_pt:
            peca["categoria"] = "Case Fones"
        else:
            peca["categoria"] = "Peça comum"

    return lista_pecas






# --- Exemplo de Uso ---
if __name__ == "__main__":
    # Modelo e cookies extraídos dos arquivos de exemplo
    modelo_exemplo = "SM-X110NZAAMEA"  # 
    cookies_exemplo = obter_cookies_validos_recentes()
    # Chama a função com os dados de exemplo
    lista_de_pecas = baixar_lista_pecas_mx(modelo_exemplo, cookies_exemplo)
    lista = obter_dados_pecas(lista_de_pecas, cookies_exemplo)

    lista_identificada = identificar_pecas(lista)
    lista_categorizada = categorizar_pecas(lista_identificada)
    # Imprime o resultado
    if lista_categorizada:
        for peca in lista_categorizada:
            print("=" * 40)
            print(f"Código..........: {peca.get('codigo')}")
            print(f"Nome (inglês)...: {peca.get('nome')}")
            print(f"Nome (português): {peca.get('nome_portugues')}")
            print(f"Disponível......: {'Sim' if peca.get('disponivel') else 'Não'}")
            print(f"DNA.............: {'Sim' if peca.get('dna') else 'Não'}")
            print(f"Alternativo.....: {'Sim' if peca.get('alternativo') else 'Não'}")
            print(f"Categoria.......: {peca.get('categoria')}")
        print("=" * 40)