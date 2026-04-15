import os
import time
from read_data import ler_multiplas_instancias # Nome da função no novo read_data
from solver_mhlopp_transversal import resolver_multi_compartimento
from compile_results import compilar_resultados

if __name__ == "__main__":
    # 1. Configurações de Caminhos
    # Use o r"" para evitar problemas com as barras invertidas do Windows
    arquivo_instancias = r"C:\Users\progo\Containers_Multicompartimentados\Multiconteiner\Indices\MHLOPP-transversal\DATA_1_m05b2d1\DATA_1_n10m05b2d1.dat"
    
    # Pasta onde todos os resultados (txt e resumo) serão salvos
    pasta_saida = "resultados_n10m05b2d1"
    os.makedirs(pasta_saida, exist_ok=True)

    start_time_geral = time.time()

    # 2. Loop de Resolução
    # O ler_multiplas_instancias retorna (id, compartimentos, boxes) para cada bloco no arquivo
    print(f"Iniciando processamento do arquivo: {arquivo_instancias}")
    
    for id_inst, compartimentos, boxes in ler_multiplas_instancias(arquivo_instancias):
        print(f"\n" + "="*40)
        print(f" Resolvendo instância {id_inst}...")
        print(f" Com {len(compartimentos)} compartimentos e {len(boxes)} tipos de caixas.")
        print("="*40)
        
        # Define o nome do arquivo de saída baseado no ID da instância
        nome_base = f"instancia_{id_inst}"
        caminho_arquivo_saida = os.path.join(pasta_saida, f"{nome_base}.txt")
        
        # 3. Chama o Solver de Índices
        # Argumentos: (lista_compartimentos, lista_caixas, string_caminho_saida)
        try:
            resolver_multi_compartimento(compartimentos, boxes, caminho_arquivo_saida)
        except Exception as e:
            print(f"Erro crítico ao resolver instância {id_inst}: {e}")

    # 4. Compilação Final
    print("\n" + "="*50)
    print("Processamento de todas as instâncias concluído.")
    print(f"Tempo total decorrido: {time.time() - start_time_geral:.2f} segundos.")
    
    # Chama o script de compilação que gera o CSV para Excel
    compilar_resultados(pasta_saida)
    print("="*50)