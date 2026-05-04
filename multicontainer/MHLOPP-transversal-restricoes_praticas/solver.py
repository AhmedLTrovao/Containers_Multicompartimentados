import gurobipy as gp
from gurobipy import GRB

def gerar_coordenadas_normais(dimensao_maxima, dimensoes_caixas):
    coordenadas = {0}
    for d in sorted(list(dimensoes_caixas)):
        novas = set()
        for c in coordenadas:
            novo = c + d
            while novo <= dimensao_maxima:
                novas.add(novo)
                novo += d
        coordenadas.update(novas)
    if not dimensoes_caixas:
        return [0]
    menor_dimensao = min(dimensoes_caixas)
    coordenadas_finais = [c for c in coordenadas if c <= dimensao_maxima - menor_dimensao]
    if 0 not in coordenadas_finais:
        coordenadas_finais.insert(0, 0)
    return sorted(coordenadas_finais)

def resolver_multi_compartimento(compartimentos, boxes, arquivo_saida, sigma, peso):
    m = len(boxes)
    num_compartimentos = len(compartimentos)
    total_capacity = sum(L * W * H for (L, W, H) in compartimentos)
    v = [(l*w*h)/total_capacity for (l,w,h,b) in boxes]
    
    all_lengths = {l for (l,_,_,_) in boxes}
    all_widths  = {w for (_,w,_,_) in boxes}
    all_heights = {h for (_,_,h,_) in boxes}

    model = gp.Model("MultiContainerGrid_Pratico")

    # --- 1: Variáveis de Decisão ---
    x = {}
    for k, (L_k, W_k, H_k) in enumerate(compartimentos):
        if k % 2 == 0:
            O_X_k = 0
        else:
            O_X_k = compartimentos[k-1][0] 
        O_Y_k = sum(compartimentos[c][1] for c in range(0, k-1, 2))
        
        E_L_k = gerar_coordenadas_normais(L_k, all_lengths)
        E_W_k = gerar_coordenadas_normais(W_k, all_widths)
        E_H_k = gerar_coordenadas_normais(H_k, all_heights)
        
        X_k = [x_ + O_X_k for x_ in E_L_k] 
        Y_k = [y_ + O_Y_k for y_ in E_W_k]
        Z_k = E_H_k
        
        for i in range(m):
            li, wi, hi, bi = boxes[i]
            
            X_ik = [p for p in X_k if p + li <= O_X_k + L_k]
            Y_ik = [q for q in Y_k if q + wi <= O_Y_k + W_k]
            Z_ik = [r for r in Z_k if r + hi <= H_k]
            
            for p in X_ik:
                for q in Y_ik:
                    for r in Z_ik:
                        x[k, i, p, q, r] = model.addVar(vtype=GRB.BINARY, name=f"x_k{k}_i{i}_{p}_{q}_{r}")

    model.update()

    # --- 2: Função Objetivo ---
    model.setObjective(gp.quicksum(v[i] * x[k, i, p, q, r] for (k, i, p, q, r) in x), GRB.MAXIMIZE)

    # --- 3: Restrições de Não Sobreposição ---
    for k, (L_k, W_k, H_k) in enumerate(compartimentos):
        if k % 2 == 0:
            O_X_k = 0
        else:
            O_X_k = compartimentos[k-1][0] 
        O_Y_k = sum(compartimentos[c][1] for c in range(0, k-1, 2))
        
        E_L_k = gerar_coordenadas_normais(L_k, all_lengths)
        E_W_k = gerar_coordenadas_normais(W_k, all_widths)
        E_H_k = gerar_coordenadas_normais(H_k, all_heights)
        
        X_k = [x_ + O_X_k for x_ in E_L_k]
        Y_k = [y_ + O_Y_k for y_ in E_W_k] 
        Z_k = E_H_k
        
        vars_k = [(i, p, q, r) for (k_, i, p, q, r) in x if k_ == k]
        
        for s in X_k:
            for t in Y_k:
                for u in Z_k:
                    covering = []
                    for (i, p, q, r) in vars_k:
                        li, wi, hi, _ = boxes[i]
                        if (p <= s < p + li) and (q <= t < q + wi) and (r <= u < r + hi):
                            covering.append(x[k, i, p, q, r])
                    if covering:
                        model.addConstr(gp.quicksum(covering) <= 1, name=f"over_k{k}_{s}_{t}_{u}")

    # --- 4: Restrição de Inventário ---
    for i in range(m):
        total_placed_i = gp.quicksum(x[k, i, p, q, r] for (k, i_, p, q, r) in x if i_ == i)
        model.addConstr(total_placed_i <= boxes[i][3], name=f"inv_i{i}")

    # --- 5: Restrições Práticas (Estabilidade e Empilhamento) ---
    alpha, beta, gamma = 1.0, 1.0, 1.0
    for k, (L_k, W_k, H_k) in enumerate(compartimentos):
        if k % 2 == 0:
            O_X_k = 0
        else:
            O_X_k = compartimentos[k-1][0] 
        O_Y_k = sum(compartimentos[c][1] for c in range(0, k-1, 2))
        
        E_L_k = gerar_coordenadas_normais(L_k, all_lengths)
        E_W_k = gerar_coordenadas_normais(W_k, all_widths)
        E_H_k = gerar_coordenadas_normais(H_k, all_heights)
        X_k = [x_ + O_X_k for x_ in E_L_k]
        Y_k = [y_ + O_Y_k for y_ in E_W_k] 
        Z_k = E_H_k

        # 5.1. Estabilidade Vertical (Eixo Z)
        for i in range(m):
            li, wi, hi, _ = boxes[i]
            X_ik = [p for p in X_k if p + li <= O_X_k + L_k]
            Y_ik = [q for q in Y_k if q + wi <= O_Y_k + W_k]
            for p in X_ik:
                for q in Y_ik:
                    for r in [c for c in Z_k if c > 0 and c + hi <= H_k]:
                        if (k, i, p, q, r) not in x: continue
                        lhs = gp.LinExpr()
                        for j in range(m):
                            lj, wj, hj, _ = boxes[j]
                            r_linha = r - hj
                            if r_linha in Z_k:
                                rel_p = [pl for pl in X_k if (p - lj + 1 <= pl <= p + li - 1)]
                                rel_q = [ql for ql in Y_k if (q - wj + 1 <= ql <= q + wi - 1)]
                                for p_linha in rel_p:
                                    for q_linha in rel_q:
                                        if (k, j, p_linha, q_linha, r_linha) in x:
                                            L_ij = min(p + li, p_linha + lj) - max(p, p_linha)
                                            W_ij = min(q + wi, q_linha + wj) - max(q, q_linha)
                                            lhs += (L_ij * W_ij) * x[k, j, p_linha, q_linha, r_linha]
                        model.addConstr(lhs >= alpha * li * wi * x[k, i, p, q, r], name=f"EstZ_k{k}_i{i}_{p}_{q}_{r}")

        # 5.2. Estabilidade Horizontal X
        for i in range(m):
            li, wi, hi, _ = boxes[i]
            X_ik = [p for p in X_k if p + li <= O_X_k + L_k]
            Y_ik = [q for q in Y_k if q + wi <= O_Y_k + W_k]
            Z_ik = [r for r in Z_k if r + hi <= H_k]
            for q in Y_ik:
                for r in Z_ik:
                    # 'c > O_X_k' substitui o 'c > 0' (encostado na parede local do compartimento)
                    for p in [c for c in X_ik if c > O_X_k]: 
                        if (k, i, p, q, r) not in x: continue
                        lhs_x = gp.LinExpr()
                        for j in range(m):
                            lj, wj, hj, _ = boxes[j]
                            p_linha = p - lj
                            if p_linha in X_k:
                                rel_q = [ql for ql in Y_k if (q - wj + 1 <= ql <= q + wi - 1)]
                                rel_r = [rl for rl in Z_k if (r - hj + 1 <= rl <= r + hi - 1)]
                                for q_linha in rel_q:
                                    for r_linha in rel_r:
                                        if (k, j, p_linha, q_linha, r_linha) in x:
                                            W_ij = min(q + wi, q_linha + wj) - max(q, q_linha)
                                            H_ij = min(r + hi, r_linha + hj) - max(r, r_linha)
                                            lhs_x += (W_ij * H_ij) * x[k, j, p_linha, q_linha, r_linha]
                        model.addConstr(lhs_x >= beta * wi * hi * x[k, i, p, q, r], name=f"EstX_k{k}_i{i}_{p}_{q}_{r}")

        # 5.3. Estabilidade Horizontal Y
        for i in range(m):
            li, wi, hi, _ = boxes[i]
            X_ik = [p for p in X_k if p + li <= O_X_k + L_k]
            Y_ik = [q for q in Y_k if q + wi <= O_Y_k + W_k]
            Z_ik = [r for r in Z_k if r + hi <= H_k]
            for p in X_ik:
                for r in Z_ik:
                    # 'c > O_Y_k' substitui o 'c > 0'
                    for q in [c for c in Y_ik if c > O_Y_k]:
                        if (k, i, p, q, r) not in x: continue
                        lhs_y = gp.LinExpr()
                        for j in range(m):
                            lj, wj, hj, _ = boxes[j]
                            q_linha = q - wj
                            if q_linha in Y_k:
                                rel_p = [pl for pl in X_k if (p - lj + 1 <= pl <= p + li - 1)]
                                rel_r = [rl for rl in Z_k if (r - hj + 1 <= rl <= r + hi - 1)]
                                for p_linha in rel_p:
                                    for r_linha in rel_r:
                                        if (k, j, p_linha, q_linha, r_linha) in x:
                                            L_ij = min(p + li, p_linha + lj) - max(p, p_linha)
                                            H_ij = min(r + hi, r_linha + hj) - max(r, r_linha)
                                            lhs_y += (L_ij * H_ij) * x[k, j, p_linha, q_linha, r_linha]
                        model.addConstr(lhs_y >= gamma * li * hi * x[k, i, p, q, r], name=f"EstY_k{k}_i{i}_{p}_{q}_{r}")

        # 5.4. Loadbearing (Pressão / Resistência ao Empilhamento)
        for s in X_k:
            for t in Y_k:
                for u in Z_k:
                    lhs_pressao = gp.LinExpr()
                    rhs_resistencia = gp.LinExpr()
                    
                    for j in range(m):
                        lj, wj, hj, _ = boxes[j]
                        rel_p1 = [p for p in X_k if (s - lj + 1 <= p <= s) and (p + lj <= O_X_k + L_k)]
                        rel_q1 = [q for q in Y_k if (t - wj + 1 <= q <= t) and (q + wj <= O_Y_k + W_k)]
                        rel_r1 = [r for r in Z_k if (u + 1 <= r <= H_k - hj)]
                        for p1 in rel_p1:
                            for q1 in rel_q1:
                                for r1 in rel_r1:
                                    if (k, j, p1, q1, r1) in x:
                                        lhs_pressao += (peso[j] / (lj * wj)) * x[k, j, p1, q1, r1]
                                        
                    for i in range(m):
                        li, wi, hi, _ = boxes[i]
                        rel_p = [p for p in X_k if (s - li + 1 <= p <= s) and (p + li <= O_X_k + L_k)]
                        rel_q = [q for q in Y_k if (t - wi + 1 <= q <= t) and (q + wi <= O_Y_k + W_k)]
                        rel_r = [r for r in Z_k if (u - hi + 1 <= r <= u) and (r + hi <= H_k)]
                        for p in rel_p:
                            for q in rel_q:
                                for r in rel_r:
                                    if (k, i, p, q, r) in x:
                                        rhs_resistencia += sigma[i] * x[k, i, p, q, r]
                                        
                    if lhs_pressao.size() > 0 or rhs_resistencia.size() > 0:
                        model.addConstr(lhs_pressao <= rhs_resistencia, name=f"Empilhamento_k{k}_{s}_{t}_{u}")

    # --- 6: Resolver ---
    model.Params.TimeLimit = 3600
    model.optimize()

    # --- 7. Output ---
    tipo_dict = {}
    tipo_counter = 1
    for li, wi, hi, bi in boxes:
        dims = (li, wi, hi)
        if dims not in tipo_dict:
            tipo_dict[dims] = tipo_counter
            tipo_counter += 1

    with open(arquivo_saida, "w") as f:
        f.write(f"{num_compartimentos}\n")
        for (L_c, W_c, H_c) in compartimentos:
            f.write(f"{L_c} {W_c} {H_c}\n")
        if hasattr(model, 'SolCount') and model.SolCount > 0:
            for (k, i, p, q, r) in x:
                if x[k, i, p, q, r].X > 0.5:
                    li, wi, hi, bi = boxes[i]
                    tipo = tipo_dict[(li, wi, hi)]
                    cliente = 1
                    f.write(f"{p} {q} {r} {li} {wi} {hi} {tipo} {cliente} {k}\n")
    
    resumo_arquivo = arquivo_saida.replace(".txt", "_resumo.txt")
    with open(resumo_arquivo, "w") as f:
        f.write(f"Status da solucao: {model.Status}\n")
        if model.SolCount > 0:
            num_caixas = sum(1 for (k,i,p,q,r) in x if x[k,i,p,q,r].X > 0.5)
            k_len = len(compartimentos)
            total_capacity = sum(compartimentos[c][0] * compartimentos[c][1] * compartimentos[c][2] for c in range(k_len))
            volume_packed = model.ObjVal * total_capacity
            ocupacao_global = (volume_packed / total_capacity) * 100

            f.write(f"Objetivo final (Soma v_i): {model.ObjVal:.6f}\n")
            f.write(f"Volume total carregado: {volume_packed:.2f}\n")
            f.write(f"Capacidade Total ({num_compartimentos} compartimentos): {total_capacity}\n")
            f.write(f"Ocupação Global: {ocupacao_global:.2f}%\n")
            f.write(f"Número total de caixas: {num_caixas}\n")
            f.write(f"Gap: {model.MIPGap*100:.6f}%\n")
            f.write(f"Tempo: {model.Runtime:.6f} s\n")
            
            f.write("\n--- Detalhes por Compartimento ---\n")
            for k in range(num_compartimentos):
                vol_k = sum(boxes[i][0]*boxes[i][1]*boxes[i][2] for (k_,i,p,q,r) in x 
                           if k_==k and x[k_,i,p,q,r].X > 0.5)
                (L, W, H) = compartimentos[k]
                f.write(f"Compartimento {k}: {vol_k:.2f} vol ({vol_k/(L*W*H)*100:.1f}%)\n")
        else:
            f.write("Nenhuma solução viável encontrada.\n")