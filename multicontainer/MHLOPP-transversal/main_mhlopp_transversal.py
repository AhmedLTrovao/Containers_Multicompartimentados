import time
from solver_mhlopp_transversal import resolver_multi_compartimento 
import os

if __name__ == "__main__":
    start_time = time.time()
    path = os.path.dirname(os.path.realpath(__file__))
    
    # Lista de compartimentos: Cada tupla é (L, W, H)
    containers_example = [
        (8, 12, 8), # Compartimento 0
        (8, 12, 8), # Compartimento 1
        (8, 8, 6), # Compartimento 0
        (8, 8, 6), # Compartimento 1
        (8, 12, 8), # Compartimento 0
        (8, 12, 8), # Compartimento 1
        (8, 8, 6), # Compartimento 0
        (8, 8, 6), # Compartimento 1
    ]
    
    # Lista de caixas: (Comprimento, Largura, Altura, Quantidade)
    boxes_example = [
        (6, 3, 2, 20), 
        (6, 4, 3, 20), 
        (8, 3, 2, 20),
        (4, 3, 2, 20),
        (4, 4, 3, 20)
    ]
    
    arquivo_saida = "solucao_mhlopp_transversal.txt"
    arquivo_saida = os.path.join(path, arquivo_saida)
    
    # Chama o solver com os 3 argumentos corretos
    resolver_multi_compartimento(containers_example, boxes_example, arquivo_saida)
    
    end_time = time.time()
    print(f"\nProcesso concluído em {end_time - start_time:.2f} segundos.")
    print(f"Verifique os ficheiros '{arquivo_saida}' e '{arquivo_saida.replace('.txt', '_resumo.txt')}'.")