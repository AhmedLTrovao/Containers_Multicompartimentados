import time
from solver import resolver_multi_compartimento 
import os

if __name__ == "__main__":
    start_time = time.time()
    path = os.path.dirname(os.path.realpath(__file__))
    
    teste = 2
    
    if teste==1:
        # Lista de compartimentos: Cada tupla é (L, W, H)
        containers_example = [
            (12, 8, 8) # Compartimento 0
        ]
        
        # Lista de caixas: (Comprimento, Largura, Altura, Quantidade)
        boxes_example = [(6, 3, 2, 2), (6, 4, 3, 5), (8, 3, 2, 3), (4, 3, 2, 2), (4,4,3,3)]
        
        # Adicionando parâmetros práticos (sigma e peso)
        Sigma = [0, 3, 5, 0, 3]
        Peso = [l*w*h for (l, w, h, b) in boxes_example]
        
        arquivo_saida = "teste1.txt"
        arquivo_saida = os.path.join(path, arquivo_saida)
        
        # Chama o solver repassando as novas entradas
        resolver_multi_compartimento(containers_example, boxes_example, arquivo_saida, Sigma, Peso)
    elif teste==2:
        containers_example = [
            (12, 8, 8), # Compartimento 0
            (12, 8, 8),
            (12, 8, 8),
            (12, 8, 8)
        ]
        
        # Lista de caixas: (Comprimento, Largura, Altura, Quantidade)
        boxes_example = [(6, 3, 2, 8), (6, 4, 3, 20), (8, 3, 2, 12), (4, 3, 2, 8), (4,4,3,12)]
        
        # Adicionando parâmetros práticos (sigma e peso)
        Sigma = [0, 3, 5, 0, 3]
        Peso = [l*w*h for (l, w, h, b) in boxes_example]
        
        arquivo_saida = "teste2.txt"
        arquivo_saida = os.path.join(path, arquivo_saida)
        
        # Chama o solver repassando as novas entradas
        resolver_multi_compartimento(containers_example, boxes_example, arquivo_saida, Sigma, Peso)