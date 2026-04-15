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

def resolver_multi_compartimento(L, W, H, boxes, num_compartimentos, arquivo_saida):
    """
    Resolve o problema de empacotamento para múltiplos compartimentos idênticos,
    aplicando a lógica de offset (O_k) baseada nos conjuntos X_ik, Y_ik, Z_ik.
    """
    m = len(boxes)

    total_capacity = num_compartimentos*L*W*H
    v = [(l*w*h)/total_capacity for (l,w,h,b) in boxes]
    
    all_lengths = {l for (l,_,_,_) in boxes}
    all_widths  = {w for (_,w,_,_) in boxes}
    all_heights = {h for (_,_,h,_) in boxes}

    # Gera os padrões normais base
    E_L = gerar_coordenadas_normais(L, all_lengths)
    E_W = gerar_coordenadas_normais(W, all_widths)
    E_H = gerar_coordenadas_normais(H, all_heights)

    model = gp.Model("MulticompartimentoGrid_Formal")

    # --- 1: Variáveis de Decisão
    x = {}

    for k in range(num_compartimentos):
        # Deslocamento do compartimento k ao longo do eixo Y (O_k)
        # Se os compartimentos tivessem tamanhos diferentes, somaríamos os W_c anteriores
        O_k = k * W 
        
        # Conjuntos de pontos discretos para o compartimento k (X_k, Y_k, Z_k)
        X_k = E_L
        Y_k = [y + O_k for y in E_W]
        Z_k = E_H
        
        for i in range(m):
            li, wi, hi, bi = boxes[i]
            
            # Conjuntos filtrados (X_ik, Y_ik, Z_ik) - Exatamente como na modelagem!
            X_ik = [p for p in X_k if p + li <= L]
            Y_ik = [q for q in Y_k if q + wi <= O_k + W] # Impede vazar pro próximo
            Z_ik = [r for r in Z_k if r + hi <= H]
            
            for p in X_ik:
                for q in Y_ik:
                    for r in Z_ik:
                        x[k, i, p, q, r] = model.addVar(
                            vtype=GRB.BINARY, 
                            name=f"x_k{k}_i{i}_{p}_{q}_{r}"
                        )

    model.update()

    # --- 2: Função Objetivo
    model.setObjective(
        gp.quicksum(v[i] * x[k, i, p, q, r] for (k, i, p, q, r) in x), 
        GRB.MAXIMIZE
    )

    # --- 3: Restrições de Não Sobreposição
    print("Gerando restricoes de nao sobreposicao...")
    for k in range(num_compartimentos):
        O_k = k * W
        X_k = E_L
        Y_k = [y + O_k for y in E_W]
        Z_k = E_H
        
        # Filtra previamente as variáveis do compartimento 'k' para otimizar os loops
        vars_k = [(i, p, q, r) for (k_, i, p, q, r) in x if k_ == k]
        
        # varrendo todos s, t, u nos conjuntos globais do compartimento k
        for s in X_k:
            for t in Y_k:
                for u in Z_k:
                    covering = []
                    
                    for (i, p, q, r) in vars_k:
                        li, wi, hi, _ = boxes[i]
                        # A condição p <= s < p+li garante o voxel ocupado
                        if (p <= s < p + li) and (q <= t < q + wi) and (r <= u < r + hi):
                            covering.append(x[k, i, p, q, r])
                    
                    if covering:
                        model.addConstr(gp.quicksum(covering) <= 1, name=f"no_overlap_k{k}_{s}_{t}_{u}")

    # --- 4: Restrição de Inventário (Quantidade de caixas)
    for i in range(m):
        total_placed_i = gp.quicksum(x[k, i, p, q, r] for (k, i_, p, q, r) in x if i_ == i)
        model.addConstr(total_placed_i <= boxes[i][3], name=f"inventario_i{i}")

    # --- 5: Resolver
    model.Params.TimeLimit = 3600
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
        # A nova dimensão do Y global impressa no cabeçalho
        f.write(f"{L} {W * num_compartimentos} {H} {num_compartimentos}\n")
        
        for (k, i, p, q, r) in x:
            if x[k, i, p, q, r].X > 0.5:
                li, wi, hi, bi = boxes[i]
                tipo = tipo_dict[(li, wi, hi)]
                cliente = 1
                f.write(f"{p} {q} {r} {li} {wi} {hi} {tipo} {cliente} {k}\n")

    # Resumo
    resumo_arquivo = arquivo_saida.replace(".txt", "_resumo.txt")
    with open(resumo_arquivo, "w") as f:
        f.write(f"Status da solução: {model.Status}\n")
        if model.SolCount > 0:
            num_caixas = sum(1 for (k,i,p,q,r) in x if x[k,i,p,q,r].X > 0.5)
            total_capacity = (L * W * H) * num_compartimentos
            volume_packed = model.ObjVal * (L * W * H) * num_compartimentos
            
            ocupacao_global = (volume_packed / total_capacity) * 100

            f.write(f"Objetivo final (Soma v_i): {model.ObjVal:.6f}\n")
            f.write(f"Volume total carregado: {volume_packed:.2f}\n")
            f.write(f"Capacidade Total ({num_compartimentos} compartimentos): {total_capacity}\n")
            f.write(f"Ocupação Global: {ocupacao_global:.2f}%\n")
            f.write(f"Número total de caixas: {num_caixas}\n")
            f.write(f"Gap: {model.MIPGap*100:.6f}%\n")
            f.write(f"Tempo: {model.Runtime:.6f} s\n")
            
            f.write("\n--- Detalhes por compartimento ---\n")
            for k in range(num_compartimentos):
                vol_k = sum(boxes[i][0]*boxes[i][1]*boxes[i][2] for (k_,i,p,q,r) in x 
                           if k_==k and x[k_,i,p,q,r].X > 0.5)
                f.write(f"compartimento {k}: {vol_k:.2f} vol ({vol_k/(L*W*H)*100:.1f}%)\n")
        else:
            f.write("Nenhuma solução viável encontrada.\n")