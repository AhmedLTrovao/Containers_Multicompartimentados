import os
from modelos_finais.com_compartimentos.com_restricoes.old.multidrop_estabilidadexyz_loadbearing.solver import resolver_instancia

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
                    {"dims": (2, 2, 2), "qtd": 2, "peso": 8, "sigma": 20, "delta_x": 2},
                    {"dims": (4, 4, 4), "qtd": 2, "peso": 64, "sigma": 20, "delta_x": 4}
                ]
            }, {
                "id_cliente": 1,
                "itens": [
                    {"dims": (2, 2, 2), "qtd": 1, "peso": 8, "sigma": 20, "delta_x": 2},
                    {"dims": (4, 4, 4), "qtd": 2, "peso": 64, "sigma": 20, "delta_x": 4}
                ]
            }, {
                "id_cliente": 2,
                "itens": [
                    {"dims": (2, 2, 2), "qtd": 2, "peso": 8, "sigma": 20, "delta_x": 2},
                    {"dims": (4, 4, 4), "qtd": 2, "peso": 64, "sigma": 20, "delta_x": 4}
                ]
            }
        ]
        
        dir_path = os.path.dirname(os.path.realpath(__file__))
        arquivo_saida = os.path.join(dir_path, 'multidrop_comparison.txt')
        resolver_instancia(compartimentos,clientes, arquivo_saida, 3600,True,True,True)

if __name__ == "__main__":
    main()