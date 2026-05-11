import time
from solver import resolver_multi_multidrop_pratico
import os

if __name__ == "__main__":
    start_time = time.time()
    path = os.path.dirname(os.path.realpath(__file__))
    
    teste = "multidrop2"
    
    if teste == "loadbearing1":
        containers_example = [
            (10, 10, 10)
        ]
        boxes_por_cliente = [
            # Cliente 0
            [(5, 5, 5, 4), (5, 5, 5, 4)],
        ]
        sigma_por_cliente = [
            [100, 0],    # Sigma caixas do Cliente -
        ]
        peso_por_cliente = [
            [l*w*h for (l,w,h,q) in c_boxes] for c_boxes in boxes_por_cliente
        ]
        alpha =beta =gamma = 0
    elif teste == "loadbearing2":
        containers_example = [
            (10, 10, 10)
        ]
        boxes_por_cliente = [
            # Cliente 0
            [(5, 5, 5, 0), (5, 5, 5, 8)],
        ]
        sigma_por_cliente = [
            [100, 0],    # Sigma caixas do Cliente -
        ]
        peso_por_cliente = [
            [l*w*h for (l,w,h,q) in c_boxes] for c_boxes in boxes_por_cliente
        ]
        alpha =beta =gamma = 0
    elif teste == "estabilidade":
        containers_example = [
            (10, 10, 10)
        ]
        boxes_por_cliente = [
            # Cliente 0
            [(6, 6, 5, 4)],
        ]
        sigma_por_cliente = [
            [1000],    # Sigma caixas do Cliente -
        ]
        peso_por_cliente = [
            [l*w*h for (l,w,h,q) in c_boxes] for c_boxes in boxes_por_cliente
        ]
        alpha =beta =gamma=1
    elif teste == "multidrop":
        containers_example = [
            (10, 10, 10),
            (10, 10, 10)
        ]
        boxes_por_cliente = [
            # Cliente 0
            [(5, 10, 5, 4)],
            # cliente 1
            [(5, 10, 5, 4)],
            
        ]
        sigma_por_cliente = [
            [1000], [1000]   # Sigma caixas do Cliente -
        ]
        peso_por_cliente = [
            [l*w*h for (l,w,h,q) in c_boxes] for c_boxes in boxes_por_cliente
        ]
        alpha =beta =gamma=0
    elif teste == "multidrop2":
        containers_example = [
            (10, 10, 10),
            (10, 10, 10)
        ]
        boxes_por_cliente = [
            # Cliente 0
            [(5, 10, 10, 1)],
            # cliente 1
            [(5, 10, 5, 3)],
            # cliente 2
            [(5, 10, 5, 4)],
        ]
        sigma_por_cliente = [
            [100000], [100000], [100000]   # Sigma caixas do Cliente -
        ]
        peso_por_cliente = [
            [l*w*h for (l,w,h,q) in c_boxes] for c_boxes in boxes_por_cliente
        ]
        prioridade = [[1],[1],[1]]
        alpha =beta =gamma=0
    arquivo_saida = "solucao_multidrop_multi_pratico.txt"
    arquivo_saida = os.path.join(path, arquivo_saida)
    
    print("Iniciando a modelagem Multidrop + Multicompartimentado + Restrições Físicas...")
    resolver_multi_multidrop_pratico(
        containers_example, 
        boxes_por_cliente, 
        arquivo_saida, 
        sigma_por_cliente, 
        peso_por_cliente,
        alpha, beta, gamma, prioridade
    )
    
    end_time = time.time()
    print(f"\nProcesso concluído em {end_time - start_time:.2f} segundos.")