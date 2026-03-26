import os
import re
import pandas as pd

def compilar_resultados(pasta_resultados):
    """
    Lê todos os arquivos *_resumo.txt na pasta especificada e compila as métricas principais
    em um único DataFrame salvo como CSV.
    """

    resultados = []

    # Verifica se a pasta existe antes de começar
    if not os.path.exists(pasta_resultados):
        print(f"Erro: A pasta {pasta_resultados} não existe.")
        return pd.DataFrame()

    for arquivo in os.listdir(pasta_resultados):
        # O solver agora deve gerar arquivos com este sufixo
        if arquivo.endswith("_resumo.txt"):
            caminho = os.path.join(pasta_resultados, arquivo)
            
            try:
                with open(caminho, "r", encoding="utf-8") as f:
                    content = f.read()

                # Expressões regulares para capturar os dados do resumo
                status_match = re.search(r"Status da solução:\s*(\d+)", content)
                objetivo_match = re.search(r"Objetivo final\s*:\s*([\d\.]+)", content)
                volume_match = re.search(r"Volume total carregado:\s*([\d\.]+)", content)
                caixas_match = re.search(r"Número total de caixas carregadas:\s*(\d+)", content)
                gap_match = re.search(r"Gap de otimalidade:\s*([\d\.]+)%?", content)
                tempo_match = re.search(r"Tempo de execução:\s*([\d\.]+)", content)
                nos_match = re.search(r"Número de nós explorados:\s*([\d\.]+)", content)

                # Extrair valores com segurança
                status = int(status_match.group(1)) if status_match else None
                objetivo = float(objetivo_match.group(1)) if objetivo_match else None
                volume = float(volume_match.group(1)) if volume_match else None
                caixas = int(caixas_match.group(1)) if caixas_match else None
                gap = float(gap_match.group(1)) if gap_match else 0.0
                tempo = float(tempo_match.group(1)) if tempo_match else None
                nos = float(nos_match.group(1)) if nos_match else 0

                nome_instancia = arquivo.replace("_resumo.txt", "")

                resultados.append({
                    "Instância": nome_instancia,
                    "Status": status,
                    "Objetivo (Ocupação)": objetivo,
                    "Volume Total": volume,
                    "Nº Caixas": caixas,
                    "Gap (%)": gap,
                    "Tempo (s)": tempo,
                    "Nós Explorados": nos
                })
            except Exception as e:
                print(f"Erro ao ler o arquivo {arquivo}: {e}")

    # 1. Verificação de lista vazia (evita o KeyError: 'Instância')
    if not resultados:
        print("\n[AVISO] Nenhum dado foi compilado.")
        print("Certifique-se de que o solver está gerando os arquivos '_resumo.txt'.")
        return pd.DataFrame()

    # 2. Converter em DataFrame
    df = pd.DataFrame(resultados)

    # 3. Ordenar pelo nome da instância (ex: instancia_1, instancia_2...)
    # Usamos uma função natural sort para evitar que 'instancia_10' venha antes de 'instancia_2'
    if "Instância" in df.columns:
        df['num'] = df['Instância'].str.extract('(\d+)').astype(int)
        df.sort_values(by="num", inplace=True)
        df.drop(columns=['num'], inplace=True)

    # 4. Salvar CSV
    caminho_saida = os.path.join(pasta_resultados, "resultados_compilados.csv")
    # sep=";" e decimal="," facilitam a abertura direta no Excel (PT-BR)
    df.to_csv(caminho_saida, index=False, sep=";", decimal=",")
    
    print("-" * 30)
    print(f"Sucesso! {len(df)} instâncias compiladas.")
    print(f"Arquivo salvo em: {caminho_saida}")
    print("-" * 30)
    print(df.to_string(index=False)) # Mostra a tabela limpa no console

    return df