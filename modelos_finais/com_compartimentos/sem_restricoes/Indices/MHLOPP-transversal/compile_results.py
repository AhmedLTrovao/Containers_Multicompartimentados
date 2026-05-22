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

    # Lista os arquivos e garante ordem numérica (instancia_1, instancia_2...)
    arquivos = [f for f in os.listdir(pasta_resultados) if f.endswith("_resumo.txt")]
    
    for arquivo in arquivos:
        caminho = os.path.join(pasta_resultados, arquivo)
        
        try:
            # Tratamento de encoding para aceitar caracteres especiais e acentos
            content = ""
            try:
                with open(caminho, "r", encoding="utf-8") as f:
                    content = f.read()
            except UnicodeDecodeError:
                with open(caminho, "r", encoding="latin-1") as f:
                    content = f.read()

            # --- REGEX FLEXÍVEL (Ignora acentos e espaços extras) ---
            # Busca: Status da solucao ou Status da solução
            status_m = re.search(r"Status da solu[cç][ãa]o:\s*(\d+)", content, re.IGNORECASE)
            
            # Busca: Objetivo final (Soma v_i) ou apenas Objetivo final
            obj_m = re.search(r"Objetivo final.*?:\s*([\d\.,]+)", content, re.IGNORECASE)
            
            # Busca: Volume total carregado
            vol_m = re.search(r"Volume total carregado:\s*([\d\.,]+)", content, re.IGNORECASE)
            
            # Busca: Número total de caixas ou Nº total de caixas
            caixas_m = re.search(r"N[úu]mero total de caixas:\s*(\d+)", content, re.IGNORECASE)
            
            # Busca: Gap ou Gap de otimalidade
            gap_m = re.search(r"Gap.*?:\s*([\d\.,]+)%?", content, re.IGNORECASE)
            
            # Busca: Tempo ou Tempo de execução
            tempo_m = re.search(r"Tempo.*?:\s*([\d\.,]+)", content, re.IGNORECASE)

            # Função para converter string (com vírgula ou ponto) para float
            def to_f(match):
                if match:
                    return float(match.group(1).replace(',', '.'))
                return 0.0

            resultados.append({
                "Instância": arquivo.replace("_resumo.txt", ""),
                "Status": int(status_m.group(1)) if status_m else "N/A",
                "Objetivo (Ocupação)": TO_F(obj_m),
                "Volume Total": TO_F(vol_m),
                "Nº Caixas": int(caixas_m.group(1)) if caixas_m else 0,
                "Gap (%)": TO_F(gap_m),
                "Tempo (s)": TO_F(tempo_m)
            })

        except Exception as e:
            print(f"Aviso: Erro ao processar o arquivo {arquivo}: {e}")

    if not resultados:
        print("\n[AVISO] Nenhum dado encontrado nos arquivos de resumo.")
        return pd.DataFrame()

    # Criar DataFrame e ordenar numericamente
    df = pd.DataFrame(resultados)
    if "Instância" in df.columns:
        df['n_sort'] = df['Instância'].str.extract('(\d+)').astype(float)
        df = df.sort_values(by="n_sort").drop(columns=['n_sort'])

    # Exportar para CSV formatado para Excel brasileiro (; e ,)
    caminho_csv = os.path.join(pasta_resultados, "resultados_compilados.csv")
    df.to_csv(caminho_csv, index=False, sep=";", decimal=",")
    
    print("\n" + "="*60)
    print(f" COMPILAÇÃO CONCLUÍDA: {len(df)} instâncias processadas.")
    print(f" Arquivo gerado: {caminho_csv}")
    print("="*60)
    print(df.to_string(index=False))

    return df

# Função auxiliar para o float não dar erro
def TO_F(match):
    if match:
        try:
            return float(match.group(1).replace(',', '.'))
        except:
            return 0.0
    return 0.0