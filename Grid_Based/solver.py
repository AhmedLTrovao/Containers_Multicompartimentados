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

def resolver_instancia(L, W, H, boxes, arquivo_saida):
    m = len(boxes)
    v = [(l*w*h)/(L*W*H) for (l,w,h,b) in boxes]
    all_lengths = {l for (l,_,_,_) in boxes}
    all_widths  = {w for (_,w,_,_) in boxes}
    all_heights = {h for (_,_,h,_) in boxes}

    X_coords = gerar_coordenadas_normais(L, all_lengths)
    Y_coords = gerar_coordenadas_normais(W, all_widths)
    Z_coords = gerar_coordenadas_normais(H, all_heights)

    model = gp.Model("GridBasedPosition")

    x = {}
    for i in range(m):
        li, wi, hi, bi = boxes[i]
        for p in [c for c in X_coords if c <= L - li]:
            for q in [c for c in Y_coords if c <= W - wi]:
                for r in [c for c in Z_coords if c <= H - hi]:
                    x[i,p,q,r] = model.addVar(vtype=GRB.BINARY, name=f"x_{i}_{p}_{q}_{r}")

    model.update()
    model.setObjective(gp.quicksum(v[i]*x[i,p,q,r] for (i,p,q,r) in x), GRB.MAXIMIZE)

    # Restrição de não sobreposição
    for xp in X_coords:
        for yq in Y_coords:
            for zr in Z_coords:
                covering = [x[i,p,q,r] for (i,p,q,r) in x
                            if (p <= xp < p+boxes[i][0])
                            and (q <= yq < q+boxes[i][1])
                            and (r <= zr < r+boxes[i][2])]
                if covering:
                    model.addConstr(gp.quicksum(covering) <= 1)

    # Limite de quantidade de caixas de cada tipo
    for i in range(m):
        model.addConstr(gp.quicksum(x[i,p,q,r] for (i_,p,q,r) in x if i_ == i) <= boxes[i][3])

    # Logs
    model.Params.LogFile = arquivo_saida.replace(".txt", "_log.txt")

    model.Params.TimeLimit = 3600

    model.optimize()

    tipo_dict = {}
    tipo_counter = 1
    for li,wi,hi,bi in boxes:
        dims = (li,wi,hi)
        if dims not in tipo_dict:
            tipo_dict[dims] = tipo_counter
            tipo_counter += 1

    with open(arquivo_saida, "w") as f:
        f.write(f"{L} {W} {H}\n")
        for (i,p,q,r) in x:
            if x[i,p,q,r].X > 0.5:
                li,wi,hi,bi = boxes[i]
                tipo = tipo_dict[(li,wi,hi)]
                cliente = 1
                f.write(f"{p} {q} {r} {li} {wi} {hi} {tipo} {cliente}\n")

        resumo_arquivo = arquivo_saida.replace(".txt", "_resumo.txt")
        with open(resumo_arquivo, "w") as f:
            f.write(f"Status da solução: {model.Status}\n")

            if model.SolCount > 0:
                # Número de caixas usadas
                num_caixas = sum(1 for (i,p,q,r) in x if x[i,p,q,r].X > 0.5)

                # Volume total (obj * volume total do contêiner)
                volume_total = model.ObjVal * (L * W * H)
                ocupacao_percent = model.ObjVal * 100

                f.write(f"Objetivo final (ocupação): {model.ObjVal:.6f}\n")
                f.write(f"Volume total carregado: {volume_total:.2f} unidades³ ({ocupacao_percent:.2f}% do contêiner)\n")
                f.write(f"Número total de caixas carregadas: {num_caixas}\n")
                f.write(f"Gap de otimalidade: {model.MIPGap*100:.6f}%\n")
                f.write(f"Tempo de execução: {model.Runtime:.6f} segundos\n")
                f.write(f"Número de nós explorados: {model.NodeCount}\n")

                # Indica se o limite de tempo foi atingido
                if abs(model.Runtime - model.Params.TimeLimit) < 1e-2:
                    f.write("Tempo limite atingido — solução ótima não garantida.\n")

            else:
                f.write("Nenhuma solução viável encontrada.\n")

