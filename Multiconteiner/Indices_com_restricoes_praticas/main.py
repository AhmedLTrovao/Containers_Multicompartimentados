# test_falhas_antigas.py
import os
import sys

# IMPORTANTE: Garanta que você está importando o SOLVER ANTIGO aqui para ver o erro.
# Se o seu arquivo antigo se chamar 'solver_antigo.py', mude para: from solver_antigo import resolver_instancia
from solver import resolver_instancia

def main():
    # 2 Compartimentos de tamanho (10, 5, 5)
    compartimentos = [
        (10, 5, 5), # k=0 (Par - acesso esquerdo, origem O_X = 0)
        (10, 5, 5)  # k=1 (Ímpar - acesso direito, origem O_X = 10)
    ]
    
    # Esta entrada foi desenhada especificamente para quebrar a lógica matemática do solver antigo:
    clientes = [
        {
            # GATILHO DA FALHA 1 (KeyError): O primeiro cliente da lista tem ID 2. 
            # O solver antigo vai tentar buscar range(num_clientes) -> demanda[0] e vai quebrar o Python na hora.
            "id_cliente": 2, 
            "itens": [
                # GATILHO DA FALHA 3 (Loadbearing com Big-M errado): 
                # Uma caixa pesada (400kg) em cima de uma que só aguenta 100kg (sigma). 
                # Devido ao erro de escala do Big-M antigo, o Gurobi pode aceitar essa violação física por erro de arredondamento.
                {"dims": (3, 2, 2), "qtd": 1, "peso": 400.0, "sigma": 9999.0, "delta_x": 1.0},
            ]
        },
        {
            "id_cliente": 5, # ID não sequencial para reforçar o KeyError se passar do primeiro.
            "itens": [
                # GATILHO DA FALHA 2 (Infeasible no Multidrop X): 
                # Caixa do cliente atual que o solver tentará colocar na origem (p = 0).
                # Na matemática do solver antigo, isso força o limite do cliente anterior a ser negativo, 
                # tornando o modelo Infeasible (Inviável) imediatamente.
                {"dims": (2, 2, 2), "qtd": 1, "peso": 10.0, "sigma": 100.0, "delta_x": 1.0},
            ]
        }
    ]
    
    dir_path = os.path.dirname(os.path.realpath(__file__))
    arquivo_saida = os.path.join(dir_path, 'saida_teste_falhas.txt')
    
    print("Executando o solver...")
    try:
        resolver_instancia(
            compartimentos=compartimentos, 
            clientes=clientes, 
            arquivo_saida=arquivo_saida,
            tempo_limite=30, # Curto, pois se o solver antigo não quebrar por erro, ele ficará travado em Infeasible
            stabv=True,
            stabh=True,
            loadbearing=True
        )
        print("\n[RESULTADO] O solver terminou sem estourar erros no Python.")
    except KeyError as ke:
        print(f"\n[FALHA 1 CONFIRMADA] O solver antigo quebrou com KeyError: {ke}")
        print("Motivo: Ele tentou acessar demanda[0] ou deltas[0], mas os IDs dos seus clientes são 2 e 5.")
    except Exception as e:
        print(f"\n[ERRO DESCONHECIDO]: {e}")

if __name__ == "__main__":
    main()