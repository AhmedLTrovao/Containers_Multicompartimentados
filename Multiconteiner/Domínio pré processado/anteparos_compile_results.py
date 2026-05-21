import os
import re
import pandas as pd

def compilar_resultados(pasta_resultados):
    """
    Lê os arquivos de resultados na pasta especificada e compila as métricas 
    em um CSV formatado para Excel (Ponto e vírgula e vírgula decimal).
    """

    resultados = []

    # Verifica se a pasta existe
    if not os.path.exists(pasta_resultados):
        print(f"Erro: A pasta '{pasta_resultados}' não existe.")
        return pd.DataFrame()

    print(f"Buscando arquivos de resultados em: {pasta_resultados}...")

    # Lista todos os arquivos na pasta
    arquivos = os.listdir(pasta_resultados)
    
    for arquivo in arquivos:
        # Filtra arquivos .txt que contenham 'instancia' no nome
        # Ignora o arquivo CSV de saída se ele já existir na pasta
        if arquivo.lower().endswith("_resumo.txt"):
            caminho = os.path.join(pasta_resultados, arquivo)
            
            try:
                with open(caminho, "r", encoding="utf-8") as f:
                    content = f.read()

                # Regex para capturar os dados (suporta ponto ou vírgula como decimal)
                status_match = re.search(r"Status da solução:\s*(\d+)", content)
                objetivo_match = re.search(r"Objetivo final\s*:\s*([\d\.,]+)", content)
                volume_match = re.search(r"Volume total carregado:\s*([\d\.,]+)", content)
                caixas_match = re.search(r"Número total de caixas carregadas:\s*(\d+)", content)
                gap_match = re.search(r"Gap de otimalidade:\s*([\d\.,]+)%?", content)
                tempo_match = re.search(r"Tempo de execução:\s*([\d\.,]+)", content)
                nos_match = re.search(r"Número de nós explorados:\s*([\d\.,]+)", content)

                # Função auxiliar para converter string numérica para float corretamente
                def parse_float(match):
                    if not match: return 0.0
                    val = match.group(1).replace(',', '.') # Padroniza para ponto
                    return float(val)

                # Extração dos dados
                resultados.append({
                    "Instância": arquivo.replace("_resumo.txt", "").replace(".txt", ""),
                    "Status": int(status_match.group(1)) if status_match else "N/A",
                    "Objetivo (Ocupação)": parse_float(objetivo_match),
                    "Volume Total": parse_float(volume_match),
                    "Nº Caixas": int(caixas_match.group(1)) if caixas_match else 0,
                    "Gap (%)": parse_float(gap_match),
                    "Tempo (s)": parse_float(tempo_match),
                    "Nós Explorados": parse_float(nos_match)
                })
            except Exception as e:
                print(f"Aviso: Erro ao processar o arquivo {arquivo}: {e}")

    if not resultados:
        print(f"\n[AVISO] Nenhum arquivo compatível encontrado em '{pasta_resultados}'.")
        print("Certifique-se de que os arquivos contêm 'instancia' no nome e terminam em .txt")
        return pd.DataFrame()

    # Criar DataFrame
    df = pd.DataFrame(resultados)

    # Ordenação Natural (Ex: instancia_2 vem antes de instancia_10)
    if "Instância" in df.columns:
        # Extrai o número do nome do arquivo para ordenar numericamente
        df['num_sort'] = df['Instância'].str.extract('(\d+)').astype(float)
        df = df.sort_values(by="num_sort").drop(columns=['num_sort'])

    # Salvar CSV (Formato Excel PT-BR: separado por ';' e decimal por ',')
    caminho_csv = os.path.join(pasta_resultados, "resultados_compilados.csv")
    df.to_csv(caminho_csv, index=False, sep=";", decimal=",")
    
    print("\n" + "="*60)
    print(f" COMPILAÇÃO CONCLUÍDA: {len(df)} arquivos processados")
    print(f" Arquivo salvo em: {caminho_csv}")
    print("="*60)
    
    # Exibe a tabela no terminal de forma organizada
    print(df.to_string(index=False))

    return df