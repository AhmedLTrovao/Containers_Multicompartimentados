import gurobipy as gp
from gurobipy import GRB

def resolver_instancia_free_loading(L, W, H, boxes, arquivo_saida, tempo_limite=60
                                    ):
    # Expande cada tipo de caixa em unidades individuais
    boxes_expanded = []
    for l, w, h, b in boxes:
        for _ in range(int(b)):
            boxes_expanded.append((l, w, h))

    M = L + W + H + 1000
    m = len(boxes_expanded)
    vi = [(l*w*h)/(L*W*H) for l, w, h in boxes_expanded]

    # Cria modelo
    model = gp.Model("container_loading")
    p = model.addVars(m, vtype=GRB.BINARY, name="p")
    x = model.addVars(m, vtype=GRB.CONTINUOUS, lb=0, name="x")
    y = model.addVars(m, vtype=GRB.CONTINUOUS, lb=0, name="y")
    z = model.addVars(m, vtype=GRB.CONTINUOUS, lb=0, name="z")
    a = model.addVars(m, m, vtype=GRB.BINARY, name="a")
    b = model.addVars(m, m, vtype=GRB.BINARY, name="b")
    c = model.addVars(m, m, vtype=GRB.BINARY, name="c")
    d = model.addVars(m, m, vtype=GRB.BINARY, name="d")
    e = model.addVars(m, m, vtype=GRB.BINARY, name="e")
    f = model.addVars(m, m, vtype=GRB.BINARY, name="f")

    # Função objetivo
    model.setObjective(gp.quicksum(vi[i]*p[i] for i in range(m)), GRB.MAXIMIZE)

    # Restrições
    for i in range(m):
        li, wi, hi = boxes_expanded[i]
        # Dentro do contêiner
        model.addConstr(x[i]+li <= L + M*(1-p[i]))
        model.addConstr(y[i]+wi <= W + M*(1-p[i]))
        model.addConstr(z[i]+hi <= H + M*(1-p[i]))
        # Se p[i]=0, força posição em 0
        model.addConstr(x[i] <= M*p[i])
        model.addConstr(y[i] <= M*p[i])
        model.addConstr(z[i] <= M*p[i])

        for j in range(i+1, m):
            lj, wj, hj = boxes_expanded[j]
            model.addConstr(x[i]+li <= x[j] + (1-a[i,j])*M)
            model.addConstr(x[j]+lj <= x[i] + (1-b[i,j])*M)
            model.addConstr(y[i]+wi <= y[j] + (1-c[i,j])*M)
            model.addConstr(y[j]+wj <= y[i] + (1-d[i,j])*M)
            model.addConstr(z[i]+hi <= z[j] + (1-e[i,j])*M)
            model.addConstr(z[j]+hj <= z[i] + (1-f[i,j])*M)
            model.addConstr(a[i,j]+b[i,j]+c[i,j]+d[i,j]+e[i,j]+f[i,j] >= p[i]+p[j]-1)

    # Parâmetros
    model.Params.TimeLimit = tempo_limite
    model.Params.LogFile = arquivo_saida.replace(".txt","_log.txt")
    model.optimize()

    # Mapeamento tipos de caixa
    tipo_dict = {}
    tipo_counter = 1
    for box in boxes_expanded:
        if box not in tipo_dict:
            tipo_dict[box] = tipo_counter
            tipo_counter += 1

    # Salva solução
    with open(arquivo_saida, "w") as f:
        f.write(f"{L} {W} {H}\n")
        for i in range(m):
            if p[i].X > 0.5:
                li, wi, hi = boxes_expanded[i]
                f.write(f"{x[i].X} {y[i].X} {z[i].X} {li} {wi} {hi} {tipo_dict[boxes_expanded[i]]} 1\n")

    # Salva resumo
    resumo_arquivo = arquivo_saida.replace(".txt","_resumo.txt")
    with open(resumo_arquivo, "w") as f:
        f.write(f"Status: {model.Status}\n")
        if model.SolCount > 0:
            f.write(f"Objetivo: {model.ObjVal:.6f}\n")
            f.write(f"Gap: {model.MIPGap*100:.6f}%\n")
            f.write(f"Tempo de execução: {model.Runtime:.6f} s\n")
            f.write(f"Nós explorados: {model.NodeCount}\n")
        else:
            f.write("Nenhuma solução viável encontrada.\n")
