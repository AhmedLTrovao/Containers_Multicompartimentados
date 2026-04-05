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

def resolver_multi_compartimento(compartimentos, boxes, arquivo_saida):
    """
    Resolve o problema de empacotamento para múltiplos compartimentos distintos,
    aplicando a lógica de offset (O_k) baseada nos conjuntos X_ik, Y_ik, Z_ik.
    """
    m = len(boxes)
    num_compartimentos = len(compartimentos)
    total_capacity = sum(L * W * H for (L, W, H) in compartimentos)
    v = [(l*w*h)/total_capacity for (l,w,h,b) in boxes]
    
    all_lengths = {l for (l,_,_,_) in boxes}
    all_widths  = {w for (_,w,_,_) in boxes}
    all_heights = {h for (_,_,h,_) in boxes}

    model = gp.Model("MultiContainerGrid_Flexivel")

    # --- 1: Variáveis de Decisão ---
    x = {}
    for k, (L_k, W_k, H_k) in enumerate(compartimentos):
        O_k = sum(compartimentos[c][1] for c in range(k))
        
        E_L_k = gerar_coordenadas_normais(L_k, all_lengths)
        E_W_k = gerar_coordenadas_normais(W_k, all_widths)
        E_H_k = gerar_coordenadas_normais(H_k, all_heights)
        
        X_k = E_L_k
        Y_k = [y + O_k for y in E_W_k]
        Z_k = E_H_k
        
        for i in range(m):
            li, wi, hi, bi = boxes[i]
            
            X_ik = [p for p in X_k if p + li <= L_k]
            Y_ik = [q for q in Y_k if q + wi <= O_k + W_k] 
            Z_ik = [r for r in Z_k if r + hi <= H_k]
            
            for p in X_ik:
                for q in Y_ik:
                    for r in Z_ik:
                        x[k, i, p, q, r] = model.addVar(vtype=GRB.BINARY, name=f"x_k{k}_i{i}_{p}_{q}_{r}")

    model.update()

    # --- 2: Função Objetivo ---
    model.setObjective(gp.quicksum(v[i] * x[k, i, p, q, r] for (k, i, p, q, r) in x), GRB.MAXIMIZE)

    # --- 3: Restrições de Não Sobreposição ---
    print("A gerar restrições de não sobreposição...")
    for k, (L_k, W_k, H_k) in enumerate(compartimentos):
        O_k = sum(compartimentos[c][1] for c in range(k))
        E_L_k = gerar_coordenadas_normais(L_k, all_lengths)
        E_W_k = gerar_coordenadas_normais(W_k, all_widths)
        E_H_k = gerar_coordenadas_normais(H_k, all_heights)
        
        X_k = E_L_k
        Y_k = [y + O_k for y in E_W_k]
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

    # --- 5: Resolver ---
    model.Params.TimeLimit = 3600
    #vmodel.Params.MIPFocus = 1 
    model.optimize()

    # --- 6. Output ---
    tipo_dict = {}
    tipo_counter = 1
    for li, wi, hi, bi in boxes:
        dims = (li, wi, hi)
        if dims not in tipo_dict:
            tipo_dict[dims] = tipo_counter
            tipo_counter += 1

    with open(arquivo_saida, "w") as f:
        # 1. Escreve o número total de compartimentos
        f.write(f"{num_compartimentos}\n")
        # 2. Escreve as dimensões exatas (L, W, H) de CADA compartimento
        for (L_c, W_c, H_c) in compartimentos:
            f.write(f"{L_c} {W_c} {H_c}\n")
        # 3. Escreve as caixas (apenas se o Gurobi encontrou uma solução)
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
            
            k = len(compartimentos)
            total_capacity = sum(compartimentos[c][0] * compartimentos[c][1] * compartimentos[c][2] for c in range(k))
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