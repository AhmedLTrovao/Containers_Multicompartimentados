import os
import pandas as pd
import re

def compilar_resultados(pasta_saida):
    """
    Lê todos os arquivos *_resumo.txt e cria um Excel consolidado com:
    Instância | Gap (%) | Tempo (s) | Nº Caixas | Volume (%)
    """
    resultados = []

    for arquivo in os.listdir(pasta_saida):  # percorre todos os arquivos da pasta
        if arquivo.endswith("_resumo.txt"):  # só pega os *_resumo.txt
            caminho = os.path.join(pasta_saida, arquivo)
            nome_instancia = arquivo.replace("_resumo.txt", "")

            with open(caminho, "r", encoding="utf-8") as f:
                conteudo = f.read()

            # pega os números dentro do arquivo usando expressões regulares
            gap_match = re.search(r"Gap de otimalidade:\s*([\d.,]+)%", conteudo)
            tempo_match = re.search(r"Tempo de execução:\s*([\d.,]+)", conteudo)
            vol_match = re.search(r"Objetivo final:\s*([\d.,]+)", conteudo)

            # converte os valores para número
            gap = float(gap_match.group(1).replace(",", ".")) if gap_match else None
            tempo = float(tempo_match.group(1).replace(",", ".")) if tempo_match else None
            vol = float(vol_match.group(1).replace(",", ".")) if vol_match else None

            # adiciona o resultado à lista
            resultados.append({
                "Instância": nome_instancia,
                "Gap (%)": gap,
                "Tempo (s)": tempo,
                "Volume (%)": vol
            })

    # transforma tudo em uma planilha Excel
    df = pd.DataFrame(resultados)
    excel_saida = os.path.join(pasta_saida, "Resumo_geral.csv")
    df.to_csv(excel_saida, index=False)
    print(f"\n Resultados consolidados em: {excel_saida}")
    
if __name__ == '__main__':
    compilar_resultados('DATA_1_n30m05b2d1')
