import os
import re
import pandas as pd

def compilar_resultados(pasta_resultados):
    """
    Lê todos os arquivos *_resumo.txt na pasta especificada e compila as métricas principais
    (status, objetivo, volume, número de caixas, gap, tempo e nós explorados)
    em um único DataFrame salvo como CSV.
    """

    resultados = []

    for arquivo in os.listdir(pasta_resultados):
        if arquivo.endswith("_resumo.txt"):
            caminho = os.path.join(pasta_resultados, arquivo)
            with open(caminho, "r", encoding="latin-1") as f:
                content = f.read()

            # Expressões regulares mais flexíveis
            status_match = re.search(r"Status da solução:\s*(\d+)", content)
            objetivo_match = re.search(r"Objetivo final.*:\s*([\d\.]+)", content)
            volume_match = re.search(r"Volume total carregado:\s*([\d\.]+)", content)
            caixas_match = re.search(r"Número total de caixas carregadas:\s*(\d+)", content)
            gap_match = re.search(r"Gap de otimalidade:\s*([\d\.]+)%", content)
            tempo_match = re.search(r"Tempo de execução:\s*([\d\.]+)", content)
            nos_match = re.search(r"Número de nós explorados:\s*([\d\.]+)", content)

            # Extrair valores ou definir como None se não encontrado
            status = int(status_match.group(1)) if status_match else None
            objetivo = float(objetivo_match.group(1)) if objetivo_match else None
            volume = float(volume_match.group(1)) if volume_match else None
            caixas = int(caixas_match.group(1)) if caixas_match else None
            gap = float(gap_match.group(1)) if gap_match else None
            tempo = float(tempo_match.group(1)) if tempo_match else None
            nos = float(nos_match.group(1)) if nos_match else None

            nome_instancia = arquivo.replace("_resumo.txt", "")

            resultados.append({
                "Instância": nome_instancia,
                "Status": status,
                "Objetivo": objetivo,
                "Volume": volume,
                "Nº Caixas": caixas,
                "Gap (%)": gap,
                "Tempo (s)": tempo,
                "Nós Explorados": nos
            })

    # Converter em DataFrame
    df = pd.DataFrame(resultados)

    # Ordenar pelo nome da instância (opcional)
    df.sort_values(by="Instância", inplace=True)

    # Salvar CSV
    caminho_saida = os.path.join(pasta_resultados, "resultados_compilados.csv")
    df.to_csv(caminho_saida, index=False, sep=";", decimal=",")
    
    print(f"Resultados compilados salvos em: {caminho_saida}")
    print(df)

    return df
