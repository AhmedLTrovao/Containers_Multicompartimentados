# main.py
import os
import time
from read_data_IRP import ler_instancias_praticas
from solver_IRP import resolver_instancia
from compile_results_IRP import compilar_resultados

if __name__ == "__main__":
    # 1. Configurações de Caminhos
    # Troque pelo caminho real onde salvou o seu arquivo de instâncias numéricas
    arquivo_instancias = r"C:\Users\progo\Containers_Multicompartimentados\Multiconteiner\Indices_com_restricoes_praticas\DATA_1_m05b2d1\DATA_1_n30m05b2d1.dat"
    #arquivo_instancias = r"C:\Users\progo\Containers_Multicompartimentados\Multiconteiner\Indices_com_restricoes_praticas\teste_basico.txt"
    
    # Pasta onde todos os resultados (txt, _resumo, _log) serão salvos
    pasta_saida = "resultados DATA_1_n30m05b2d1"
    #pasta_saida = "resultados teste_basico"
    os.makedirs(pasta_saida, exist_ok=True)

    start_time_geral = time.time()

    # 2. Loop de Resolução
    print(f"Iniciando processamento do arquivo: {arquivo_instancias}")
    
    # O ler_instancias_praticas retorna (id, compartimentos, clientes) para cada bloco
    for id_inst, compartimentos, clientes in ler_instancias_praticas(arquivo_instancias):
        print(f"\n" + "="*40)
        print(f" Resolvendo instância {id_inst}...")
        print(f" Com {len(compartimentos)} compartimentos e dados estruturados de clientes.")
        print("="*40)
        
        # Define o nome do arquivo de saída baseado no ID da instância
        nome_base = f"instancia_{id_inst}"
        caminho_arquivo_saida = os.path.join(pasta_saida, f"{nome_base}.txt")
        
        # 3. Chama o Solver atualizado com as regras práticas
        try:
            resolver_instancia(
                compartimentos=compartimentos, 
                clientes=clientes, 
                arquivo_saida=caminho_arquivo_saida,
                tempo_limite=3600,
                stabv=False,         # Estabilidade Vertical ativada
                stabh=False,         # Estabilidade Horizontal ativada
                loadbearing=False,    # Capacidade de carga/esmagamento ativada
                multidrop=False         # Multidrop ativado
            )
        except Exception as e:
            print(f"Erro crítico ao resolver instância {id_inst}: {e}")

    # 4. Compilação Final
    print("\n" + "="*50)
    print("Processamento de todas as instâncias concluído.")
    print(f"Tempo total decorrido: {time.time() - start_time_geral:.2f} segundos.")
    
    # Chama o script de compilação que gera o CSV para Excel
    compilar_resultados(pasta_saida)
    print("="*50)