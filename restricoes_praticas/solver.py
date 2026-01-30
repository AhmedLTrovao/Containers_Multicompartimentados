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

def resolver_instancia(L, W, H, boxes, arquivo_saida, sigma, peso,tempo_limite=3600):
    m = len(boxes)
    v = [(l*w*h)/(L*W*H) for (l,w,h,b) in boxes]
    all_lengths = {l for (l,_,_,_) in boxes}
    all_widths  = {w for (_,w,_,_) in boxes}
    all_heights = {h for (_,_,h,_) in boxes}

    X_coords = gerar_coordenadas_normais(L, all_lengths)
    Y_coords = gerar_coordenadas_normais(W, all_widths)
    Z_coords = gerar_coordenadas_normais(H, all_heights)

    model = gp.Model("GridBasedPosition")
    x = {}
    for i in range(m):
        li, wi, hi, bi = boxes[i]
        for p in [c for c in X_coords if c <= L - li]:
            for q in [c for c in Y_coords if c <= W - wi]:
                for r in [c for c in Z_coords if c <= H - hi]:
                    x[i,p,q,r] = model.addVar(vtype=GRB.BINARY, name=f"x_{i}_{p}_{q}_{r}")

    model.update()
    model.setObjective(gp.quicksum(v[i]*x[i,p,q,r] for (i,p,q,r) in x), GRB.MAXIMIZE)


    # Restrição de não sobreposição
    for xp in X_coords:
        for yq in Y_coords:
            for zr in Z_coords:
                covering = [x[i,p,q,r] for (i,p,q,r) in x if (p <= xp <  p + boxes[i][0]) and (q <= yq < q+boxes[i][1]) and (r <= zr < r+boxes[i][2])]
                if covering:
                    model.addConstr(gp.quicksum(covering) <= 1)
                    

    # Restrição de disponibilidade (boxes[i][3] é a quantidade máxima de caixas disponíveis para o tipo i)
    for i in range(m):
        model.addConstr(gp.quicksum(x[i,p,q,r] for (i_,p,q,r) in x if i_==i) <= boxes[i][3])
        
         
    # Restrição de estabilidade vertical
    alpha = 1.0 # fator de estabilidade
    for j in range(m):
        lj, wj, hj, bj = boxes[j]
        
        X_j = [c for c in X_coords if c <= L - lj]
        Y_j = [c for c in Y_coords if c <= W - wj]
        Z_j = [c for c in Z_coords if c <= H - hj]
        
        for p_linha in X_j:
            for q_linha in Y_j:
                for r_linha in [r for r in Z_j if r > 0]: # restrição aplicada para qualquer caixa acima do solo
                    lhs = gp.LinExpr()
                    
                    for i in range(m):
                        li, wi, hi, bi = boxes[i]
                        X_i = [c for c in X_coords if c <= L - li]
                        Y_i = [c for c in Y_coords if c <= W - wi]
                        Z_i = [c for c in Z_coords if c <= H - hi]
                        
                        r = r_linha - hi # a caixa i deve estar exatamente abaixo da caixa j
                        if r in Z_i:
                            relevant_p = [p for p in X_i if (p_linha - li + 1 <= p <= p_linha + lj - 1)]
                            relevant_q = [q for q in Y_i if (q_linha - wi + 1 <= q <= q_linha + wj - 1)]
                            
                            for p in relevant_p:
                                for q in relevant_q:
                                    # Cálculo das dimensões da área de contato (L_ij2 e W_ij2) [1]
                                    L_ij = min(p + li, p_linha + lj) - max(p, p_linha)
                                    W_ij = min(q + wi, q_linha + wj) - max(q, q_linha)
                                    
                                    # Acúmulo da área suportada ponderada pela variável de decisão
                                    lhs += (L_ij * W_ij) * x[i, p, q, r]
                                    
                    model.addConstr(lhs >= alpha * lj * wj * x[j, p_linha, q_linha, r_linha], 
                                name=f"EstabilidadeZ_{j}_{p_linha}_{q_linha}_{r_linha}")
                            
             
                       
    # Restrição de estabilidade horizontal no eixo X
    beta = 1.0
    for j in range(m):
        lj, wj, hj, bj = boxes[j]
        
        X_j = [c for c in X_coords if c <= L - lj]
        Y_j = [c for c in Y_coords if c <= W - wj]
        Z_j = [c for c in Z_coords if c <= H - hj]
        for q_linha in Y_j:
            for r_linha in Z_j:
                for p_linha in [p for p in X_j if p > 0]: # estável - encostado na parede do contêiner
                    lhs_x = gp.LinExpr()
                    
                    for i in range(m):
                        li, wi, hi, bi = boxes[i]
                        X_i = [c for c in X_coords if c <= L - li]
                        Y_i = [c for c in Y_coords if c <= W - wi]
                        Z_i = [c for c in Z_coords if c <= H - hi]
                        
                        p = p_linha - li
                        
                        if p in X_i:
                            relevant_q = [q for q in Y_i if (q_linha - wi + 1 <= q <= q_linha + wj - 1)]
                            relevant_r = [r for r in Z_i if (r_linha - hi + 1 <= r <= r_linha + hj - 1)]
                            for q in relevant_q:
                                for r in relevant_r:
                                    W_ij = min(q + wi, q_linha + wj) - max(q, q_linha)
                                    H_ij = min(r + hi, r_linha + hj) - max(r, r_linha)
                                    lhs_x += (W_ij * H_ij) * x[i, p, q, r]
                    model.addConstr(lhs_x >= beta * wi * hj * x[j, p_linha, q_linha, r_linha])
                            
                    
    # Restrição de estabilidade horizontal no eixo Y
    gamma = 1.0
    for j in range(m):
        lj, wj, hj, bj = boxes[j]
        
        X_j = [c for c in X_coords if c <= L - lj]
        Y_j = [c for c in Y_coords if c <= W - wj]
        Z_j = [c for c in Z_coords if c <= H - hj]
        for p_linha in X_j:
            for r_linha in Z_j:
                for q_linha in [q for q in Y_j if q > 0]:
                    lhs_y = gp.LinExpr()
                    
                    for i in range(m):
                        li, wi, hi, bi = boxes[i]
                        X_i = [c for c in X_coords if c <= L - li]
                        Y_i = [c for c in Y_coords if c <= W - wi]
                        Z_i = [c for c in Z_coords if c <= H - hi]
                        
                        q = q_linha - wi
                        if q in Y_i:
                            relevant_p = [p for p in X_i if (p_linha - li + 1 <= p <= p_linha + lj - 1)]
                            relevant_r = [r for r in Z_i if (r_linha - hi + 1 <= r <= r_linha + hj - 1)]
                            for p in relevant_p:
                                for r in relevant_r:
                                    L_ij = min(p + li, p_linha + lj) - max(p, p_linha)
                                    H_ij = min(r + hi, r_linha + hj) - max(r, r_linha)
                                    lhs_y += (L_ij * H_ij) * x[i, p, q, r]
                    model.addConstr(lhs_y >= gamma * lj * hj * x[j, p_linha, q_linha, r_linha])             
            
    # Restrição loadbearing
    for s in X_coords:
        for t in Y_coords:
            for u in Z_coords:
                lhs_pressao = gp.LinExpr()
                rhs_resistencia = gp.LinExpr()
                
                # lado esquerdo: soma das pressões
                for j in range(m):
                    lj, wj, hj, bj = boxes[j]
                    
                    relevant_p1 = [p for p in X_coords if (s - lj + 1 <= p <= s) and (p <= L - lj)]
                    relevant_q1 = [q for q in Y_coords if (t - wj + 1 <= q <= t) and (q <= W - wj)]
                    relevant_r1 = [r for r in Z_coords if (u + 1 <= r <= H - hj)]
                    
                    for p1 in relevant_p1:
                        for q1 in relevant_q1:
                            for r1 in relevant_r1:
                                lhs_pressao += (peso[j] / (lj * wj)) * x[j, p1, q1, r1]
                
                # lado direito: resistência da caixa i que ocupa a posição (s,t,u)
                for i in range(m):
                    li, wi, hi, bi = boxes[i]
                    
                    relevant_p = [p for p in X_coords if (s - li + 1 <= p <= s) and (p <= L - li)]
                    relevant_q = [q for q in Y_coords if (t - wi + 1 <= q <= t) and (q <= W - wi)]
                    relevant_r = [r for r in Z_coords if (u - hi + 1 <= r <= u) and (r <= H - hi)]
                    
                    for p in relevant_p:
                        for q in relevant_q:
                            for r in relevant_r:
                                rhs_resistencia += sigma[i] * x[i, p, q, r]
                
                # Adiciona restrição apenas se houver caixas possíveis naquela coordenada
                if lhs_pressao.size() > 0 or rhs_resistencia.size() > 0:
                    model.addConstr(lhs_pressao <= rhs_resistencia, name=f"Empilhamento_{s}_{t}_{u}")

    model.Params.LogFile = arquivo_saida.replace(".txt", "_log.txt")
    model.Params.TimeLimit = tempo_limite

    model.optimize()

    tipo_dict = {}
    tipo_counter = 1
    for li,wi,hi,bi in boxes:
        dims = (li,wi,hi)
        if dims not in tipo_dict:
            tipo_dict[dims] = tipo_counter
            tipo_counter += 1

    with open(arquivo_saida, "w") as f:
        f.write(f"{L} {W} {H}\n")
        for (i,p,q,r) in x:
            if x[i,p,q,r].X > 0.5:
                li,wi,hi,bi = boxes[i]
                tipo = tipo_dict[(li,wi,hi)]
                cliente = 1
                f.write(f"{p} {q} {r} {li} {wi} {hi} {tipo} {cliente}\n")

    resumo_arquivo = arquivo_saida.replace(".txt", "_resumo.txt")
    with open(resumo_arquivo, "w") as f:
        f.write(f"Status da solução: {model.Status}\n")
        if model.SolCount > 0:
            f.write(f"Objetivo final: {model.ObjVal:.6f}\n")
            f.write(f"Gap de otimalidade: {model.MIPGap*100:.6f}%\n")
            f.write(f"Tempo de execução: {model.Runtime:.6f} segundos\n")
            f.write(f"Número de nós explorados: {model.NodeCount}\n")
        else:
            f.write("Nenhuma solução viável encontrada.\n")