import os
from solver import resolver_instancia

def main():
    # Lista de compartimentos: (L, W, H)
    compartimentos = [
        (8, 8, 8), # k=0 (Par - acesso esquerdo)
        (8, 8, 8)
    ]
    
    # Nova estrutura unificada de entrada. 
    # Clientes ordenados pela rota de entrega (0 recebe primeiro, depois 1, etc.)
    # Cada caixa já contém seu peso, sigma e o delta_x (margem de alcance lateral).
    clientes = [
        {
            "id_cliente": 1,
            "itens": [
                {"dims": (4, 4, 8), "qtd": 7, "peso": 27, "sigma": 100, "delta_x": 4},
            ]
        },
        {
            "id_cliente": 0,
            "itens": [
                {"dims": (4, 4, 8), "qtd": 1, "peso": 27, "sigma": 100, "delta_x": 4}, 
            ]
        }
    ]
    
    dir_path = os.path.dirname(os.path.realpath(__file__))
    arquivo_saida = os.path.join(dir_path, 'saida_multicompartimento.txt')
    resolver_instancia(
        compartimentos=compartimentos, 
        clientes=clientes, 
        arquivo_saida=arquivo_saida,
        tempo_limite=3600,
        stabv=True,
        stabh=True,
        loadbearing=True
    )

if __name__ == "__main__":
    main()