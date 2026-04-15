'''
A diferença desse solver e do solver antigo é que esse considera os compartimentos deslocados de Wk entre si -
compartimentos iguais em tamanhos mas com posição relativa entre si
'''
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
    Resolve o problema de empacotamento para múltiplos compartimentos idênticos,
    alocando cada compartimento k sequencialmente no eixo Y (deslocamento k * W).
    """
    m = len(boxes)
    vol_container = L * W * H 
    
    # valor de cada caixa (relativo ao volume de um único compartimento)
    v = [(l*w*h)/vol_container for (l,w,h,b) in boxes]
    
    all_lengths = {l for (l,_,_,_) in boxes}
    all_widths  = {w for (_,w,_,_) in boxes}
    all_heights = {h for (_,_,h,_) in boxes}

    # 1. Gera as coordenadas base como se fosse um único compartimento
    X_coords = gerar_coordenadas_normais(L, all_lengths)
    Y_coords_base = gerar_coordenadas_normais(W, all_widths)
    Z_coords = gerar_coordenadas_normais(H, all_heights)

    model = gp.Model("MultiContainerGrid_Deslocado")
    model.Params.MIPFocus = 1

    # --- 1: Variáveis
    # x[k, i, p, q, r] = 1 se caixa 'i' está no compartimento 'k'
    # ATENÇÃO: a coordenada 'q' agora é GLOBAL (já inclui o deslocamento)
    x = {}

    for k in range(num_containers):
        # Desloca o eixo Y para o compartimento k (k=0 -> 0, k=1 -> W, k=2 -> 2W...)
        Y_coords_k = [q + (k * W) for q in Y_coords_base]
        
        for i in range(m):
            li, wi, hi, bi = boxes[i]
            
            valid_p = [c for c in X_coords if c <= L - li]
            # O limite máximo em Y para este compartimento é (k * W) + W - wi
            valid_q = [c for c in Y_coords_k if c <= (k * W) + W - wi]
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

    # --- 3: Restrições de não sobreposição
    print("Generating non-overlap constraints...")
    
    for k in range(num_containers):
        # Recupera as coordenadas Y específicas deste compartimento
        Y_coords_k = [q + (k * W) for q in Y_coords_base]
        
        # Filtra as variáveis apenas do compartimento k (Otimização de performance)
        vars_k = [(i, p, q, r) for (k_, i, p, q, r) in x if k_ == k]
        
        for xp in X_coords:
            for yq in Y_coords_k:
                for zr in Z_coords:
                    covering = []
                    
                    for (i, p, q, r) in vars_k:
                        li, wi, hi, _ = boxes[i]
                        # A verificação geométrica permanece idêntica, pois 'q' e 'yq' já estão no espaço global
                        if (p <= xp < p + li) and \
                           (q <= yq < q + wi) and \
                           (r <= zr < r + hi):
                            covering.append(x[k, i, p, q, r])
                    
                    if covering:
                        model.addConstr(gp.quicksum(covering) <= 1, name=f"no_overlap_k{k}_{xp}_{yq}_{zr}")

    # --- 4: Restrição de quantidade de caixas (Inventário)
    for i in range(m):
        # A soma de todas as posições em todos os compartimentos não pode exceder o estoque bi
        total_placed_i = gp.quicksum(x[k, i, p, q, r] for (k, i_, p, q, r) in x if i_ == i)
        model.addConstr(total_placed_i <= boxes[i][3], name=f"max_qty_type_{i}")


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
        # Header: O tamanho do Y global agora é W * num_containers
        f.write(f"{L} {W * num_containers} {H} {num_containers}\n")
        
        for (k, i, p, q, r) in x:
            if x[k, i, p, q, r].X > 0.5:
                li, wi, hi, bi = boxes[i]
                tipo = tipo_dict[(li, wi, hi)]
                cliente = 1 # Placeholder
                
                # Como 'q' já é global (ex: se k=1 e W=10, q já começa de 10), 
                # não precisamos somar nada na hora de imprimir!
                f.write(f"{p} {q} {r} {li} {wi} {hi} {tipo} {cliente} {k}\n")

    # Resumo
    resumo_arquivo = arquivo_saida.replace(".txt", "_resumo.txt")
    with open(resumo_arquivo, "w") as f:
        f.write(f"Status da solução: {model.Status}\n")
        if model.SolCount > 0:
            num_caixas = sum(1 for (k,i,p,q,r) in x if x[k,i,p,q,r].X > 0.5)
            total_capacity = (L * W * H) * num_containers
            volume_packed = model.ObjVal * (L * W * H) 
            
            ocupacao_global = (volume_packed / total_capacity) * 100

            f.write(f"Objetivo final (Soma v_i): {model.ObjVal:.6f}\n")
            f.write(f"Volume total carregado: {volume_packed:.2f}\n")
            f.write(f"Capacidade Total ({num_containers} containers): {total_capacity}\n")
            f.write(f"Ocupação Global: {ocupacao_global:.2f}%\n")
            f.write(f"Número total de caixas: {num_caixas}\n")
            f.write(f"Gap: {model.MIPGap*100:.6f}%\n")
            f.write(f"Tempo: {model.Runtime:.6f} s\n")
            
            f.write("\n--- Detalhes por Container ---\n")
            for k in range(num_containers):
                vol_k = sum(boxes[i][0]*boxes[i][1]*boxes[i][2] for (k_,i,p,q,r) in x 
                           if k_==k and x[k_,i,p,q,r].X > 0.5)
                f.write(f"Container {k}: {vol_k:.2f} vol ({vol_k/(L*W*H)*100:.1f}%)\n")
        else:
            f.write("Nenhuma solução viável encontrada.\n")
