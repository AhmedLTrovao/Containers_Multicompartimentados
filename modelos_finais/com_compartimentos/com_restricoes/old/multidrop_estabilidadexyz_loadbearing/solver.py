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

def resolver_instancia(compartimentos, clientes, arquivo_saida, tempo_limite=3600, stabv=True, stabh=False, loadbearing=False):
    model = gp.Model("MultiCompartment_Lateral_Multidrop")
    
    # 1. Extração de Tipos Únicos e Parâmetros
    tipos_caixas = []
    mapa_tipos = {}
    demanda = {}      # demanda[c][i] = qtd
    deltas = {}       # deltas[c][i] = delta_x
    
    idx_tipo = 0
    for cl in clientes:
        c = cl["id_cliente"]
        demanda[c] = {}
        deltas[c] = {}
        for item in cl["itens"]:
            dims = item["dims"]
            peso = item["peso"]
            sigma = item["sigma"]
            
            # Assinatura única para reutilizar variáveis de caixas idênticas
            assinatura = (dims, peso, sigma)
            if assinatura not in mapa_tipos:
                mapa_tipos[assinatura] = idx_tipo
                tipos_caixas.append({
                    "id": idx_tipo, "dims": dims, "peso": peso, "sigma": sigma
                })
                idx_tipo += 1
            
            i = mapa_tipos[assinatura]
            demanda[c][i] = demanda[c].get(i, 0) + item["qtd"]
            deltas[c][i] = item["delta_x"]
            
    print(demanda)
    num_clientes = len(clientes)
    num_compartimentos = len(compartimentos)
    
    X_coords_comp = {}
    Y_coords_comp = {}
    Z_coords_comp = {}
    
    x = {} # x[k, c, i, p, q, r]
    
    # 2. Criação de Variáveis com Offsets Globais
    O_X = {}
    O_Y = {}
    
    # Recalculando o Big-M para suportar coordenadas globais
    # Deve ser pelo menos o tamanho máximo possível no eixo X
    M = sum(comp[0] for comp in compartimentos) 

    for k, (L_k, W_k, H_k) in enumerate(compartimentos):
        # A sua lógica de offset
        if k % 2 == 0:
            O_X[k] = 0
        else:
            O_X[k] = compartimentos[k-1][0]
            
        O_Y[k] = sum(compartimentos[c][1] for c in range(0, k-1, 2))
        
        all_lengths = {cx["dims"][0] for cx in tipos_caixas}
        all_widths  = {cx["dims"][1] for cx in tipos_caixas}
        all_heights = {cx["dims"][2] for cx in tipos_caixas}
        
        E_L_k = gerar_coordenadas_normais(L_k, all_lengths)
        E_W_k = gerar_coordenadas_normais(W_k, all_widths)
        E_H_k = gerar_coordenadas_normais(H_k, all_heights)
        
        # Aplicando o offset global
        X_coords_comp[k] = [x + O_X[k] for x in E_L_k]
        Y_coords_comp[k] = [y + O_Y[k] for y in E_W_k]
        Z_coords_comp[k] = E_H_k
        
        for c in range(num_clientes):
            for i in demanda[c].keys():
                li, wi, hi = tipos_caixas[i]["dims"]
                
                # Filtragem ajustada para o espaço global
                X_ki = [p for p in X_coords_comp[k] if p <= O_X[k] + L_k - li]
                Y_ki = [q for q in Y_coords_comp[k] if q <= O_Y[k] + W_k - wi]
                Z_ki = [r for r in Z_coords_comp[k] if r <= H_k - hi]
                
                for p in X_ki:
                    for q in Y_ki:
                        for r in Z_ki:
                            x[k, c, i, p, q, r] = model.addVar(vtype=GRB.BINARY, name=f"x_k{k}_c{c}_i{i}_{p}_{q}_{r}")

    # Variáveis de limite lateral (Multidrop no eixo X)
    L_vars = {}
    for k in range(num_compartimentos):
        for c in range(num_clientes):
            L_vars[k, c] = model.addVar(vtype=GRB.CONTINUOUS, name=f"L_{k}_{c}")

    model.update()

    # 3. Função Objetivo: Maximizar volume global ocupado
    obj_expr = gp.quicksum(
        (tipos_caixas[i]["dims"][0] * tipos_caixas[i]["dims"][1] * tipos_caixas[i]["dims"][2]) * x[k, c, i, p, q, r]
        for (k, c, i, p, q, r) in x
    )
    model.setObjective(obj_expr, GRB.MAXIMIZE)

    # 4. Restrições Fundamentais
    for k, (L_k, W_k, H_k) in enumerate(compartimentos):
        # 4.1. Não sobreposição (Isolada por compartimento)
        
        for xp in X_coords_comp[k]:
            for yq in Y_coords_comp[k]:
                for zr in Z_coords_comp[k]:
                    covering = [
                        x[k_, c, i, p, q, r] for (k_, c, i, p, q, r) in x 
                        if k_ == k and 
                           (p <= xp < p + tipos_caixas[i]["dims"][0]) and 
                           (q <= yq < q + tipos_caixas[i]["dims"][1]) and 
                           (r <= zr < r + tipos_caixas[i]["dims"][2])
                    ]
                    if covering:
                        model.addConstr(gp.quicksum(covering) <= 1)

    # 4.2. Demanda: A soma de alocações (em qualquer compartimento) não deve exceder o pedido
    for c in range(num_clientes):
        for i in demanda[c].keys():
            demand_vars = [x[k, c_, i_, p, q, r] for (k, c_, i_, p, q, r) in x if c_ == c and i_ == i]
            if demand_vars:
                model.addConstr(gp.quicksum(demand_vars) <= demanda[c][i], name=f"Demanda_c{c}_i{i}")

    # 5. Restrições de Multidrop Lateral (Eixo X)
    for k, (L_k, W_k, H_k) in enumerate(compartimentos):
        is_even = (k % 2 == 0)
        
        for c in range(num_clientes):
            model.addConstr(L_vars[k, c] >= O_X[k])
            model.addConstr(L_vars[k, c] <= O_X[k] + L_k)
            
            # Ordenação dos limites no compartimento
            if c > 0:
                if is_even: # Acesso pela Esquerda (origem em 0)
                    model.addConstr(L_vars[k, c-1] <= L_vars[k, c])
                else:       # Acesso pela Direita (origem em L_k)
                    model.addConstr(L_vars[k, c-1] >= L_vars[k, c])
            
            # Aplicação dos limites em relação às caixas
            for i in demanda[c].keys():
                li = tipos_caixas[i]["dims"][0]
                delta_val = deltas[c][i]
                
                vars_caixa = [(p, q, r) for (k_, c_, i_, p, q, r) in x if k_ == k and c_ == c and i_ == i]
                
                for (p, q, r) in vars_caixa:
                    var_x = x[k, c, i, p, q, r]
                    if is_even:
                        # Cliente c não avança além de L_vars
                        model.addConstr((p + li) * var_x <= L_vars[k, c])
                        # Cliente c deve estar atrás do limite de c-1 (permitindo delta)
                        if c > 0:
                            model.addConstr(L_vars[k, c-1] - delta_val <= p * var_x + M * (1 - var_x))
                    else:
                        # Cliente c não começa à esquerda de L_vars
                        model.addConstr(L_vars[k, c] <= p * var_x + M * (1 - var_x))
                        # Cliente c termina antes do limite esquerdo de c-1 (permitindo delta)
                        if c > 0:
                            model.addConstr((p + li) * var_x <= L_vars[k, c-1] + delta_val + M * (1 - var_x))
    if stabv:
        alpha = 1.0 # Fator de estabilidade vertical
        print("Gerando restrições de Estabilidade Vertical (Z)...")
        for (k, c, i, p, q, r), var in x.items():
            if r == 0: 
                continue # Apoiada no chão do caminhão
                
            li, wi, hi = tipos_caixas[i]["dims"]
            lhs_z = gp.LinExpr()
            
            # Procura caixas de qualquer cliente (c_) que estejam no mesmo compartimento (k) 
            # e exatamente abaixo (r_ == r - hj)
            for (k_, c_, j, p_, q_, r_), var_ in x.items():
                if k_ == k:
                    lj, wj, hj = tipos_caixas[j]["dims"]
                    if r_ == r - hj:
                        # Intersecção das bases
                        L_ij = max(0, min(p + li, p_ + lj) - max(p, p_))
                        W_ij = max(0, min(q + wi, q_ + wj) - max(q, q_))
                        
                        if L_ij > 0 and W_ij > 0:
                            lhs_z += (L_ij * W_ij) * var_
                            
            model.addConstr(lhs_z >= alpha * li * wi * var, name=f"StabZ_k{k}_c{c}_i{i}_{p}_{q}_{r}")

    if stabh:
        beta = 1.0  # Fator de estabilidade horizontal (X)
        gamma = 1.0 # Fator de estabilidade horizontal (Y)
        print("Gerando restrições de Estabilidade Horizontal (X e Y)...")
        
        for (k, c, i, p, q, r), var in x.items():
            li, wi, hi = tipos_caixas[i]["dims"]
            
            # --- Estabilidade X ---
            # Só exige apoio se não estiver encostada na parede esquerda do seu compartimento
            if p > O_X[k]:
                lhs_x = gp.LinExpr()
                for (k_, c_, j, p_, q_, r_), var_ in x.items():
                    if k_ == k:
                        lj, wj, hj = tipos_caixas[j]["dims"]
                        if p_ == p - lj: # Caixa j está exatamente à esquerda
                            W_ij = max(0, min(q + wi, q_ + wj) - max(q, q_))
                            H_ij = max(0, min(r + hi, r_ + hj) - max(r, r_))
                            if W_ij > 0 and H_ij > 0:
                                lhs_x += (W_ij * H_ij) * var_
                model.addConstr(lhs_x >= beta * wi * hi * var, name=f"StabX_k{k}_c{c}_i{i}_{p}_{q}_{r}")
                
            # --- Estabilidade Y ---
            # Só exige apoio se não estiver encostada na parede frontal do seu compartimento
            if q > O_Y[k]:
                lhs_y = gp.LinExpr()
                for (k_, c_, j, p_, q_, r_), var_ in x.items():
                    if k_ == k:
                        lj, wj, hj = tipos_caixas[j]["dims"]
                        if q_ == q - wj: # Caixa j está exatamente à frente
                            L_ij = max(0, min(p + li, p_ + lj) - max(p, p_))
                            H_ij = max(0, min(r + hi, r_ + hj) - max(r, r_))
                            if L_ij > 0 and H_ij > 0:
                                lhs_y += (L_ij * H_ij) * var_
                model.addConstr(lhs_y >= gamma * li * hi * var, name=f"StabY_k{k}_c{c}_i{i}_{p}_{q}_{r}")

    if loadbearing:
        print("Gerando restrições de Loadbearing (Resistência ao Esmagamento)...")
        for k in range(num_compartimentos):
            # Para evitar varrer o caminhão inteiro, limitamos a busca aos voxels deste compartimento
            for s in X_coords_comp[k]:
                for t in Y_coords_comp[k]:
                    for u in Z_coords_comp[k]:
                        lhs_pressao = gp.LinExpr()
                        rhs_resistencia = gp.LinExpr()
                        
                        # Filtramos apenas as variáveis que pertencem a este compartimento
                        vars_k = [(key, var) for key, var in x.items() if key[0] == k]
                        
                        for (k_, c, j, p, q, r), var in vars_k:
                            lj, wj, hj = tipos_caixas[j]["dims"]
                            peso_j = tipos_caixas[j]["peso"]
                            sigma_j = tipos_caixas[j]["sigma"]
                            
                            # Se a caixa cobre as coordenadas X e Y do voxel (s, t)
                            if p <= s < p + lj and q <= t < q + wj:
                                # Pressão: a caixa está acima do voxel u
                                if r > u:
                                    lhs_pressao += (peso_j / (lj * wj)) * var
                                # Resistência: a caixa ocupa o voxel u
                                if r <= u < r + hj:
                                    rhs_resistencia += sigma_j * var
                                    
                        if lhs_pressao.size() > 0 or rhs_resistencia.size() > 0:
                            model.addConstr(lhs_pressao <= rhs_resistencia, name=f"Load_k{k}_{s}_{t}_{u}")

    model.Params.LogFile = arquivo_saida.replace(".txt", "_log.txt")
    model.Params.TimeLimit = tempo_limite
    model.optimize()

    # 6. Escrita do Arquivo com Coordenadas Globais
    with open(arquivo_saida, "w") as f:
        f.write(f"{num_compartimentos}\n")
        for (L_c, W_c, H_c) in compartimentos:
            f.write(f"{L_c} {W_c} {H_c}\n")
        
        for (k, c, i, p, q, r) in x:
            if x[k, c, i, p, q, r].X > 0.5:
                li, wi, hi = tipos_caixas[i]["dims"]
                f.write(f"{p} {q} {r} {li} {wi} {hi} {i} {c} {k}\n")
    

    resumo_arquivo = arquivo_saida.replace(".txt", "_resumo.txt")
    volume_total = sum([l*w*h for (l,w,h) in compartimentos])
    with open(resumo_arquivo, "w") as f:
        f.write(f"Status da solução: {model.Status}\n")
        if model.SolCount > 0:
            f.write(f"Objetivo final : {model.ObjVal/volume_total:.6f}\n")
            f.write(f"Gap de otimalidade: {model.MIPGap*100:.6f}%\n")
            f.write(f"Tempo de execução: {model.Runtime:.6f} segundos\n")
            f.write(f"Número de nós explorados: {model.NodeCount}\n")
        else:
            f.write("Nenhuma solução viável encontrada.\n")