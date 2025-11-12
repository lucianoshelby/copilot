import requests
import json
import sys
from identificar_pecas import baixar_lista_pecas_mx, obter_dados_pecas
sys.path.insert(0, 'C:\\Users\\Gestão MX\\Documents\\Copilot')
from login_gspn.cookies_manager import obter_cookies_validos_recentes

def consulta_compatibilidade_por_codigo(lista_codigos, modelo, cookies):
    """
    Verifica a compatibilidade de códigos de peças com um modelo.
    Usa verificação direta e, se necessário, verificação detalhada baseada em códigos alternativos.

    Args:
        lista_codigos (list[str]): Lista de códigos a verificar.
        modelo (str): Código do modelo a ser consultado.
        cookies (dict): Cookies de autenticação.

    Returns:
        list[dict]: Lista com {"codigo": ..., "compativel": True/False}
    """

    # Etapa 1: Obter lista de códigos diretamente compatíveis com o modelo
    codigos_modelo = set(baixar_lista_pecas_mx(modelo, cookies))

    resultado_temp = {}  # Dict para montar o resultado final: {codigo: True/False}
    codigos_pendentes_detalhe = []

    # Etapa 2: Verificação direta
    for codigo in lista_codigos:
        if codigo in codigos_modelo:
            resultado_temp[codigo] = True
        else:
            codigos_pendentes_detalhe.append(codigo)

    # Etapa 3: Verificação detalhada individual para os códigos pendentes
    codigos_alternativos_por_codigo = {}  # {codigo_original: [alternativos...]}

    for codigo in codigos_pendentes_detalhe:
        detalhes = obter_dados_pecas([codigo], cookies, detalhado=True)

        if not detalhes:
            resultado_temp[codigo] = False  # Nenhuma informação → incompatível
            continue

        codigos_retornados = [p.get("codigo") for p in detalhes if "codigo" in p]

        if len(codigos_retornados) == 1 and codigos_retornados[0] == codigo:
            # Só ele mesmo → incompatível
            resultado_temp[codigo] = False
        else:
            # Há códigos alternativos
            codigos_alternativos_por_codigo[codigo] = codigos_retornados

    # Etapa 4: Verifica se algum alternativo é compatível
    for codigo_original, codigos_alternativos in codigos_alternativos_por_codigo.items():
        for cod_alt in codigos_alternativos:
            if cod_alt in codigos_modelo:
                resultado_temp[codigo_original] = True
                break
        else:
            # Nenhum alternativo compatível
            resultado_temp[codigo_original] = False

    # Etapa 5: Montar resultado final com a mesma ordem da lista original
    resultado_final = [{"codigo": codigo, "compativel": resultado_temp.get(codigo, False)} for codigo in lista_codigos]

    return resultado_final

    

if __name__ == "__main__":
    # Exemplo de uso
    lista_codigos = ["GH96-16601A", "GH82-36827A"]
    modelo = "SM-A566EZKTLEB"
    cookies = obter_cookies_validos_recentes()
    resultado = consulta_compatibilidade_por_codigo(lista_codigos, modelo, cookies)
    print(json.dumps(resultado, indent=4))  # Imprime o resultado formatado em JSON