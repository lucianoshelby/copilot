from finalizar_sem_reparo import aplicar_produto_entregue, aplicar_reparo_completo_remontagem, mudar_pra_ow, muda_tecnico_gspn, aplica_ag_custo_gspn
from automacoes.cos.auto_cos import deletar_cos
from automacoes.cos.coletar_dados_cos import obter_os_correspondentes
from automacoes.coletar_dados import fetch_os_data
from coletar_os_da_base.coletar_informações_os import coletar_informacoes_os
import time
from login_gspn.cookies_manager import obter_cookies_validos_recentes
CAMINHO_ARQUIVO = r"C:\\Users\\Gestão MX\\Documents\\Copilot\\OS_ag_custo.txt"



def fechar_lista_de_os(cookies=None):

    print("Iniciando mudança pra AG CUSTO de lista de OS...")
    fallhas = []
    with open(CAMINHO_ARQUIVO, "r", encoding="utf-8") as file:
        os_list = [line.strip() for line in file.readlines() if line.strip()]
    total=[]
    for os in os_list:
        #deletar = deletar_cos(os)
        #os = obter_os_correspondentes(os)
        #dados= fetch_os_data(os)
        #fechamento = mudar_pra_ow(dados)
        #fechamento = aplica_ag_custo_gspn(os)
        #fechamento = muda_tecnico_gspn(os)
        #fechamento = coletar_informacoes_os(os, cookies)
        
        fechamento = aplica_ag_custo_gspn(os)
        if fechamento:
            print(f"Mudança pra AG CUSTO da OS {os} realizado com sucesso.")
            #total.append(fechamento)
            #time.sleep(2)
        else:
            print(f"Erro ao fechar a OS {os}.")
            fallhas.append(os)
            continue
        """print('Aplicando o produto entregue...')
        produto_entregue = aplicar_produto_entregue(os)
        if produto_entregue:
            print(f"Produto entregue aplicado na OS {os} com sucesso.")
            print("Deletando OS COS...")
            deletar = deletar_cos(os)
            if deletar:
                print(f"OS COS {os} deletada com sucesso.")
            else:
                print(f"Erro ao deletar a OS COS {os}.")
        else:
            print(f"Erro ao aplicar o produto entregue na OS {os}.")
            fallhas.append(os)"""
    if fallhas:
        print("As seguintes OSs falharam no fechamento:")
        for os in fallhas:
            print(os)
    """for fechamento in total:
        print('------Dados da OS-------')
        for chave, valor in fechamento.items():
            print(f'{chave}: {valor}')"""

if __name__ == "__main__":
    #cookies = obter_cookies_validos_recentes()
    fechar_lista_de_os()
    #aplicar_reparo_completo_remontagem("4172771585")
    print("Mudança pra AG CUSTO da lista de OS concluído.")