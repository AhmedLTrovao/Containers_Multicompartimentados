import gurobipy as gp
from gurobipy import GRB
from math import floor

def gerar_coordenadas_normais(dimensao_maxima, dimensoes_caixas):
    coordenadas = {0}
    for d in sorted(list(dimensoes_caixas)):
        novas = set()
        for c_ in coordenadas:
            novo = c_ + d
            while novo <= dimensao_maxima:
                novas.add(novo)
                novo += d
        coordenadas.update(novas)
    if not dimensoes_caixas: return [0]
    menor = min(dimensoes_caixas)
    finais = [c for c in coordenadas if c <= dimensao_maxima - menor]
    if 0 not in finais: finais.insert(0, 0)
    return sorted(finais)

def resolver_multi_multidrop_pratico(compartimentos, clientes_boxes, arquivo_saida, sigma, peso, alpha, beta, gamma, prioridade):
    num_compartimentos = len(compartimentos)
    num_clientes = len(clientes_boxes)
    
    todas_caixas = [box for cliente in clientes_boxes for box in cliente]
    all_L = {b[0] for b in todas_caixas}
    all_W = {b[1] for b in todas_caixas}
    all_H = {b[2] for b in todas_caixas}

    model = gp.Model("3D_Multi_Multidrop_Pratico")

    # --- 1: Variáveis de Decisão e Fronteiras ---
    x = {}
    B = {} # Fronteira Multidrop

    # Guarda os conjuntos de cada compartimento para usar depois
    Info_K = {}

    for k, (L_k, W_k, H_k) in enumerate(compartimentos):
        if k % 2 == 0:
            O_X_k = 0
        else:
            O_X_k = compartimentos[k-1][0] 
        O_Y_k = sum(compartimentos[c][1] for c in range(0, k-1, 2))
        
        E_L_k = gerar_coordenadas_normais(L_k, all_L)
        E_W_k = gerar_coordenadas_normais(W_k, all_W)
        E_H_k = gerar_coordenadas_normais(H_k, all_H)
        
        X_k = [p + O_X_k for p in E_L_k]
        Y_k = [q + O_Y_k for q in E_W_k]
        Z_k = E_H_k
        
        Info_K[k] = (O_X_k, O_Y_k, X_k, Y_k, Z_k)
        
        for c in range(num_clientes):
            B[k, c] = model.addVar(lb=O_Y_k, ub=O_Y_k + W_k, name=f"B_k{k}_c{c}")
            
            for i, (li, wi, hi, qty) in enumerate(clientes_boxes[c]):
                X_ik = [p for p in X_k if p + li <= O_X_k + L_k]
                Y_ik = [q for q in Y_k if q + wi <= O_Y_k + W_k]
                Z_ik = [r for r in Z_k if r + hi <= H_k]
                
                for p in X_ik:
                    for q in Y_ik:
                        for r in Z_ik:
                            x[k, c, i, p, q, r] = model.addVar(vtype=GRB.BINARY, name=f"x_k{k}_c{c}_i{i}_{p}_{q}_{r}")

    model.update()


   # --- 2: Função Objetivo (Testes com Prioridade/Lucro) ---
    obj_expr = gp.LinExpr()
    for (k, c, i, p, q, r), var in x.items():
        li, wi, hi, _ = clientes_boxes[c][i]
        volume_caixa = li * wi * hi
        # Multiplica o volume pelo peso/prioridade daquele cliente
        obj_expr += (volume_caixa * prioridade[c][i]) * var
        
        
    model.setObjective(obj_expr, GRB.MAXIMIZE)
 # --- 3: Restrições de Fronteira Multidrop LATERAL (Eixo X) ---
    for k, (L_k, W_k, H_k) in enumerate(compartimentos):
        O_X_k, O_Y_k, X_k, Y_k, Z_k = Info_K[k]
        is_left = (k % 2 == 0) # Pares ficam à esquerda no Python
        
        for c in range(num_clientes):
            # A fronteira agora vive no eixo X
            B[k, c].lb = O_X_k
            B[k, c].ub = O_X_k + L_k
            
            if is_left:
                # Compartimento ESQUERDO: Porta em O_X_k. Fronteira cresce para a direita (->).
                if c > 0:
                    model.addConstr(B[k, c] >= B[k, c-1], name=f"SeqB_L_k{k}_c{c}")
            else:
                # Compartimento DIREITO: Porta em O_X_k + L_k. Fronteira diminui para a esquerda (<-).
                if c > 0:
                    model.addConstr(B[k, c] <= B[k, c-1], name=f"SeqB_R_k{k}_c{c}")

    for (k, c, i, p, q, r), var in x.items():
        li = clientes_boxes[c][i][0]
        O_X_k, O_Y_k, X_k, Y_k, Z_k = Info_K[k]
        L_k = compartimentos[k][0]
        M = O_X_k + L_k + 10 # Um Big-M grande o suficiente
        
        is_left = (k % 2 == 0)

        if is_left:
            # ESQUERDA: Carga do cliente 'c' fica ENTRE a fronteira de 'c-1' e 'c'
            if c > 0:
                model.addConstr(p >= B[k, c-1] - M * (1 - var), name=f"DropLx1_k{k}c{c}i{i}")
            model.addConstr(p + li <= B[k, c] + M * (1 - var), name=f"DropLx2_k{k}c{c}i{i}")
        else:
            # DIREITA: Lógica invertida! Carga do cliente 'c' fica ENTRE 'c' e 'c-1'
            B_prev = B[k, c-1] if c > 0 else (O_X_k + L_k)
            model.addConstr(p + li <= B_prev + M * (1 - var), name=f"DropRx1_k{k}c{c}i{i}")
            model.addConstr(p >= B[k, c] - M * (1 - var), name=f"DropRx2_k{k}c{c}i{i}")

    # --- 4: Restrições de Não Sobreposição ---
    print("Gerando restrições de não sobreposição...")
    for k, (L_k, W_k, H_k) in enumerate(compartimentos):
        O_X_k, O_Y_k, X_k, Y_k, Z_k = Info_K[k]
        vars_k = [(c, i, p, q, r) for (k_, c, i, p, q, r) in x if k_ == k]
        for s in X_k:
            for t in Y_k:
                for u in Z_k:
                    covering = []
                    for (c, i, p, q, r) in vars_k:
                        li, wi, hi, _ = clientes_boxes[c][i]
                        if (p <= s < p + li) and (q <= t < q + wi) and (r <= u < r + hi):
                            covering.append(x[k, c, i, p, q, r])
                    if covering:
                        model.addConstr(gp.quicksum(covering) <= 1, name=f"over_k{k}_{s}_{t}_{u}")

    # --- 5: Restrição de Inventário ---
    for c in range(num_clientes):
        for i in range(len(clientes_boxes[c])):
            total_placed = gp.quicksum(v for (k_, c_, i_, p, q, r), v in x.items() if c_==c and i_==i)
            model.addConstr(total_placed <= clientes_boxes[c][i][3], name=f"inv_c{c}_i{i}")

    # --- 6: Restrições Práticas (Estabilidades e Empilhamento) ---
    print("Gerando restrições de estabilidade e loadbearing...")
    # alpha, beta, gamma = 1.0, 1.0, 1.0
    
    # 6.1 Estabilidade Vertical (Z)
    for (k, c, i, p, q, r), var in x.items():
        if r == 0: continue
        li, wi, hi, _ = clientes_boxes[c][i]
        O_X_k, O_Y_k, X_k, Y_k, Z_k = Info_K[k]
        
        lhs_z = gp.LinExpr()
        for c_ in range(num_clientes):
            for j in range(len(clientes_boxes[c_])):
                lj, wj, hj, _ = clientes_boxes[c_][j]
                r_linha = r - hj
                if r_linha in Z_k:
                    rel_p = [pl for pl in X_k if (p - lj + 1 <= pl <= p + li - 1)]
                    rel_q = [ql for ql in Y_k if (q - wj + 1 <= ql <= q + wi - 1)]
                    for p_linha in rel_p:
                        for q_linha in rel_q:
                            if (k, c_, j, p_linha, q_linha, r_linha) in x:
                                L_ij = min(p + li, p_linha + lj) - max(p, p_linha)
                                W_ij = min(q + wi, q_linha + wj) - max(q, q_linha)
                                lhs_z += (L_ij * W_ij) * x[k, c_, j, p_linha, q_linha, r_linha]
        model.addConstr(lhs_z >= alpha * li * wi * var)

    # 6.2 Estabilidade Horizontal (X)
    for (k, c, i, p, q, r), var in x.items():
        O_X_k, O_Y_k, X_k, Y_k, Z_k = Info_K[k]
        if p == O_X_k: continue
        li, wi, hi, _ = clientes_boxes[c][i]
        
        lhs_x = gp.LinExpr()
        for c_ in range(num_clientes):
            for j in range(len(clientes_boxes[c_])):
                lj, wj, hj, _ = clientes_boxes[c_][j]
                p_linha = p - lj
                if p_linha in X_k:
                    rel_q = [ql for ql in Y_k if (q - wj + 1 <= ql <= q + wi - 1)]
                    rel_r = [rl for rl in Z_k if (r - hj + 1 <= rl <= r + hi - 1)]
                    for q_linha in rel_q:
                        for r_linha in rel_r:
                            if (k, c_, j, p_linha, q_linha, r_linha) in x:
                                W_ij = min(q + wi, q_linha + wj) - max(q, q_linha)
                                H_ij = min(r + hi, r_linha + hj) - max(r, r_linha)
                                lhs_x += (W_ij * H_ij) * x[k, c_, j, p_linha, q_linha, r_linha]
        model.addConstr(lhs_x >= beta * wi * hi * var)

    # 6.3 Estabilidade Horizontal (Y)
    for (k, c, i, p, q, r), var in x.items():
        O_X_k, O_Y_k, X_k, Y_k, Z_k = Info_K[k]
        if q == O_Y_k: continue
        li, wi, hi, _ = clientes_boxes[c][i]
        
        lhs_y = gp.LinExpr()
        for c_ in range(num_clientes):
            for j in range(len(clientes_boxes[c_])):
                lj, wj, hj, _ = clientes_boxes[c_][j]
                q_linha = q - wj
                if q_linha in Y_k:
                    rel_p = [pl for pl in X_k if (p - lj + 1 <= pl <= p + li - 1)]
                    rel_r = [rl for rl in Z_k if (r - hj + 1 <= rl <= r + hi - 1)]
                    for p_linha in rel_p:
                        for r_linha in rel_r:
                            if (k, c_, j, p_linha, q_linha, r_linha) in x:
                                L_ij = min(p + li, p_linha + lj) - max(p, p_linha)
                                H_ij = min(r + hi, r_linha + hj) - max(r, r_linha)
                                lhs_y += (L_ij * H_ij) * x[k, c_, j, p_linha, q_linha, r_linha]
        model.addConstr(lhs_y >= gamma * li * hi * var)

    # 6.4 Loadbearing (Pressão / Resistência ao Empilhamento)
    for k, (L_k, W_k, H_k) in enumerate(compartimentos):
        O_X_k, O_Y_k, X_k, Y_k, Z_k = Info_K[k]
        for s in X_k:
            for t in Y_k:
                for u in Z_k:
                    lhs_pressao = gp.LinExpr()
                    rhs_resistencia = gp.LinExpr()
                    
                    for c_ in range(num_clientes):
                        for j in range(len(clientes_boxes[c_])):
                            lj, wj, hj, _ = clientes_boxes[c_][j]
                            # Pressão (Caixas ACIMA de u)
                            rel_p1 = [p for p in X_k if (s - lj + 1 <= p <= s)]
                            rel_q1 = [q for q in Y_k if (t - wj + 1 <= q <= t)]
                            rel_r1 = [r for r in Z_k if (u + 1 <= r <= H_k - hj)]
                            for p1 in rel_p1:
                                for q1 in rel_q1:
                                    for r1 in rel_r1:
                                        if (k, c_, j, p1, q1, r1) in x:
                                            lhs_pressao += (peso[c_][j] / (lj * wj)) * x[k, c_, j, p1, q1, r1]
                                            
                            # Resistência (Caixas NESSE voxel u)
                            rel_p = [p for p in X_k if (s - lj + 1 <= p <= s)]
                            rel_q = [q for q in Y_k if (t - wj + 1 <= q <= t)]
                            rel_r = [r for r in Z_k if (u - hj + 1 <= r <= u)]
                            for p in rel_p:
                                for q in rel_q:
                                    for r in rel_r:
                                        if (k, c_, j, p, q, r) in x:
                                            rhs_resistencia += sigma[c_][j] * x[k, c_, j, p, q, r]
                                            
                    if lhs_pressao.size() > 0 or rhs_resistencia.size() > 0:
                        model.addConstr(lhs_pressao <= rhs_resistencia)

    # --- 7: Resolver ---
    model.Params.TimeLimit = 3600
    model.Params.MIPFocus = 1 # Foca em achar soluções rapidamente (importante para modelos densos)
    model.optimize()

    # --- 8: Output unificado ---
    tipo_dict = {}
    tipo_counter = 1
    for c in range(num_clientes):
        for i, (li, wi, hi, _) in enumerate(clientes_boxes[c]):
            # A chave agora é o cliente e o índice da caixa (c, i)
            # Isso garante que caixas idênticas em tamanho, mas com sigmas diferentes, ganhem IDs únicos!
            tipo_dict[(c, i)] = tipo_counter
            tipo_counter += 1

    with open(arquivo_saida, "w") as f:
        f.write(f"{num_compartimentos}\n")
        for (L_c, W_c, H_c) in compartimentos:
            f.write(f"{L_c} {W_c} {H_c}\n")
            
        if hasattr(model, 'SolCount') and model.SolCount > 0:
            for (k, c, i, p, q, r) in x:
                if x[k, c, i, p, q, r].X > 0.5:
                    li, wi, hi, _ = clientes_boxes[c][i]
                    # Busca o tipo pela chave exata (c, i)
                    tipo = tipo_dict[(c, i)]
                    cliente_id = c 
                    f.write(f"{p} {q} {r} {li} {wi} {hi} {tipo} {cliente_id} {k}\n")