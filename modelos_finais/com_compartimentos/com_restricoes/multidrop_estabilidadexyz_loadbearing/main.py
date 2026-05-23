import os
from solver import resolver_instancia

def main():
    teste = 1
    
    if teste==1:
        compartimentos = [
            (8, 8, 8)
        ]
        
        # Nova estrutura unificada de entrada. 
        # Clientes ordenados pela rota de entrega (0 recebe primeiro, depois 1, etc.)
        # Cada caixa já contém seu peso, sigma e o delta_x (margem de alcance lateral).
        clientes = [
            {
                "id_cliente": 0,
                "itens": [
                    {"dims": (6, 3, 2), "qtd": 1, "peso": 36, "sigma": 0, "delta_x": 3},
                    {"dims": (6, 4, 3), "qtd": 3, "peso": 72, "sigma": 3, "delta_x": 4},
                    {"dims": (8, 3, 2), "qtd": 0, "peso": 48, "sigma": 5, "delta_x": 3},
                    {"dims": (4, 3, 2), "qtd": 0, "peso": 24, "sigma": 0, "delta_x": 3},
                    {"dims": (4, 4, 3), "qtd": 0, "peso": 48, "sigma": 3, "delta_x": 4},
                ]
            }, {
                "id_cliente": 1,
                "itens": [
                    {"dims": (6, 3, 2), "qtd": 0, "peso": 36, "sigma": 0, "delta_x": 3},
                    {"dims": (6, 4, 3), "qtd": 1, "peso": 72, "sigma": 3, "delta_x": 4},
                    {"dims": (8, 3, 2), "qtd": 2, "peso": 48, "sigma": 5, "delta_x": 3},
                    {"dims": (4, 3, 2), "qtd": 0, "peso": 24, "sigma": 0, "delta_x": 3},
                    {"dims": (4, 4, 3), "qtd": 2, "peso": 48, "sigma": 3, "delta_x": 4},
                ]
            }, {
                "id_cliente": 2,
                "itens": [
                    {"dims": (6, 3, 2), "qtd": 1, "peso": 36, "sigma": 0, "delta_x": 3},
                    {"dims": (6, 4, 3), "qtd": 1, "peso": 72, "sigma": 3, "delta_x": 4},
                    {"dims": (8, 3, 2), "qtd": 1, "peso": 48, "sigma": 5, "delta_x": 3},
                    {"dims": (4, 3, 2), "qtd": 2, "peso": 24, "sigma": 0, "delta_x": 3},
                    {"dims": (4, 4, 3), "qtd": 1, "peso": 48, "sigma": 3, "delta_x": 4},
                ]
            }
        ]
        
        dir_path = os.path.dirname(os.path.realpath(__file__))
        arquivo_saida = os.path.join(dir_path, 'teste1.txt')
        resolver_instancia(compartimentos,clientes, arquivo_saida)

if __name__ == "__main__":
    main()