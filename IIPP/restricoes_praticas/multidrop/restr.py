import gurobipy as gp

'''
    alpha = 1.0 # fator de estabilidade
    for i in range(m):
        for k in range(n):
            li, wi, hi = boxes[i] # para cada cliente k precisamos entregar b_ik caixas do tipo i
        
            X_i = [c for c in X_coords if c <= L - li]
            Y_i = [c for c in Y_coords if c <= W - wi]
            Z_i = [c for c in Z_coords if c <= H - hi]
            
            for p in X_i:
                for q in Y_i:
                    for r in [c for c in Z_i if c > 0]: # restrição aplicada para qualquer caixa acima do solo
                        lhs = gp.LinExpr()
                        
                        for j in range(m):
                            for k_ in range(k + 1):
                                lj, wj, hj = boxes[j]
                                X_j = [c for c in X_coords if c <= L - lj]
                                Y_j = [c for c in Y_coords if c <= W - wj]
                                Z_j = [c for c in Z_coords if c <= H - hj]
                                
                                r_linha = r - hj # a caixa j deve estar exatamente abaixo da caixa i; a caixa i está sendo apoiada
                                if r_linha in Z_j:
                                    relevant_p_linha = [p_linha for p_linha in X_j if (p - lj + 1 <= p_linha <= p + li - 1)] # a caixa de cima deve terminar depois da caixa de baixo começar E começar antes da caixa de baixo terminar
                                    relevant_q_linha = [q_linha for q_linha in Y_j if (q - wj + 1 <= q_linha <= q + wi - 1)] #
                                    
                                    for p_linha in relevant_p_linha:
                                        for q_linha in relevant_q_linha:
                                            L_ij = min(p + li, p_linha + lj) - max(p, p_linha)
                                            W_ij = min(q + wi, q_linha + wj) - max(q, q_linha)
                                            
                                            # Acúmulo da área suportada ponderada pela variável de decisão
                                            lhs += (L_ij * W_ij) * x[j, k_, p_linha, q_linha, r_linha]
                                        
                        model.addConstr(lhs >= alpha * li * wi * x[i,k, p, q, r], 
                                    name=f"EstabilidadeZ_{i}_,{k}_{p}_{q}_{r}")
'''
def addStabZ(model, boxes, L, W, H, m, n, X_coords, Y_coords, Z_coords, x, alpha=1.0):
    for i in range(m):
        for k in range(n):
            li, wi, hi = boxes[i] # para cada cliente k precisamos entregar b_ik caixas do tipo i
        
            X_i = [c for c in X_coords if c <= L - li]
            Y_i = [c for c in Y_coords if c <= W - wi]
            Z_i = [c for c in Z_coords if c <= H - hi]
            
            for p in X_i:
                for q in Y_i:
                    for r in [c for c in Z_i if c > 0]: # restrição aplicada para qualquer caixa acima do solo
                        lhs = gp.LinExpr()
                        
                        for j in range(m):
                            for k_ in range(k + 1):
                                lj, wj, hj = boxes[j]
                                X_j = [c for c in X_coords if c <= L - lj]
                                Y_j = [c for c in Y_coords if c <= W - wj]
                                Z_j = [c for c in Z_coords if c <= H - hj]
                                
                                r_linha = r - hj # a caixa j deve estar exatamente abaixo da caixa i; a caixa i está sendo apoiada
                                if r_linha in Z_j:
                                    relevant_p_linha = [p_linha for p_linha in X_j if (p - lj + 1 <= p_linha <= p + li - 1)] # a caixa de cima deve terminar depois da caixa de baixo começar E começar antes da caixa de baixo terminar
                                    relevant_q_linha = [q_linha for q_linha in Y_j if (q - wj + 1 <= q_linha <= q + wi - 1)] #
                                    
                                    for p_linha in relevant_p_linha:
                                        for q_linha in relevant_q_linha:
                                            L_ij = min(p + li, p_linha + lj) - max(p, p_linha)
                                            W_ij = min(q + wi, q_linha + wj) - max(q, q_linha)
                                            
                                            # Acúmulo da área suportada ponderada pela variável de decisão
                                            lhs += (L_ij * W_ij) * x[j, k_, p_linha, q_linha, r_linha]
                                        
                        model.addConstr(lhs >= alpha * li * wi * x[i,k, p, q, r], 
                                    name=f"EstabilidadeZ_{i}_,{k}_{p}_{q}_{r}")


'''                   
    # Restrição de estabilidade X
    beta = 1.0 # fator de estabilidade
    for i in range(m):
        for k in range(n):
            li, wi, hi = boxes[i] # para cada cliente k precisamos entregar b_ik caixas do tipo i
        
            X_i = [c for c in X_coords if c <= L - li]
            Y_i = [c for c in Y_coords if c <= W - wi]
            Z_i = [c for c in Z_coords if c <= H - hi]
            
            for q in Y_i:
                for r in Z_i:
                    for p in [c for c in X_i if c > 0]: # restrição aplicada para qualquer caixa acima do solo
                        lhs = gp.LinExpr()
                        
                        for j in range(m):
                            for k_ in range(k + 1):
                                lj, wj, hj = boxes[j]
                                X_j = [c for c in X_coords if c <= L - lj]
                                Y_j = [c for c in Y_coords if c <= W - wj]
                                Z_j = [c for c in Z_coords if c <= H - hj]
                                
                                p_linha = p - lj # a caixa j deve estar exatamente abaixo da caixa i; a caixa i está sendo apoiada
                                if p_linha in X_j:
                                    relevant_q_linha = [q_linha for q_linha in Y_j if (q - wj + 1 <= q_linha <= q + wi - 1)]
                                    relevant_r_linha = [r_linha for r_linha in Z_j if (r - hj + 1 <= r_linha <= r + hi - 1)]
                                    
                                    for q_linha in relevant_q_linha:
                                        for r_linha in relevant_r_linha:
                                            W_ij = min(q + wi, q_linha + wj) - max(q, q_linha)
                                            H_ij = min(r + hi, r_linha + hj) - max(r, r_linha)
                                            lhs += (W_ij * H_ij) * x[j, k_, p_linha, q_linha, r_linha]
                                        
                        model.addConstr(lhs >= beta * wi * hi * x[i,k, p, q, r], 
                                    name=f"EstabilidadeX_{i}_,{k}_{p}_{q}_{r}")
''' 
def addStabX(model, boxes, L, W, H, m, n, X_coords, Y_coords, Z_coords, x, beta=1.0):
    for i in range(m):
        for k in range(n):
            li, wi, hi = boxes[i] # para cada cliente k precisamos entregar b_ik caixas do tipo i
        
            X_i = [c for c in X_coords if c <= L - li]
            Y_i = [c for c in Y_coords if c <= W - wi]
            Z_i = [c for c in Z_coords if c <= H - hi]
            
            for q in Y_i:
                for r in Z_i:
                    for p in [c for c in X_i if c > 0]: # restrição aplicada para qualquer caixa acima do solo
                        lhs = gp.LinExpr()
                        
                        for j in range(m):
                            for k_ in range(k + 1):
                                lj, wj, hj = boxes[j]
                                X_j = [c for c in X_coords if c <= L - lj]
                                Y_j = [c for c in Y_coords if c <= W - wj]
                                Z_j = [c for c in Z_coords if c <= H - hj]
                                
                                p_linha = p - lj # a caixa j deve estar exatamente abaixo da caixa i; a caixa i está sendo apoiada
                                if p_linha in X_j:
                                    relevant_q_linha = [q_linha for q_linha in Y_j if (q - wj + 1 <= q_linha <= q + wi - 1)]
                                    relevant_r_linha = [r_linha for r_linha in Z_j if (r - hj + 1 <= r_linha <= r + hi - 1)]
                                    
                                    for q_linha in relevant_q_linha:
                                        for r_linha in relevant_r_linha:
                                            W_ij = min(q + wi, q_linha + wj) - max(q, q_linha)
                                            H_ij = min(r + hi, r_linha + hj) - max(r, r_linha)
                                            lhs += (W_ij * H_ij) * x[j, k_, p_linha, q_linha, r_linha]
                                        
                        model.addConstr(lhs >= beta * wi * hi * x[i,k, p, q, r], 
                                    name=f"EstabilidadeX_{i}_,{k}_{p}_{q}_{r}")
                        

'''                    
    # Restrição de estabilidade Y
    gamma = 1.0 # fator de estabilidade
    for i in range(m):
        for k in range(n):
            li, wi, hi = boxes[i] # para cada cliente k precisamos entregar b_ik caixas do tipo i
        
            X_i = [c for c in X_coords if c <= L - li]
            Y_i = [c for c in Y_coords if c <= W - wi]
            Z_i = [c for c in Z_coords if c <= H - hi]
            
            for p in X_i:
                for r in Z_i:
                    for q in [c for c in Y_i if c > 0]:
                        lhs = gp.LinExpr()
                        
                        for j in range(m):
                            for k_ in range(k + 1):
                                lj, wj, hj = boxes[j]
                                X_j = [c for c in X_coords if c <= L - lj]
                                Y_j = [c for c in Y_coords if c <= W - wj]
                                Z_j = [c for c in Z_coords if c <= H - hj]
                                
                                q_linha = q - wj
                                if q_linha in Y_j:
                                    relevant_p_linha = [p_linha for p_linha in X_j if (p - lj + 1 <= p_linha <= p + li - 1)]
                                    relevant_r_linha = [r_linha for r_linha in Z_j if (r - hj + 1 <= r_linha <= r + hi - 1)]
                                    for p_linha in relevant_p_linha:
                                        for r_linha in relevant_r_linha:
                                            L_ij = min(p + li, p_linha + lj) - max(p, p_linha)
                                            H_ij = min(r + hi, r_linha + hj) - max(r, r_linha)
                                            lhs += (L_ij * H_ij) * x[j, k_, p_linha, q_linha, r_linha]
                                        
                        model.addConstr(lhs >= gamma * li * hi * x[i,k, p, q, r], 
                                    name=f"EstabilidadeY_{i}_,{k}_{p}_{q}_{r}")
                                    '''
def addStabY(model, boxes, L, W, H, m, n, X_coords, Y_coords, Z_coords, x, gamma=1.0):
    for i in range(m):
        for k in range(n):
            li, wi, hi = boxes[i] # para cada cliente k precisamos entregar b_ik caixas do tipo i
        
            X_i = [c for c in X_coords if c <= L - li]
            Y_i = [c for c in Y_coords if c <= W - wi]
            Z_i = [c for c in Z_coords if c <= H - hi]
            
            for p in X_i:
                for r in Z_i:
                    for q in [c for c in Y_i if c > 0]:
                        lhs = gp.LinExpr()
                        
                        for j in range(m):
                            for k_ in range(k + 1):
                                lj, wj, hj = boxes[j]
                                X_j = [c for c in X_coords if c <= L - lj]
                                Y_j = [c for c in Y_coords if c <= W - wj]
                                Z_j = [c for c in Z_coords if c <= H - hj]
                                
                                q_linha = q - wj
                                if q_linha in Y_j:
                                    relevant_p_linha = [p_linha for p_linha in X_j if (p - lj + 1 <= p_linha <= p + li - 1)]
                                    relevant_r_linha = [r_linha for r_linha in Z_j if (r - hj + 1 <= r_linha <= r + hi - 1)]
                                    for p_linha in relevant_p_linha:
                                        for r_linha in relevant_r_linha:
                                            L_ij = min(p + li, p_linha + lj) - max(p, p_linha)
                                            H_ij = min(r + hi, r_linha + hj) - max(r, r_linha)
                                            lhs += (L_ij * H_ij) * x[j, k_, p_linha, q_linha, r_linha]
                                        
                        model.addConstr(lhs >= gamma * li * hi * x[i,k, p, q, r], 
                                    name=f"EstabilidadeY_{i}_,{k}_{p}_{q}_{r}")

    '''    
    # Restrição loadbearing
    for s in X_coords:
        for t in Y_coords:
            for u in Z_coords:
                lhs_pressao = gp.LinExpr()
                rhs_resistencia = gp.LinExpr()
                
                # lado esquerdo: soma das pressões
                for k in range(n):
                    for j in range(m):
                        lj, wj, hj = boxes[j]
                        
                        relevant_p1 = [p for p in X_coords if (s - lj + 1 <= p <= s) and (p <= L - lj)]
                        relevant_q1 = [q for q in Y_coords if (t - wj + 1 <= q <= t) and (q <= W - wj)]
                        relevant_r1 = [r for r in Z_coords if (u + 1 <= r <= H - hj)]
                        
                        for p1 in relevant_p1:
                            for q1 in relevant_q1:
                                for r1 in relevant_r1:
                                    lhs_pressao += (peso[j] / (lj * wj)) * x[j, k, p1, q1, r1]
                
                for k in range(n):
                    for i in range(m):
                        li, wi, hi = boxes[i]
                        
                        relevant_p = [p for p in X_coords if (s - li + 1 <= p <= s) and (p <= L - li)]
                        relevant_q = [q for q in Y_coords if (t - wi + 1 <= q <= t) and (q <= W - wi)]
                        relevant_r = [r for r in Z_coords if (u - hi + 1 <= r <= u) and (r <= H - hi)]
                        
                        for p in relevant_p:
                            for q in relevant_q:
                                for r in relevant_r:
                                    rhs_resistencia += sigma[i] * x[i, k, p, q, r]
                
                # Adiciona restrição apenas se houver caixas possíveis naquela coordenada
                if lhs_pressao.size() > 0 or rhs_resistencia.size() > 0:
                    model.addConstr(lhs_pressao <= rhs_resistencia, name=f"Empilhamento_{s}_{t}_{u}")
                    '''                     
def addLoadbearing(model, boxes, L, W, H, m, n, X_coords, Y_coords, Z_coords, x, peso, sigma):
    # Restrição loadbearing
    for s in X_coords:
        for t in Y_coords:
            for u in Z_coords:
                lhs_pressao = gp.LinExpr()
                rhs_resistencia = gp.LinExpr()
                
                # lado esquerdo: soma das pressões
                for k in range(n):
                    for j in range(m):
                        lj, wj, hj = boxes[j]
                        
                        relevant_p1 = [p for p in X_coords if (s - lj + 1 <= p <= s) and (p <= L - lj)]
                        relevant_q1 = [q for q in Y_coords if (t - wj + 1 <= q <= t) and (q <= W - wj)]
                        relevant_r1 = [r for r in Z_coords if (u + 1 <= r <= H - hj)]
                        
                        for p1 in relevant_p1:
                            for q1 in relevant_q1:
                                for r1 in relevant_r1:
                                    lhs_pressao += (peso[j] / (lj * wj)) * x[j, k, p1, q1, r1]
                
                for k in range(n):
                    for i in range(m):
                        li, wi, hi = boxes[i]
                        
                        relevant_p = [p for p in X_coords if (s - li + 1 <= p <= s) and (p <= L - li)]
                        relevant_q = [q for q in Y_coords if (t - wi + 1 <= q <= t) and (q <= W - wi)]
                        relevant_r = [r for r in Z_coords if (u - hi + 1 <= r <= u) and (r <= H - hi)]
                        
                        for p in relevant_p:
                            for q in relevant_q:
                                for r in relevant_r:
                                    rhs_resistencia += sigma[i] * x[i, k, p, q, r]
                
                # Adiciona restrição apenas se houver caixas possíveis naquela coordenada
                if lhs_pressao.size() > 0 or rhs_resistencia.size() > 0:
                    model.addConstr(lhs_pressao <= rhs_resistencia, name=f"Empilhamento_{s}_{t}_{u}")