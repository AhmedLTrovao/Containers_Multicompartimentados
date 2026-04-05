import gurobipy as gp
from gurobipy import GRB
import IIPP.restricoes_praticas.multidrop.restr as restr

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

def resolver_instancia(L, W, H, boxes, b, n, delta, arquivo_saida, sigma, peso, tempo_limite=3600, stabv = True, stabh = False, loadbearing = False):
    m = len(boxes)
    v = [(l*w*h)/(L*W*H) for (l,w,h) in boxes]
    all_lengths = {l for (l,_,_) in boxes}
    all_widths  = {w for (_,w,_) in boxes}
    all_heights = {h for (_,_,h) in boxes}
    M = L+W+H

    X_coords = gerar_coordenadas_normais(L, all_lengths)
    Y_coords = gerar_coordenadas_normais(W, all_widths)
    Z_coords = gerar_coordenadas_normais(H, all_heights)

    model = gp.Model("GridBasedPosition")
    
    x = {} # x_ikpqr
    for i in range(m):
        for k in range(n):
            li, wi, hi = boxes[i] # para cada cliente k precisamos entregar b_ik caixas do tipo i
            for p in [c for c in X_coords if c <= L - li]:
                for q in [c for c in Y_coords if c <= W - wi]:
                    for r in [c for c in Z_coords if c <= H - hi]:
                        x[i,k,p,q,r] = model.addVar(vtype=GRB.BINARY, name=f"x_{i}_{k}_{p}_{q}_{r}")
    
    L_ = {}
    for k in range(n):
        L_[k] = model.addVar(vtype=GRB.CONTINUOUS, name=f"L_{k}")

    model.update()
    model.setObjective(gp.quicksum(v[i]*x[i,k,p,q,r] for (i,k,p,q,r) in x), GRB.MAXIMIZE)



    # 12.29 - Não sobreposição
    for xp in X_coords:
        for yq in Y_coords:
            for zr in Z_coords:
                covering = [x[i,k,p,q,r] for (i,k,p,q,r) in x if (p <= xp <  p + boxes[i][0]) and (q <= yq < q+boxes[i][1]) and (r <= zr < r+boxes[i][2])]
                if covering:
                    model.addConstr(gp.quicksum(covering) <= 1)
                    

    # 12.30 - Disponibilidade
    for k in range(n):
        for i in range(m):
            # Filtra apenas as variáveis que pertencem ao par (i, k)
            demand_vars = [x[i_,k_,p,q,r] for (i_,k_,p,q,r) in x if i_==i and k_==k]
            if demand_vars:
                model.addConstr(gp.quicksum(demand_vars) <= b[k][i], name=f"Demanda_{i}_{k}")
    
         
    # Restrições de estabilidade 
    if(stabv):
        restr.addStabZ(model, boxes, L, W, H, m, n, X_coords, Y_coords, Z_coords, x)
        
    if(stabh):
        restr.addStabX(model, boxes, L, W, H, m, n, X_coords, Y_coords, Z_coords, x)
        restr.addStabY(model, boxes, L, W, H, m, n, X_coords, Y_coords, Z_coords, x)
        
    if(loadbearing):
        restr.addLoadbearing(model, boxes, L, W, H, m, n, X_coords, Y_coords, Z_coords, x, peso, sigma)
    
    # 12.33                
    for i in range(m):
        for k in range(n):
            li, wi, hi = boxes[i]
            
            X_i = [c for c in X_coords if c <= L - li]
            Y_i = [c for c in Y_coords if c <= W - wi]
            Z_i = [c for c in Z_coords if c <= H - hi]
            
            for p in X_i:
                for q in Y_i:
                    for r in Z_i:
                        model.addConstr((p+li)*x[i,k,p,q,r] <= L_[k])
    # 12.34
    for i in range(m):
        for k in range(1,n):
            li, wi, hi = boxes[i]
            
            X_i = [c for c in X_coords if c <= L - li]
            Y_i = [c for c in Y_coords if c <= W - wi]
            Z_i = [c for c in Z_coords if c <= H - hi]
            
            for p in X_i:
                for q in Y_i:
                    for r in Z_i:
                        model.addConstr(L_[k-1] - delta[k][i] <= p*x[i,k,p,q,r] + (1 - x[i,k,p,q,r]) * M)
                        
    # 12.35
    for k in range(1,n):
        model.addConstr(L_[k-1] <= L_[k])
    
    # 12.36
    for k in range(n):
        model.addConstr(0 <= L_[k])
        model.addConstr(L_[k] <= L)

    

    model.Params.LogFile = arquivo_saida.replace(".txt", "_log.txt")
    model.Params.TimeLimit = tempo_limite

    model.optimize()

    tipo_dict = {}
    tipo_counter = 1
    for li,wi,hi in boxes:
        dims = (li,wi,hi)
        if dims not in tipo_dict:
            tipo_dict[dims] = tipo_counter
            tipo_counter += 1

    with open(arquivo_saida, "w") as f:
        f.write(f"{L} {W} {H}\n")
        for (i,k,p,q,r) in x:
            if x[i,k,p,q,r].X > 0.5:
                li,wi,hi = boxes[i]
                tipo = tipo_dict[(li,wi,hi)]
                f.write(f"{p} {q} {r} {li} {wi} {hi} {tipo} {k+1}\n")

    resumo_arquivo = arquivo_saida.replace(".txt", "_resumo.txt")
    with open(resumo_arquivo, "w") as f:
        f.write(f"Status da solução: {model.Status}\n")
        if model.SolCount > 0:
            f.write(f"Objetivo final: {model.ObjVal:.6f}\n")
            f.write(f"Gap de otimalidade: {model.MIPGap*100:.6f}%\n")
            f.write(f"Tempo de execução: {model.Runtime:.6f} segundos\n")
            f.write(f"Número de nós explorados: {model.NodeCount}\n")
        else:
            f.write("Nenhuma solução viável encontrada.\n")