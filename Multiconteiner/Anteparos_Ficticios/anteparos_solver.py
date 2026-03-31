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
    Solver Inteligente para Caminhões Multicompartimentados.
    - Calcula o tamanho do container baseado em canais únicos de divisórias.
    - Estica as paredes transversais para selar as baias laterais.
    """
    
    # 1. Identificar Canais Únicos de Divisórias (Evita crescimento duplicado)
    canais_X = set() # Onde existem paredes transversais (|)
    canais_Y = set() # Onde existem paredes longitudinais (-)
    
    for w in walls_list:
        if w['l'] < w['w']: # Transversal
            canais_X.add(w['x'])
        elif w['w'] < w['l']: # Longitudinal
            # Aqui usamos o Y original do .dat para identificar o corredor
            canais_Y.add(w['y'])
    
    # Cada canal único adiciona 1 unidade de espessura
    extra_L = len(canais_X)
    extra_W = len(canais_Y)
    
    L_total = L_orig + extra_L
    W_total = W_orig + extra_W

    # 2. Unificar objetos e AJUSTAR DIMENSÕES das paredes (Auto-Stretch)
    all_objs = list(boxes)
    primeiro_idx_parede = len(all_objs)
    
    for w in walls_list:
        # SE FOR TRANSVERSAL (|): Estica para tocar as duas laterais do caminhão
        if w['l'] < w['w']:
            nova_parede = (w['l'], W_total, w['h'], w['b'])
            px, py = w['x'], 0 # Começa na quina lateral
        else:
            # SE FOR LONGITUDINAL (-): Mantém o comprimento definido
            nova_parede = (w['l'], w['w'], w['h'], w['b'])
            px, py = w['x'], w['y']
            
        all_objs.append(nova_parede)
        w['x_fix'], w['y_fix'] = px, py

    # 3. Gerar Grade de Coordenadas
    all_l = {b[0] for b in all_objs}
    all_w = {b[1] for b in all_objs}
    all_h = {b[2] for b in all_objs}
    
    X_coords = gerar_coordenadas_normais(L_total, all_l)
    Y_coords = gerar_coordenadas_normais(W_total, all_w)
    Z_coords = gerar_coordenadas_normais(H, all_h)
    
    # Garantir que os pontos das paredes existam na grade
    for w in walls_list:
        if w['x_fix'] not in X_coords: X_coords.append(w['x_fix'])
        if w['y_fix'] not in Y_coords: Y_coords.append(w['y_fix'])
    X_coords.sort(); Y_coords.sort()

    # 4. Inicializar Modelo Gurobi
    model = gp.Model("Caminhao_Multicompartimentado")
    model.Params.OutputFlag = 1
    model.Params.TimeLimit = 120 # Limite de 2 minutos para testes

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

    # 6. Objetivo: Maximizar volume das CAIXAS (Paredes têm peso zero no objetivo)
    vol_container = L_total * W_total * H
    model.setObjective(
        gp.quicksum(((all_objs[i][0]*all_objs[i][1]*all_objs[i][2])/vol_container)*x_var[i,p,q,r]
                    for (i,p,q,r) in x_var if i < primeiro_idx_parede),
        GRB.MAXIMIZE
    )

    # 7. Restrição de Não Sobreposição (Overlap)
    for xp in X_coords:
        for yq in Y_coords:
            for zr in Z_coords:
                covering = [x_var[i,p,q,r] for (i,p,q,r) in x_var 
                            if (p <= xp < p + all_objs[i][0] and 
                                q <= yq < q + all_objs[i][1] and 
                                r <= zr < r + all_objs[i][2])]
                if covering:
                    model.addConstr(gp.quicksum(covering) <= 1)

    # 8. Restrição de Quantidade
    for i in range(len(all_objs)):
        model.addConstr(gp.quicksum(x_var[idx,p,q,r] for (idx,p,q,r) in x_var if idx==i) <= all_objs[i][3])

    # 9. Fixação Obrigatória das Paredes
    for idx, w in enumerate(walls_list):
        p_idx = primeiro_idx_parede + idx
        px, py = w['x_fix'], w['y_fix']
        # Procura a variável correspondente à posição fixa da parede
        key = (p_idx, px, py, 0)
        if key in x_var:
            model.addConstr(x_var[key] == 1)
        else:
            print(f"ERRO CRÍTICO: Posição da parede {idx} ({px},{py}) é inválida para a grade.")
            return

    # 10. Otimizar
    model.optimize()

    # 11. Salvar Resultados para o MATLAB
    if model.Status in [GRB.OPTIMAL, GRB.TIME_LIMIT] and model.SolCount > 0:
        with open(arquivo_saida, "w") as f:
            # Cabeçalho com dimensões atualizadas
            f.write(f"{L_total} {W_total} {H}\n")
            for (i,p,q,r) in x_var:
                if x_var[i,p,q,r].X > 0.5:
                    li, wi, hi, _ = all_objs[i]
                    tipo = 1 if i >= primeiro_idx_parede else 0
                    f.write(f"{p} {q} {r} {li} {wi} {hi} {tipo}\n")
        print(f"Instância resolvida! Ocupação útil: {model.ObjVal*100:.2f}%")
    else:
        print("Não foi possível encontrar uma solução viável.")