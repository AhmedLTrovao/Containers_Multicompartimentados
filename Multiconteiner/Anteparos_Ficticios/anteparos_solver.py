import gurobipy as gp
from gurobipy import GRB

def gerar_coordenadas_normais(dimensao_maxima, dimensoes_objetos):
    """
    Gera pontos de grade baseados nas combinações lineares das dimensões das caixas.
    Isso reduz drasticamente o número de variáveis se comparado a uma grade unitária.
    """
    coordenadas = {0}
    for d in sorted(list(dimensoes_objetos)):
        novas = set()
        for c in coordenadas:
            novo = c + d
            while novo <= dimensao_maxima:
                novas.add(novo)
                novo += d
        coordenadas.update(novas)
    
    if not dimensoes_objetos:
        return [0]
        
    menor_dim = min(dimensoes_objetos)
    # Filtra apenas coordenadas onde cabe pelo menos a menor caixa
    coords_finais = [c for c in coordenadas if c <= dimensao_maxima - menor_dim]
    if 0 not in coords_finais:
        coords_finais.insert(0, 0)
    return sorted(coords_finais)

def resolver_instancia(L_orig, W, H, boxes, wall, arquivo_saida):
    """
    L_orig: Comprimento original
    boxes: lista de (l, w, h, b)
    wall: dicionário {'l': espessura, 'w': largura, 'h': altura, 'b': qtd, 'x': pos_x, 'y': pos_y}
    """
    
    # 1. Ajuste do Container: compensamos a espessura da parede no comprimento total
    # Se a parede tem espessura 1, o container de 100 vira 101 para não perder espaço útil.
    L_total = L_orig + wall['l']
    
    # 2. Unificar objetos: Caixas Reais + Objeto Parede
    # Mantemos as caixas reais primeiro para facilitar a função objetivo
    all_objs = list(boxes)
    wall_idx = len(all_objs)
    all_objs.append((wall['l'], wall['w'], wall['h'], wall['b']))

    # 3. Gerar Grade de Coordenadas
    all_l = {b[0] for b in all_objs}
    all_w = {b[1] for b in all_objs}
    all_h = {b[2] for b in all_objs}
    
    X_coords = gerar_coordenadas_normais(L_total, all_l)
    Y_coords = gerar_coordenadas_normais(W, all_w)
    Z_coords = gerar_coordenadas_normais(H, all_h)
    
    # Garantir que as coordenadas específicas da parede existam na grade
    if wall['x'] not in X_coords: X_coords.append(wall['x'])
    if wall['y'] not in Y_coords: Y_coords.append(wall['y'])
    X_coords.sort()
    Y_coords.sort()

    # 4. Inicializar Modelo
    model = gp.Model("Container_Multicompartimentado")
    model.Params.OutputFlag = 1  # 0 para silenciar, 1 para ver o log do Gurobi
    model.Params.TimeLimit = 3600 # Limite de 1 hora

    # 5. Variáveis de Decisão
    # x[i, p, q, r] = 1 se o objeto i começa na posição (p, q, r)
    x = {}
    for i in range(len(all_objs)):
        li, wi, hi, bi = all_objs[i]
        
        # Filtro de coordenadas válidas para o tamanho de cada objeto
        valid_p = [p for p in X_coords if p <= L_total - li]
        valid_q = [q for q in Y_coords if q <= W - wi]
        valid_r = [r for r in Z_coords if r <= H - hi]
        
        for p in valid_p:
            for q in valid_q:
                for r in valid_r:
                    x[i, p, q, r] = model.addVar(vtype=GRB.BINARY, name=f"obj_{i}_{p}_{q}_{r}")

    # 6. Função Objetivo
    # Maximizar o volume ocupado APENAS pelas caixas reais (ignorando o volume da parede)
    vol_container = L_total * W * H
    model.setObjective(
        gp.quicksum(((all_objs[i][0] * all_objs[i][1] * all_objs[i][2]) / vol_container) * x[i, p, q, r]
                    for (i, p, q, r) in x if i < wall_idx),
        GRB.MAXIMIZE
    )

    # 7. Restrição: Não Sobreposição (Overlap)
    # Para cada ponto da grade, no máximo um objeto pode ocupá-lo
    print("Gerando restrições de não sobreposição...")
    for xp in X_coords:
        for yq in Y_coords:
            for zr in Z_coords:
                covering = []
                for (i, p, q, r) in x:
                    li, wi, hi, _ = all_objs[i]
                    if (p <= xp < p + li and 
                        q <= yq < q + wi and 
                        r <= zr < r + hi):
                        covering.append(x[i, p, q, r])
                
                if covering:
                    model.addConstr(gp.quicksum(covering) <= 1, name=f"overlap_{xp}_{yq}_{zr}")

    # 8. Restrição: Quantidade de Objetos
    for i in range(len(all_objs)):
        model.addConstr(
            gp.quicksum(x[i, p, q, r] for (i_idx, p, q, r) in x if i_idx == i) <= all_objs[i][3],
            name=f"qty_{i}"
        )

    # 9. FIXAR A PAREDE NA POSIÇÃO ESPECIFICADA
    # Forçamos a variável da parede a ser 1 na coordenada (x, y, 0)
    # b=1 na instância garante que apenas uma será fixada
    pos_wall_x = wall['x']
    pos_wall_y = wall['y']
    
    if (wall_idx, pos_wall_x, pos_wall_y, 0) in x:
        model.addConstr(x[wall_idx, pos_wall_x, pos_wall_y, 0] == 1, name="fix_wall")
    else:
        # Fallback de segurança caso a discretização falhe em gerar o ponto exato
        print(f"ERRO CRÍTICO: Posição da parede ({pos_wall_x}, {pos_wall_y}) incompatível com a grade.")
        return

    # 10. Otimização
    model.optimize()

    # 11. Salvar Resultados
    if model.Status in [GRB.OPTIMAL, GRB.TIME_LIMIT] and model.SolCount > 0:
        with open(arquivo_saida, "w") as f:
            # Header com dimensões ajustadas
            f.write(f"{L_total} {W} {H}\n")
            
            for (i, p, q, r) in x:
                if x[i, p, q, r].X > 0.5:
                    li, wi, hi, _ = all_objs[i]
                    # 0 para caixa, 1 para parede
                    tipo_saida = 1 if i == wall_idx else 0
                    # Formato: x y z l w h tipo
                    f.write(f"{p} {q} {r} {li} {wi} {hi} {tipo_saida}\n")
        arquivo_resumo = arquivo_saida.replace(".txt", "_resumo.txt")
        with open(arquivo_resumo, "w", encoding="utf-8") as f:
            f.write(f"Status da solução: {model.Status}\n")
            f.write(f"Objetivo final: {model.ObjVal}\n")
            
            # Volume total considerando o container com a parede
            vol_container = L_total * W * H
            f.write(f"Volume total carregado: {model.ObjVal * vol_container}\n")
            
            # Conta apenas as caixas reais que foram colocadas (ignora a parede)
            # wall_idx é o índice que definimos para a parede no solver
            num_caixas = sum(1 for (i, p, q, r) in x if x[i, p, q, r].X > 0.5 and i < wall_idx)
            f.write(f"Número total de caixas carregadas: {num_caixas}\n")
            
            f.write(f"Gap de otimalidade: {model.MIPGap * 100}%\n")
            f.write(f"Tempo de execução: {model.Runtime}\n")
            f.write(f"Número de nós explorados: {model.NodeCount}\n")
        
        print(f"Resumo salvo em: {arquivo_resumo}")
        
        print(f"Instância resolvida. Ocupação: {model.ObjVal*100:.2f}%")
    else:
        print("Nenhuma solução encontrada.")
    
    