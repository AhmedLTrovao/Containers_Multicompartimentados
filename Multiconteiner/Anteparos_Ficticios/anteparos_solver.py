import gurobipy as gp
from gurobipy import GRB

def gerar_coordenadas_inteligentes(dimensao_maxima, dimensoes_caixas, pontos_especificos=None):
    """
    Gera Normal Patterns (coordenadas úteis) e inclui pontos das paredes.
    """
    coordenadas = {0}
    if pontos_especificos:
        coordenadas.update(pontos_especificos)
        
    for d in sorted(list(dimensoes_caixas)):
        novas = set()
        for c in coordenadas:
            novo = c + d
            while novo <= dimensao_maxima:
                novas.add(novo)
                novo += d
        coordenadas.update(novas)
    
    return sorted([c for c in coordenadas if c <= dimensao_maxima])

def resolver_instancia(L, W, H, boxes, walls_list, arquivo_saida):
    """
    Solver Híbrido: Coordenadas Normais + Filtro de Anteparos.
    """
    model = gp.Model("Solver_Hibrido_Eficiente")
    model.Params.TimeLimit = 300  # 5 minutos
    
    # 1. Coletar dimensões para as coordenadas normais
    all_l = {b[0] for b in boxes}
    all_w = {b[1] for b in boxes}
    all_h = {b[2] for b in boxes}
    
    # Pontos de quebra das paredes (onde as caixas podem começar)
    wall_x = {w['x'] for w in walls_list if w['l'] == 0}
    wall_y = {w['y'] for w in walls_list if w['w'] == 0}
    
    # 2. Gerar Grade Otimizada
    X_coords = gerar_coordenadas_inteligentes(L, all_l, wall_x)
    Y_coords = gerar_coordenadas_inteligentes(W, all_w, wall_y)
    Z_coords = gerar_coordenadas_inteligentes(H, all_h)

    # 3. Criar Variáveis com Duplo Filtro (Geométrico + Anteparo)
    x_var = {}
    print(f"Grade reduzida: X({len(X_coords)}), Y({len(Y_coords)}), Z({len(Z_coords)})")
    
    for i, (li, wi, hi, qtd_max) in enumerate(boxes):
        # Filtro 1: A caixa cabe no espaço restante da grade?
        valid_p = [p for p in X_coords if p + li <= L]
        valid_q = [q for q in Y_coords if q + wi <= W]
        valid_r = [r for r in Z_coords if r + hi <= H]
        
        for p in valid_p:
            for q in valid_q:
                for r in valid_r:
                    # Filtro 2: A caixa atravessa alguma parede?
                    atravessa = False
                    for w in walls_list:
                        if w['l'] == 0: # Parede fixa em X
                            if p < w['x'] < p + li:
                                atravessa = True; break
                        elif w['w'] == 0: # Parede fixa em Y
                            if q < w['y'] < q + wi:
                                atravessa = True; break
                    
                    if not atravessa:
                        x_var[i, p, q, r] = model.addVar(vtype=GRB.BINARY, name=f"x_{i}_{p}_{q}_{r}")

    model.update()

    # 4. Função Objetivo: Maximizar ocupação volumétrica
    vol_container = L * W * H
    obj = gp.quicksum(((boxes[i][0] * boxes[i][1] * boxes[i][2]) / vol_container) * x_var[i, p, q, r]
                       for (i, p, q, r) in x_var)
    model.setObjective(obj, GRB.MAXIMIZE)

    # 5. Restrição de Não Sobreposição (Apenas nos pontos da grade inteligente)
    # Para garantir cobertura total, usamos os pontos onde as caixas REALMENTE ocupam espaço
    print("Adicionando restrições de sobreposição...")
    for s in X_coords:
        if s == L: continue
        for t in Y_coords:
            if t == W: continue
            for u in Z_coords:
                if u == H: continue
                
                # Seleciona caixas que cobrem o voxel (s, t, u)
                covering = [x_var[i, p, q, r] for (i, p, q, r) in x_var
                            if (p <= s < p + boxes[i][0] and 
                                q <= t < q + boxes[i][1] and 
                                r <= u < r + boxes[i][2])]
                
                if covering:
                    model.addConstr(gp.quicksum(covering) <= 1)

    # 6. Restrição de Inventário
    for i in range(len(boxes)):
        model.addConstr(gp.quicksum(x_var[chave] for chave in x_var if chave[0] == i) <= boxes[i][3])

    # 7. Otimização
    model.optimize()

    # 8. Exportação e Geração de Resumo
    if model.SolCount > 0:
        # Gera o arquivo para o MATLAB (coordenadas)
        with open(arquivo_saida, "w") as f:
            f.write(f"{L} {W} {H}\n")
            for (i, p, q, r), var in x_var.items():
                if var.X > 0.5:
                    li, wi, hi, _ = boxes[i]
                    f.write(f"{p} {q} {r} {li} {wi} {hi} 0\n")
            for w in walls_list:
                lx = 0.1 if w['l'] == 0 else w['l']
                wy = 0.1 if w['w'] == 0 else w['w']
                f.write(f"{w['x']} {w['y']} 0 {lx} {wy} {H} 1\n")
        
        #  GERAÇÃO DO RESUMO PARA O COMPILADOR 
        arquivo_resumo = arquivo_saida.replace(".txt", "_resumo.txt")
        vol_total_carregado = sum(boxes[i][0] * boxes[i][1] * boxes[i][2] 
                                  for (i, p, q, r), var in x_var.items() if var.X > 0.5)
        n_caixas = sum(1 for var in x_var.values() if var.X > 0.5)
        
        with open(arquivo_resumo, "w", encoding="utf-8") as f:
            f.write(f"Status da solução: {model.Status}\n")
            f.write(f"Objetivo final : {model.ObjVal}\n")
            f.write(f"Volume total carregado: {vol_total_carregado}\n")
            f.write(f"Número total de caixas carregadas: {n_caixas}\n")
            f.write(f"Gap de otimalidade: {model.MIPGap * 100}%\n")
            f.write(f"Tempo de execução: {model.Runtime}\n")
            f.write(f"Número de nós explorados: {model.NodeCount}\n")
        
        print(f"Sucesso! Resultado em {arquivo_saida} e resumo em {arquivo_resumo}")
    else:
        print("Nenhuma solução encontrada.")