import time
from solver import resolver_multi_multidrop_pratico
import os

if __name__ == "__main__":
    start_time = time.time()
    path = os.path.dirname(os.path.realpath(__file__))
    
    # 1. Compartimentos (L, W, H) - Dispostos em 2 colunas (pares esquerda, ímpares direita)
    containers_example = [
        (10, 10, 10), (10, 10, 10), # Linha 1 (Frente)
        (10, 10, 10),  (10, 10, 10),  # Linha 2
    ]
    
    # 2. Caixas separadas por Cliente (Ordem de entrega: c=0 primeiro, c=1 segundo)
    boxes_por_cliente = [
        # Cliente 0
        [(3, 3, 2, 4)], 
        # Cliente 1
        [(3, 4, 3, 10), (4, 3, 2, 10)],
        # Cliente 2
        [(4, 4, 3, 10)]
    ]
    
    # 3. Resistência (Sigma) de cada tipo de caixa, mapeado por cliente
    sigma_por_cliente = [
        [0],    # Sigma caixas do Cliente 0
        [100, 100],    # Sigma caixas do Cliente 1
        [100]        # Sigma caixas do Cliente 2
    ]
    
    # 4. Peso de cada tipo de caixa, mapeado por cliente (usando volume como proxy)
    peso_por_cliente = [
        [l*w*h for (l,w,h,q) in c_boxes] for c_boxes in boxes_por_cliente
    ]
    
    arquivo_saida = "solucao_multidrop_multi_pratico.txt"
    arquivo_saida = os.path.join(path, arquivo_saida)
    
    print("Iniciando a modelagem Multidrop + Multicompartimentado + Restrições Físicas...")
    resolver_multi_multidrop_pratico(
        containers_example, 
        boxes_por_cliente, 
        arquivo_saida, 
        sigma_por_cliente, 
        peso_por_cliente
    )
    
    end_time = time.time()
    print(f"\nProcesso concluído em {end_time - start_time:.2f} segundos.")