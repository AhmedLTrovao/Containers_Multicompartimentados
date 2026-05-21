# solver.py
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
    demanda = {}      
    deltas = {}       
    
    idx_tipo = 0
    for cl in clientes:
        c = cl["id_cliente"]
        demanda[c] = {}
        deltas[c] = {}
        for item in cl["itens"]:
            dims = item["dims"]
            peso = item["peso"]
            sigma = item["sigma"]
            
            assinatura = (dims, peso, sigma)
            if signature := assinatura not in mapa_tipos:
                mapa_tipos[assinatura] = idx_tipo
                tipos_caixas.append({
                    "id": idx_tipo, "dims": dims, "peso": peso, "sigma": sigma
                })
                idx_tipo += 1
            
            i = mapa_tipos[assinatura]
            demanda[c][i] = demanda[c].get(i, 0) + item["qtd"]
            deltas[c][i] = item["delta_x"]
            
    num_clientes = len(clientes)
    num_compartimentos = len(compartimentos)
    
    X_coords_comp = {}
    Y_coords_comp = {}
    Z_coords_comp = {}
    
    x = {} 
    O_X = {}
    O_Y = {}
    M = sum(comp[0] for comp in compartimentos) + 100 

    # Dicionário para rastrear quais variáveis ocupam cada espaço físico
    # Chave: (k, p, q, r, i) -> Variável Gurobi
    vars_por_posicao = {}

    for k, (L_k, W_k, H_k) in enumerate(compartimentos):
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
        
        X_coords_comp[k] = [x_ + O_X[k] for x_ in E_L_k]
        Y_coords_comp[k] = [y_ + O_Y[k] for y_ in E_W_k]
        Z_coords_comp[k] = E_H_k
        
        for c in range(num_clientes):
            for i in demanda[c].keys():
                li, wi, hi = tipos_caixas[i]["dims"]
                
                X_ki = [p for p in X_coords_comp[k] if p <= O_X[k] + L_k - li]
                Y_ki = [q for q in Y_coords_comp[k] if q <= O_Y[k] + W_k - wi]
                Z_ki = [r for r in Z_coords_comp[k] if r <= H_k - hi]
                
                for p in X_ki:
                    for q in Y_ki:
                        for r in Z_ki:
                            v = model.addVar(vtype=GRB.BINARY, name=f"x_k{k}_c{c}_i{i}_{p}_{q}_{r}")
                            x[k, c, i, p, q, r] = v
                            vars_por_posicao[(k, p, q, r, i)] = v

    L_vars = {}
    for k in range(num_compartimentos):
        for c in range(num_clientes):
            L_vars[k, c] = model.addVar(vtype=GRB.CONTINUOUS, name=f"L_{k}_{c}")

    model.update()

    # 3. Função Objetivo
    obj_expr = gp.quicksum(
        (tipos_caixas[i]["dims"][0] * tipos_caixas[i]["dims"][1] * tipos_caixas[i]["dims"][2]) * x[k, c, i, p, q, r]
        for (k, c, i, p, q, r) in x
    )
    model.setObjective(obj_expr, GRB.MAXIMIZE)

    # 4. Restrições Fundamentais Otimizadas (Overlap Par a Par)
    # Evita explosão de memória que acontecia na sua versão antiga
    chaves_x = list(x.keys())
    for idx_a in range(len(chaves_x)):
        k_a, c_a, i_a, p_a, q_a, r_a = chaves_x[idx_a]
        l_a, w_a, h_a = tipos_caixas[i_a]["dims"]
        
        for idx_b in range(idx_a + 1, len(chaves_x)):
            k_b, c_b, i_b, p_b, q_b, r_b = chaves_x[idx_b]
            if k_a != k_b:
                continue # Compartimentos diferentes não colidem
                
            l_b, w_b, h_b = tipos_caixas[i_b]["dims"]
            
            # Verifica se os domínios geométricos se interceptam
            if (p_a < p_b + l_b and p_a + l_a > p_b and
                q_a < q_b + w_b and q_a + w_a > q_b and
                r_a < r_b + h_b and r_a + h_a > r_b):
                model.addConstr(x[k_a, c_a, i_a, p_a, q_a, r_a] + x[k_b, c_b, i_b, p_b, q_b, r_b] <= 1)

    # 4.2. Demanda
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
            
            if c > 0:
                if is_even:
                    model.addConstr(L_vars[k, c-1] <= L_vars[k, c])
                else:
                    model.addConstr(L_vars[k, c-1] >= L_vars[k, c])
            
            for i in demanda[c].keys():
                li = tipos_caixas[i]["dims"][0]
                delta_val = deltas[c][i]
                vars_caixa = [(p, q, r) for (k_, c_, i_, p, q, r) in x if k_ == k and c_ == c and i_ == i]
                
                for (p, q, r) in vars_caixa:
                    var_x = x[k, c, i, p, q, r]
                    if is_even:
                        model.addConstr((p + li) <= L_vars[k, c] + M * (1 - var_x))
                        if c > 0:
                            model.addConstr(L_vars[k, c-1] - delta_val <= p + M * (1 - var_x))
                    else:
                        model.addConstr(L_vars[k, c] <= p + M * (1 - var_x))
                        if c > 0:
                            model.addConstr((p + li) <= L_vars[k, c-1] + delta_val + M * (1 - var_x))

    # =========================================================================
    # NOVAS: IMPLEMENTAÇÕES DAS RESTRIÇÕES PRÁTICAS PEDIDAS
    # =========================================================================
    
    # A. Estabilidade Vertical (Garante suporte por baixo)
    if stabv:
        for (k, c, i, p, q, r) in x:
            if r > 0: # Se não está no chão do compartimento
                # Procura caixas diretamente abaixo no nível r_inferior
                li, wi, _ = tipos_caixas[i]["dims"]
                suportes = []
                
                for (k_b, c_b, i_b, p_b, q_b, r_b), var_b in x.items():
                    if k_b == k and r_b + tipos_caixas[i_b]["dims"][2] == r:
                        l_b, w_b, _ = tipos_caixas[i_b]["dims"]
                        # Verifica se há intersecção de projeção horizontal
                        if p_b < p + li and p_b + l_b > p and q_b < q + wi and q_b + w_b > q:
                            suportes.append(var_b)
                
                if suportes:
                    model.addConstr(x[k, c, i, p, q, r] <= gp.quicksum(suportes), name=f"Stabv_{k}_{p}_{q}_{r}")
                else:
                    # Se não há nenhuma caixa teoricamente mapeada embaixo para suportar, essa posição é proibida
                    model.addConstr(x[k, c, i, p, q, r] == 0)

    # B. Estabilidade Horizontal (Garante contenção traseira/lateral basculante)
    if stabh:
        for (k, c, i, p, q, r) in x:
            li, wi, hi = tipos_caixas[i]["dims"]
            # Força o empacotamento encostado no fundo Y ou apoiado em outra caixa já colocada em Y
            if q > O_Y[k]: 
                apoios_y = [
                    var_b for (k_b, c_b, i_b, p_b, q_b, r_b), var_b in x.items()
                    if k_b == k and q_b + tipos_caixas[i_b]["dims"][1] == q and
                       p_b < p + li and p_b + tipos_caixas[i_b]["dims"][0] > p and
                       r_b < r + hi and r_b + tipos_caixas[i_b]["dims"][2] > r
                ]
                if apoios_y:
                    model.addConstr(x[k, c, i, p, q, r] <= gp.quicksum(apoios_y))
                else:
                    model.addConstr(x[k, c, i, p, q, r] == 0)

    # C. Loadbearing (Capacidade de carga e esmagamento pelo peso)
    if loadbearing:
        for (k, p_b, q_b, r_b, i_b), var_b in vars_por_posicao.items():
            sigma_b = tipos_caixas[i_b]["sigma"]
            l_b, w_b, h_b = tipos_caixas[i_b]["dims"]
            
            # Encontra todas as caixas que estão empilhadas em cima desta caixa 'b'
            caixas_no_topo = []
            for (k_a, c_a, i_a, p_a, q_a, r_a), var_a in x.items():
                if k_a == k and r_a >= r_b + h_b:
                    l_a, w_a, _ = tipos_caixas[i_a]["dims"]
                    # Verifica sobreposição de projeção
                    if p_a < p_b + l_b and p_a + l_a > p_b and q_a < q_b + w_b and q_a + w_a > q_b:
                        caixas_no_topo.append((tipos_caixas[i_a]["peso"], var_a))
            
            if caixas_no_topo:
                # O peso total acima não pode estourar o sigma da caixa de baixo
                peso_acumulado = gp.quicksum(peso * v_a for peso, v_a in caixas_no_topo)
                model.addConstr(peso_acumulado <= sigma_b + M * (1 - var_b), name=f"Load_{k}_{p_b}_{q_b}_{r_b}")

    # =========================================================================

    model.Params.LogFile = arquivo_saida.replace(".txt", "_log.txt")
    model.Params.TimeLimit = tempo_limite
    model.optimize()

    # 6. Escrita dos Resultados
    with open(arquivo_saida, "w") as f:
        f.write(f"{num_compartimentos}\n")
        for (L_c, W_c, H_c) in compartimentos:
            f.write(f"{L_c} {W_c} {H_c}\n")
        
        for (k, c, i, p, q, r) in x:
            if model.SolCount > 0 and x[k, c, i, p, q, r].X > 0.5:
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