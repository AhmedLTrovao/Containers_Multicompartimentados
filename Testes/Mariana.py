def gerar_coordenadas_normais(dimensao_maxima, dimensoes_caixas):
    """
    Gera um conjunto de coordenadas otimizado ('normal patterns') para um único eixo.

    Args:
        dimensao_maxima (int): O tamanho do contêiner nesse eixo (L, W ou H).
        dimensoes_caixas (list or set): Uma coleção com as dimensões únicas
                                         das caixas para esse eixo (ex: todos os comprimentos).

    Returns:
        list: Uma lista ordenada de coordenadas permitidas.
    """
    
    # 1. Comece com o ponto de origem. Usamos um 'set' para evitar duplicatas.
    coordenadas = {0}

    # 2. Itere sobre cada dimensão de caixa única.
    for d in sorted(list(dimensoes_caixas)):
        # Criamos uma cópia para adicionar os novos pontos, para não modificar o
        # conjunto enquanto iteramos sobre ele.
        novas_coordenadas_a_adicionar = set()
        
        # Para cada coordenada que já encontramos...
        for c in coordenadas:
            # ...some múltiplos da dimensão atual.
            novo_ponto = c + d
            while novo_ponto <= dimensao_maxima:
                novas_coordenadas_a_adicionar.add(novo_ponto)
                novo_ponto += d
        
        # Adiciona todos os novos pontos encontrados ao nosso conjunto principal.
        coordenadas.update(novas_coordenadas_a_adicionar)

    # Uma pequena otimização final: remove pontos onde nem a menor caixa cabe.
    if not dimensoes_caixas: return [0] # Evita erro se a lista for vazia
    menor_dimensao = min(dimensoes_caixas)
    coordenadas_finais = [c for c in coordenadas if c <= dimensao_maxima - menor_dimensao]
    
    # Adiciona a coordenada 0 se ela não estiver na lista (caso especial)
    if 0 not in coordenadas_finais:
        coordenadas_finais.insert(0,0)

    return sorted(coordenadas_finais)

import gurobipy as gp
from gurobipy import GRB
from itertools import product

def escrever_solucao_grid(x, box_types, L, W, H, filename):
    """
    Função adaptada para escrever a solução do modelo de grade em um arquivo.
    """
    print(f"\n--- Escrevendo solução no arquivo '{filename}'... ---")
    try:
        with open(filename, 'w') as f:
            # Escreve a primeira linha com as dimensões do contêiner
            f.write(f"{L} {W} {H}\n")
            
            # Itera sobre as variáveis de decisão para encontrar as caixas empacotadas
            for i, p, q, r in x:
                if x[i, p, q, r].X > 0.5:
                    li, wi, hi = box_types[i]['dims']
                    # O 'tipo' é o próprio índice 'i' do tipo de caixa (adicionamos 1 para ser mais legível)
                    tipo = i + 1
                    cliente = 1
                    
                    # Escreve a linha formatada para a caixa
                    f.write(f"{p} {q} {r} {li} {wi} {hi} {tipo} {cliente}\n")
        
        print("Arquivo de solução salvo com sucesso.")
    except Exception as e:
        print(f"ERRO: Não foi possível escrever no arquivo de solução. Causa: {e}")


def executar_e_relatar_grid(model, x, box_types, L, W, H, time_limit_seconds, output_filename):
    """
    Função adaptada para executar o modelo de grade, relatar os resultados 
    e salvar a solução.
    """
    model.setParam('TimeLimit', time_limit_seconds)
    model.setParam('OutputFlag', 0)

    print(f"--- Executando modelo de grade com limite de tempo de {time_limit_seconds} segundos... ---")
    
    model.optimize()

    print("\n" + "="*45)
    print("      RELATÓRIO FINAL DE EXECUÇÃO (MODELO DE GRADE)")
    print("="*45)

    if model.SolCount > 0:
        status_solucao = "Ótima" if model.status == GRB.OPTIMAL else "Subótima (Limite de Tempo Atingido)"
        
        print(f"Status da Solução: {status_solucao}")
        print(f"Valor Final Atingido (FO): {model.ObjVal:.4f}")
        print(f"Gap de Otimalidade: {model.MIPGap * 100:.4f}%")
        print(f"Tempo Computacional Despendido: {model.Runtime:.4f} segundos")
        
        # Chama a função adaptada para escrever a solução em um arquivo
        escrever_solucao_grid(x, box_types, L, W, H, output_filename)
    else:
        print("Status da Solução: Nenhuma solução viável foi encontrada.")
        print(f"Tempo Computacional Despendido: {model.Runtime:.4f} segundos")

    print("="*45 + "\n")


def solve_grid_based_model():
    """
    Implementa e resolve o modelo de grade, usando as funções de relatório.
    """
    try:
        # --- 1. Dados do Modelo ---
        L, W, H = 12, 8, 8
        box_types = {
            0: {'dims': (6, 3, 2), 'b': 2, 'val': (6*3*2/(L*W*H))},
            1: {'dims': (6, 4, 3), 'b': 5, 'val': (6*4*3/(L*W*H))},
            2: {'dims': (8, 3, 2), 'b': 3, 'val': (8*3*2/(L*W*H))},
            3: {'dims': (4, 3, 2), 'b': 2, 'val': (4*3*2/(L*W*H))},
            4: {'dims': (4, 4, 3), 'b': 3, 'val': (4*4*3/(L*W*H))},
        }
        m = len(box_types)
        '''
        # --- 2. Geração de Coordenadas (Padrões Normais) ---
        def get_normal_pattern_coords(max_dim, all_dims):
            coords = {0}
            for d in sorted(list(all_dims)):
                new_coords = list(coords)
                for c in coords:
                    for k in range(1, (max_dim // d) + 1):
                        new_c = c + k * d
                        if new_c <= max_dim: new_coords.append(new_c)
                        else: break
                coords.update(new_coords)
            min_box_dim = min(all_dims)
            return sorted([c for c in coords if c <= max_dim - min_box_dim])
        '''

        all_lengths = {bt['dims'][0] for bt in box_types.values()}
        all_widths = {bt['dims'][1] for bt in box_types.values()}
        all_heights = {bt['dims'][2] for bt in box_types.values()}
        X_coords = gerar_coordenadas_normais(L, all_lengths)
        Y_coords = gerar_coordenadas_normais(W, all_widths)
        Z_coords = gerar_coordenadas_normais(H, all_heights)

        # --- 3. Construção do Modelo ---
        model = gp.Model("GridBasedContainerLoading")
        
        x = {}
        for i in range(m):
            li, wi, hi = box_types[i]['dims']
            for p in [c for c in X_coords if c <= L - li]:
                for q in [c for c in Y_coords if c <= W - wi]:
                    for r in [c for c in Z_coords if c <= H - hi]:
                        x[i, p, q, r] = model.addVar(vtype=GRB.BINARY, name=f"x_{i}_{p}_{q}_{r}")

        model.setObjective(gp.quicksum(box_types[i]['val'] * x[i, p, q, r] for i, p, q, r in x), GRB.MAXIMIZE)

        for s, t, u in product(X_coords, Y_coords, Z_coords):
            boxes_covering_stu = [x[i, p, q, r] for i, p, q, r in x if (p <= s < p + box_types[i]['dims'][0]) and (q <= t < q + box_types[i]['dims'][1]) and (r <= u < r + box_types[i]['dims'][2])]
            if boxes_covering_stu:
                model.addConstr(gp.quicksum(boxes_covering_stu) <= 1)

        for i in range(m):
            placements_of_type_i = gp.quicksum(x[i, p, q, r] for i_p, p, q, r in x if i_p == i)
            model.addConstr(placements_of_type_i <= box_types[i]['b'])

        # --- 4. Execução e Relatório ---
        executar_e_relatar_grid(
            model=model,
            x=x,
            box_types=box_types,
            L=L, W=W, H=H,
            time_limit_seconds=60,
            output_filename="solucao_gridbased.txt"
        )

    except gp.GurobiError as e:
        print(f"Gurobi Error code {e.errno}: {e}")

# Executa o script principal
solve_grid_based_model()