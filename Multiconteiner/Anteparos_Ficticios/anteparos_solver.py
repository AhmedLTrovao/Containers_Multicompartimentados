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

    menor_dim = min(dimensoes_caixas)

    coords_finais = [c for c in coordenadas if c <= dimensao_maxima - menor_dim]

    if 0 not in coords_finais:
        coords_finais.insert(0,0)

    return sorted(coords_finais)


def resolver_anteparos(L, W, H, boxes, num_walls, arquivo_saida):

    m = len(boxes)

    volume_container = L*W*H

    v = [(l*w*h)/volume_container for (l,w,h,b) in boxes]

    all_lengths = {l for (l,_,_,_) in boxes}
    all_widths  = {w for (_,w,_,_) in boxes}
    all_heights = {h for (_,_,h,_) in boxes}

    X_coords = gerar_coordenadas_normais(L, all_lengths)
    Y_coords = gerar_coordenadas_normais(W, all_widths)
    Z_coords = gerar_coordenadas_normais(H, all_heights)

    model = gp.Model("SingleVehicleWithWalls")

    # ------------------------
    # Variáveis
    # ------------------------

    x = {}

    for i in range(m):

        li, wi, hi, bi = boxes[i]

        valid_p = [c for c in X_coords if c <= L-li]
        valid_q = [c for c in Y_coords if c <= W-wi]
        valid_r = [c for c in Z_coords if c <= H-hi]

        for p in valid_p:
            for q in valid_q:
                for r in valid_r:

                    x[i,p,q,r] = model.addVar(
                        vtype=GRB.BINARY,
                        name=f"x_{i}_{p}_{q}_{r}"
                    )

    # paredes

    y = {}

    for p in X_coords:

        y[p] = model.addVar(
            vtype=GRB.BINARY,
            name=f"wall_{p}"
        )

    model.update()

    # ------------------------
    # Função objetivo
    # ------------------------

    model.setObjective(

        gp.quicksum(
            v[i] * x[i,p,q,r]
            for (i,p,q,r) in x
        ),

        GRB.MAXIMIZE
    )

    # ------------------------
    # Não sobreposição
    # ------------------------

    for xp in X_coords:
        for yq in Y_coords:
            for zr in Z_coords:

                covering = []

                for (i,p,q,r) in x:

                    li, wi, hi, _ = boxes[i]

                    if (
                        p <= xp < p+li and
                        q <= yq < q+wi and
                        r <= zr < r+hi
                    ):

                        covering.append(x[i,p,q,r])

                if covering:

                    model.addConstr(
                        gp.quicksum(covering) <= 1
                    )

    # ------------------------
    # Limite de caixas
    # ------------------------

    for i in range(m):

        model.addConstr(

            gp.quicksum(
                x[i,p,q,r]
                for (i_,p,q,r) in x if i_ == i
            )

            <= boxes[i][3]
        )

    # ------------------------
    # Número de paredes
    # ------------------------

    model.addConstr(

        gp.quicksum(y[p] for p in X_coords)

        == num_walls

    )

    model.addConstr(y[0] == 0)

    # ------------------------
    # Caixa não pode cruzar parede
    # ------------------------

    for (i,p,q,r) in x:

        li, wi, hi, _ = boxes[i]

        for w in X_coords:

            if p < w < p + li:

                model.addConstr(
                    x[i,p,q,r] <= 1 - y[w]
                )

    # ------------------------
    # Resolver
    # ------------------------

    model.Params.TimeLimit = 3600

    model.optimize()

    # ------------------------
    # Salvar solução
    # ------------------------

    with open(arquivo_saida, "w") as f:

        f.write(f"{L} {W} {H}\n")

        # caixas

        for (i,p,q,r) in x:

            if x[i,p,q,r].X > 0.5:

                li, wi, hi, _ = boxes[i]

                f.write(
                    f"{p} {q} {r} {li} {wi} {hi} 0\n"
                )

        # paredes

        for p in X_coords:

            if y[p].X > 0.5:

                f.write(
                    f"{p} 0 0 0.01 {W} {H} 1\n"
                )

    print("Solução salva em:", arquivo_saida)