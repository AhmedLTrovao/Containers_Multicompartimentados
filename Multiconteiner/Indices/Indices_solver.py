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

def resolver_multi_container(L, W, H, boxes, num_containers, arquivo_saida):
    """
    Resolve o problema de empacotamento para múltiplos compartimentos idênticos
    
    Parâmetros:
        L, W, H: dimensões dos contaîneres
        boxes: lista de tuplas (l, w, h, quantidade).
        num_containers: inteiro, número de contaîneres
        arquivo_saida: nome de arquivo de output
    """
    m = len(boxes)
    
    # volume total de um container
    vol_container = L * W * H 
    
    # valor de cada caixa
    v = [(l*w*h)/vol_container for (l,w,h,b) in boxes]
    
    all_lengths = {l for (l,_,_,_) in boxes}
    all_widths  = {w for (_,w,_,_) in boxes}
    all_heights = {h for (_,_,h,_) in boxes}

    X_coords = gerar_coordenadas_normais(L, all_lengths)
    Y_coords = gerar_coordenadas_normais(W, all_widths)
    Z_coords = gerar_coordenadas_normais(H, all_heights)

    model = gp.Model("MultiContainerGrid")

    # --- 1: Variáveis
    # x[k, i, p, q, r] = 1 se caixa do tipo 'i' está no contaîner 'k' na coordenada (p,q,r)
    x = {}

    for k in range(num_containers):
        for i in range(m):
            li, wi, hi, bi = boxes[i]
            # filtrando coordenadas válidas para o tamanho específico da caixa
            valid_p = [c for c in X_coords if c <= L - li]
            valid_q = [c for c in Y_coords if c <= W - wi]
            valid_r = [c for c in Z_coords if c <= H - hi]
            
            for p in valid_p:
                for q in valid_q:
                    for r in valid_r:
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

    # --- 3: Restrições de não sobreposição dentro de cada container
    print("Generating non-overlap constraints...")
    # pra cada container e cada coordenada
    for k in range(num_containers):
        for xp in X_coords:
            for yq in Y_coords:
                for zr in Z_coords:
                    covering = []
                    # filtro caixas que pertencem ao container k
                    current_vars_k = [key for key in x.keys() if key[0] == k]
                    
                    # e checo se elas podem estar na coordenada
                    for (k_, i, p, q, r) in current_vars_k:
                        li, wi, hi, _ = boxes[i]
                        if (p <= xp < p + li) and \
                           (q <= yq < q + wi) and \
                           (r <= zr < r + hi):
                            covering.append(x[k_, i, p, q, r])
                    
                    # se há alguma caixa que possa ser colocada na coordenada, adiciona a restrição de que no máximo uma caixa pode estar nessa coordenada
                    if covering:
                        model.addConstr(gp.quicksum(covering) <= 1, name=f"no_overlap_k{k}_{xp}_{yq}_{zr}")

    # --- 4: Restrição de quantidade de caixas
    for i in range(m):
        # a quantidade de caixas do tipo i empacotadas tem que ser inferior ou i à quantidade disponivel de caixas do tipo i
        total_placed_i = gp.quicksum(x[k, i, p, q, r] for (k, i_, p, q, r) in x if i_ == i)
        model.addConstr(total_placed_i <= boxes[i][3], name=f"max_qty_type_{i}")

    # --- 5: Quebra de simetria
    # Since containers are identical, the solver might waste time swapping contents between Cont 1 and Cont 2.
    # We force Container k to be "more full" or equal to Container k+1 based on index (rough heuristic).
    # Ideally, we sort by volume, but simply ordering IDs helps.
    # for k in range(num_containers - 1):
    #     vol_k = gp.quicksum(v[i] * x[k,i,p,q,r] for (k_,i,p,q,r) in x if k_==k)
    #     vol_k_next = gp.quicksum(v[i] * x[k+1,i,p,q,r] for (k_,i,p,q,r) in x if k_==k+1)
    #     model.addConstr(vol_k >= vol_k_next)

    # --- 6: Resolver
    model.Params.TimeLimit = 3600
    model.optimize()

    # --- 7. Output ---
    
    # Helper for box types output
    tipo_dict = {}
    tipo_counter = 1
    for li, wi, hi, bi in boxes:
        dims = (li, wi, hi)
        if dims not in tipo_dict:
            tipo_dict[dims] = tipo_counter
            tipo_counter += 1

    with open(arquivo_saida, "w") as f:
        # Header: L W H num_containers
        f.write(f"{L} {W} {H} {num_containers}\n")
        
        for (k, i, p, q, r) in x:
            if x[k, i, p, q, r].X > 0.5:
                li, wi, hi, bi = boxes[i]
                tipo = tipo_dict[(li, wi, hi)]
                cliente = 1 # Placeholder
                # Added 'k' (container index) to the end of the line
                # Format: x y z l w h type client container_id
                f.write(f"{p} {q} {r} {li} {wi} {hi} {tipo} {cliente} {k}\n")

    # Resumo
    resumo_arquivo = arquivo_saida.replace(".txt", "_resumo.txt")
    with open(resumo_arquivo, "w") as f:
        f.write(f"Status da solução: {model.Status}\n")
        if model.SolCount > 0:
            num_caixas = sum(1 for (k,i,p,q,r) in x if x[k,i,p,q,r].X > 0.5)
            # Total volume available across ALL containers
            total_capacity = (L * W * H) * num_containers
            volume_packed = model.ObjVal * (L * W * H) # ObjVal is sum of relative volumes
            
            ocupacao_global = (volume_packed / total_capacity) * 100

            f.write(f"Objetivo final (Soma v_i): {model.ObjVal:.6f}\n")
            f.write(f"Volume total carregado: {volume_packed:.2f}\n")
            f.write(f"Capacidade Total ({num_containers} containers): {total_capacity}\n")
            f.write(f"Ocupação Global: {ocupacao_global:.2f}%\n")
            f.write(f"Número total de caixas: {num_caixas}\n")
            f.write(f"Gap: {model.MIPGap*100:.6f}%\n")
            f.write(f"Tempo: {model.Runtime:.6f} s\n")
            
            # Per container stats
            f.write("\n--- Detalhes por Container ---\n")
            for k in range(num_containers):
                vol_k = sum(boxes[i][0]*boxes[i][1]*boxes[i][2] for (k_,i,p,q,r) in x 
                           if k_==k and x[k_,i,p,q,r].X > 0.5)
                f.write(f"Container {k}: {vol_k:.2f} vol ({vol_k/(L*W*H)*100:.1f}%)\n")
        else:
            f.write("Nenhuma solução viável encontrada.\n")