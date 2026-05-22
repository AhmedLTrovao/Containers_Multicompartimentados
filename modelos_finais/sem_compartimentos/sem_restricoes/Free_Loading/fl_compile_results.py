import os
import re
import pandas as pd

def fl_compile_results(pasta_resultados):

    resultados = []

    for arquivo in os.listdir(pasta_resultados):
        if arquivo.endswith("_resumo.txt"):
            caminho = os.path.join(pasta_resultados, arquivo)
            with open(caminho, "r", encoding="latin-1") as f:
                content = f.read()

            status = re.search(r"Status.*:\s*(\d+)", content)
            objetivo = re.search(r"Objetivo final.*:\s*([\d\.]+)", content)
            gap = re.search(r"Gap.*:\s*([\d\.]+)", content)
            tempo = re.search(r"Tempo de execução:\s*([\d\.]+)", content)
            nos = re.search(r"Número de nós explorados:\s*([\d\.]+)", content)

            resultados.append({
                "Instância": arquivo.replace("_resumo.txt", ""),
                "Status": int(status.group(1)) if status else None,
                "Objetivo": float(objetivo.group(1)) if objetivo else None,
                "Gap (%)": float(gap.group(1)) if gap else None,
                "Tempo (s)": float(tempo.group(1)) if tempo else None,
                "Nós": float(nos.group(1)) if nos else None
            })

    df = pd.DataFrame(resultados)
    df.sort_values(by="Instância", inplace=True)

    caminho_saida = os.path.join(pasta_resultados, "resultados_compilados_free_loading.csv")
    df.to_csv(caminho_saida, index=False, sep=";", decimal=",")

    print("Resultados compilados salvos em:", caminho_saida)
    print(df)

    return df
