import os
import re
import pandas as pd

def compilar_resultados(pasta_resultados):
    """
    Lê todos os arquivos *_resumo.txt na pasta especificada e compila as métricas 
    em um CSV formatado para Excel (Ponto e vírgula e vírgula decimal).
    """

    resultados = []

    # Verifica se a pasta existe
    if not os.path.exists(pasta_resultados):
        print(f"Erro: A pasta '{pasta_resultados}' não existe.")
        return pd.DataFrame()

    print(f"Buscando resumos em: {pasta_resultados}...")

    for arquivo in os.listdir(pasta_resultados):
        # Filtra apenas os arquivos de resumo gerados pelo solver
        if arquivo.endswith("_resumo.txt"):
            caminho = os.path.join(pasta_resultados, arquivo)
            
            try:
                with open(caminho, "r", encoding="utf-8") as f:
                    content = f.read()

                # Regex para capturar os dados (mais seguro contra espaços extras)
                status_match = re.search(r"Status da solução:\s*(\d+)", content)
                objetivo_match = re.search(r"Objetivo final\s*:\s*([\d\.]+)", content)
                volume_match = re.search(r"Volume total carregado:\s*([\d\.]+)", content)
                caixas_match = re.search(r"Número total de caixas carregadas:\s*(\d+)", content)
                gap_match = re.search(r"Gap de otimalidade:\s*([\d\.]+)%?", content)
                tempo_match = re.search(r"Tempo de execução:\s*([\d\.]+)", content)
                nos_match = re.search(r"Número de nós explorados:\s*([\d\.]+)", content)

                # Extração com fallback para valores padrão caso não encontre algo
                resultados.append({
                    "Instância": arquivo.replace("_resumo.txt", ""),
                    "Status": int(status_match.group(1)) if status_match else "N/A",
                    "Objetivo (Ocupação)": float(objetivo_match.group(1)) if objetivo_match else 0.0,
                    "Volume Total": float(volume_match.group(1)) if volume_match else 0.0,
                    "Nº Caixas": int(caixas_match.group(1)) if caixas_match else 0,
                    "Gap (%)": float(gap_match.group(1)) if gap_match else 0.0,
                    "Tempo (s)": float(tempo_match.group(1)) if tempo_match else 0.0,
                    "Nós Explorados": float(nos_match.group(1)) if nos_match else 0
                })
            except Exception as e:
                print(f"Aviso: Erro ao processar o arquivo {arquivo}: {e}")

    if not resultados:
        print("\n[AVISO] Nenhum arquivo '_resumo.txt' encontrado para compilar.")
        return pd.DataFrame()

    # Criar DataFrame
    df = pd.DataFrame(resultados)

    # Ordenação Natural (Ex: instancia_2 vem antes de instancia_10)
    if "Instância" in df.columns:
        # Extrai o número do nome do arquivo para ordenar numericamente
        df['num_sort'] = df['Instância'].str.extract('(\d+)').astype(float)
        df = df.sort_values(by="num_sort").drop(columns=['num_sort'])

    # Salvar CSV (Formato Excel PT-BR)
    caminho_csv = os.path.join(pasta_resultados, "resultados_compilados.csv")
    df.to_csv(caminho_csv, index=False, sep=";", decimal=",")
    
    print("\n" + "="*50)
    print(f" COMPILAÇÃO CONCLUÍDA: {len(df)} instâncias")
    print(f" Arquivo salvo em: {caminho_csv}")
    print("="*50)
    
    # Exibe a tabela no terminal de forma organizada
    print(df.to_string(index=False))

    return df