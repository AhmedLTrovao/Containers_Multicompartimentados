# compile_results.py
import os
import re
import pandas as pd

def TO_F(match):
    """Função auxiliar para converter o grupo capturado do regex para float."""
    if match:
        try:
            return float(match.group(1).replace(',', '.'))
        except Exception:
            return 0.0
    return 0.0

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

    # Lista os arquivos e garante filtro correto por arquivos de resumo
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

            # --- REGEX FLEXÍVEL (Baseado estritamente nas chaves escritas pelo seu solver) ---
            # Busca: Status da solução: X
            status_m = re.search(r"Status da solu[cç][ãa]o:\s*(\d+)", content, re.IGNORECASE)
            
            # Busca: Objetivo final : X
            obj_m = re.search(r"Objetivo final\s*:\s*([\d\.,]+)", content, re.IGNORECASE)
            
            # Busca: Gap de otimalidade: X%
            gap_m = re.search(r"Gap de otimalidade\s*:\s*([\d\.,]+)%?", content, re.IGNORECASE)
            
            # Busca: Tempo de execução: X segundos
            tempo_m = re.search(r"Tempo de execu[cç][ãa]o\s*:\s*([\d\.,]+)", content, re.IGNORECASE)
            
            # Busca: Número de nós explorados: X
            nos_m = re.search(r"N[úu]mero de n[óo]s explorados\s*:\s*(\d+)", content, re.IGNORECASE)

            # Procura por expressões como "Numero de caixas", "Total de caixas", "Nº Caixas", etc.
            caixas_m = re.search(r"(?:N[úu]mero de caixas|Total de caixas|N[º°] Caixas)\s*:\s*(\d+)", content, re.IGNORECASE)

            # Caso a instância não tenha encontrado nenhuma solução viável
            inviavel = "Nenhuma solução viável encontrada" in content

            resultados.append({
                "Instância": arquivo.replace("_resumo.txt", ""),
                "Status": int(status_m.group(1)) if status_m else "N/A",
                "Ocupação (%)": TO_F(obj_m) * 100.0 if not inviavel else 0.0,
                "Nº Caixas": int(caixas_m.group(1)) if caixas_m and not inviavel else 0,
                "Gap (%)": TO_F(gap_m) if not inviavel else "N/A",
                "Tempo (s)": TO_F(tempo_m),
                "Nós Explorados": int(nos_m.group(1)) if nos_m else 0
            })

        except Exception as e:
            print(f"Aviso: Erro ao processar o arquivo {arquivo}: {e}")

    if not resultados:
        print("\n[AVISO] Nenhum dado encontrado nos arquivos de resumo.")
        return pd.DataFrame()

    # Criar DataFrame
    df = pd.DataFrame(resultados)
    
    # Ordenação natural numérica (ex: evita que 'instancia_10' venha antes de 'instancia_2')
    if "Instância" in df.columns:
        df['n_sort'] = df['Instância'].str.extract(r'(\d+)').astype(float)
        df = df.sort_values(by="n_sort").drop(columns=['n_sort'])

    # Exportar para CSV formatado para Excel nacional (; e ,)
    caminho_csv = os.path.join(pasta_resultados, "resultados_compilados.csv")
    df.to_csv(caminho_csv, index=False, sep=";", decimal=",")
    
    print("\n" + "="*60)
    print(f" COMPILAÇÃO CONCLUÍDA: {len(df)} instâncias processadas.")
    print(f" Arquivo gerado: {caminho_csv}")
    print("="*60)
    print(df.to_string(index=False))

    return df