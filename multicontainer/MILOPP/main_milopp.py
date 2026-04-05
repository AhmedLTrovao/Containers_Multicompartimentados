import time
from solver_milopp import resolver_multi_compartimento
import os

if __name__ == "__main__":
    start_time = time.time()
    path = os.path.dirname(os.path.realpath(__file__))
    
    # Dimensões de um único compartimento
    L, W, H = 12, 8, 8
    
    # Número de compartimentos na frota/veículo
    num_containers = 4
    
    # Lista de caixas: (Comprimento, Largura, Altura, Quantidade)
    boxes_example = [
        (6, 3, 2, 8), 
        (6, 4, 3, 10), 
        (8, 3, 2, 10),
        (4, 3, 2, 6),
        (4, 4, 3, 8)
    ]
    
    # Nome do arquivo onde as coordenadas serão salvas para o MATLAB
    arquivo_saida = "solucao_milopp.txt"
    arquivo_saida = os.path.join(path, arquivo_saida)

    resolver_multi_compartimento(L, W, H, boxes_example, num_containers, arquivo_saida)
    
    end_time = time.time()
    print(f"\nProcesso concluído em {end_time - start_time:.2f} segundos.")
    print(f"Verifique os arquivos '{arquivo_saida}' e '{arquivo_saida.replace('.txt', '_resumo.txt')}'.")