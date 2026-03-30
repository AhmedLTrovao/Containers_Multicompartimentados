import gurobipy as gp
from gurobipy import GRB

def gerar_coordenadas_normais(dimensao_maxima, dimensoes_objetos):
    """Gera pontos de grade baseados nas dimensões das caixas."""
    coordenadas = {0}
    if not dimensoes_objetos: return [0]
    for d in sorted(list(dimensoes_objetos)):
        novas = set()
        for c in coordenadas:
            novo = c + d
            while novo <= dimensao_maxima:
                novas.add(novo)
                novo += d
        coordenadas.update(novas)
    menor_dim = min(dimensoes_objetos)
    coords_finais = [c for c in coordenadas if c <= dimensao_maxima - menor_dim]
    if 0 not in coords_finais: coords_finais.insert(0, 0)
    return sorted(coords_finais)

def resolver_instancia(L_orig, W_orig, H, boxes, walls_list, arquivo_saida):
    """
    Solver Otimizado para Caminhões com Divisórias (Acessos Laterais).
    - Ajusta o container dinamicamente.
    - Estica as paredes transversais para não deixar buracos.
    """
    
    # 1. Ajuste Dinâmico do Container (Lógica de Máximo, não Soma)
    # Se houver várias paredes longitudinais em Y=5, o W só cresce a espessura de UMA.
    extra_L = max([w['l'] for w in walls_list if w['l'] < w['w']], default=0)
    extra_W = max([w['w'] for w in walls_list if w['w'] < w['l']], default=0)
    
    L_total = L_orig + extra_L
    W_total = W_orig + extra_W

    # 2. Unificar objetos e AJUSTAR DIMENSÕES das paredes
    all_objs = list(boxes)
    primeiro_idx_parede = len(all_objs)
    
    for w in walls_list:
        # Se for Transversal (|): Forçamos a largura (W) a ser o W_total do caminhão
        if w['l'] < w['w']:
            nova_parede = (w['l'], W_total, w['h'], w['b'])
            px, py = w['x'], 0 # Força a começar encostada na lateral Y=0
        else:
            # Se for Longitudinal (-): Mantém as dimensões do .dat
            nova_parede = (w['l'], w['w'], w['h'], w['b'])
            px, py = w['x'], w['y']
            
        all_objs.append(nova_parede)
        # Atualizamos os valores de x e y para a fixação posterior
        w['x_fix'], w['y_fix'] = px, py

    # 3. Gerar Grade de Coordenadas
    all_l = {b[0] for b in all_objs}
    all_w = {b[1] for b in all_objs}
    all_h = {b[2] for b in all_objs}
    
    X_coords = gerar_coordenadas_normais(L_total, all_l)
    Y_coords = gerar_coordenadas_normais(W_total, all_w)
    Z_coords = gerar_coordenadas_normais(H, all_h)
    
    # Forçar as posições das paredes na grade
    for w in walls_list:
        if w['x_fix'] not in X_coords: X_coords.append(w['x_fix'])
        if w['y_fix'] not in Y_coords: Y_coords.append(w['y_fix'])
    X_coords.sort(); Y_coords.sort()

    # 4. Inicializar Modelo
    model = gp.Model("Caminhao_Acesso_Lateral")
    model.Params.OutputFlag = 1
    model.Params.TimeLimit = 3600

    # 5. Variáveis de Decisão
    x_var = {}
    for i, (li, wi, hi, bi) in enumerate(all_objs):
        valid_p = [p for p in X_coords if p <= L_total - li]
        valid_q = [q for q in Y_coords if q <= W_total - wi]
        valid_r = [r for r in Z_coords if r <= H - hi]
        for p in valid_p:
            for q in valid_q:
                for r in valid_r:
                    x_var[i, p, q, r] = model.addVar(vtype=GRB.BINARY)

    # 6. Objetivo: Maximizar ocupação das caixas (ignora volume das paredes)
    vol_util = L_total * W_total * H
    model.setObjective(
        gp.quicksum(((all_objs[i][0]*all_objs[i][1]*all_objs[i][2])/vol_util)*x_var[i,p,q,r]
                    for (i,p,q,r) in x_var if i < primeiro_idx_parede),
        GRB.MAXIMIZE
    )

    # 7. Restrição: Não Sobreposição (Overlap)
    for xp in X_coords:
        for yq in Y_coords:
            for zr in Z_coords:
                covering = [x_var[i,p,q,r] for (i,p,q,r) in x_var 
                            if (p <= xp < p + all_objs[i][0] and 
                                q <= yq < q + all_objs[i][1] and 
                                r <= zr < r + all_objs[i][2])]
                if covering:
                    model.addConstr(gp.quicksum(covering) <= 1)

    # 8. Restrição: Quantidade de Caixas
    for i in range(len(all_objs)):
        model.addConstr(gp.quicksum(x_var[idx,p,q,r] for (idx,p,q,r) in x_var if idx==i) <= all_objs[i][3])

    # 9. FIXAR TODAS AS PAREDES
    for idx, w in enumerate(walls_list):
        p_idx = primeiro_idx_parede + idx
        px, py = w['x_fix'], w['y_fix']
        if (p_idx, px, py, 0) in x_var:
            model.addConstr(x_var[p_idx, px, py, 0] == 1)
        else:
            print(f"ERRO: Parede {idx} fora da grade em ({px},{py})")
            return

    # 10. Otimizar
    model.optimize()

    # 11. Exportar Resultados
    if model.Status in [GRB.OPTIMAL, GRB.TIME_LIMIT] and model.SolCount > 0:
        with open(arquivo_saida, "w") as f:
            f.write(f"{L_total} {W_total} {H}\n")
            for (i,p,q,r) in x_var:
                if x_var[i,p,q,r].X > 0.5:
                    li, wi, hi, _ = all_objs[i]
                    tipo = 1 if i >= primeiro_idx_parede else 0
                    f.write(f"{p} {q} {r} {li} {wi} {hi} {tipo}\n")
        print(f"Sucesso! Ocupação: {model.ObjVal*100:.2f}%")
    else:
        print("Solução não encontrada.")