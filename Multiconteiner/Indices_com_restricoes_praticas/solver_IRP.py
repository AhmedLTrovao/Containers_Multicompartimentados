# solver.py
import gurobipy as gp
from gurobipy import GRB

def gerar_coordenadas_normais(dimensao_maxima, dimensoes_caixas):
    """Generates normal patterns of coordinates to reduce the MIP search space."""
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
    model = gp.Model("MultiCompartment_Lateral_Multidrop_Fundo")
    
    # =========================================================================
    # 1. Extração de Tipos Únicos, Parâmetros e IDs Reais
    # =========================================================================
    tipos_caixas = []
    mapa_tipos = {}
    demanda = {}      # demanda[c][i] = qtd
    deltas = {}       # deltas[c][i] = delta_x
    
    # Captura a lista real de IDs presentes no arquivo para evitar KeyError
    lista_id_clientes = [cl["id_cliente"] for cl in clientes]
    
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
            if assinatura not in mapa_tipos:
                mapa_tipos[assinatura] = idx_tipo
                tipos_caixas.append({
                    "id": idx_tipo, "dims": dims, "peso": peso, "sigma": sigma
                })
                idx_tipo += 1
            
            i = mapa_tipos[assinatura]
            demanda[c][i] = demanda[c].get(i, 0) + item["qtd"]
            deltas[c][i] = item["delta_x"]
            
    num_compartimentos = len(compartimentos)
    
    X_coords_comp = {}
    Y_coords_comp = {}
    Z_coords_comp = {}
    x = {} # Dicionário de variáveis de decisão x[k, c, i, p, q, r]
    
    O_X = {}
    O_Y = {}
    
    # Big-M Geométrico Geral
    M = sum(comp[0] for comp in compartimentos) + 100 

    # =========================================================================
    # 2. Criação de Variáveis com Varredura Direcionada ao Fundo (Eixo X)
    # =========================================================================
    for k, (L_k, W_k, H_k) in enumerate(compartimentos):
        # Determinação dos Offsets Globais e Orientação Espelhada
        if k % 2 == 0:
            O_X[k] = 0
            is_even = True  # Lado Esquerdo (Porta na origem X=0, Fundo em X=L_k)
        else:
            O_X[k] = compartimentos[k-1][0]
            is_even = False # Lado Direito (Fundo na origem X=O_X, Porta em X=O_X+L_k)
            
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
        
        for c in lista_id_clientes:
            for i in demanda[c].keys():
                li, wi, hi = tipos_caixas[i]["dims"]
                
                # Filtragem de coordenadas válidas para o tamanho físico da caixa
                X_ki = [p for p in X_coords_comp[k] if p <= O_X[k] + L_k - li]
                Y_ki = [q for q in Y_coords_comp[k] if q <= O_Y[k] + W_k - wi]
                Z_ki = [r for r in Z_coords_comp[k] if r <= H_k - hi]
                
                # INVERSÃO DE VARREDURA: Força o solver a testar o fundo do caminhão primeiro
                if is_even:
                    X_ki_ordenado = sorted(X_ki, reverse=True) # Começa do fundo (direita) para a porta (esquerda)
                else:
                    X_ki_ordenado = sorted(X_ki)               # Começa do fundo (esquerda) para a porta (direita)
                
                for p in X_ki_ordenado:
                    for q in Y_ki:
                        for r in Z_ki:
                            x[k, c, i, p, q, r] = model.addVar(vtype=GRB.BINARY, name=f"x_k{k}_c{c}_i{i}_{p}_{q}_{r}")

    # Variáveis contínuas de limite do Multidrop por compartimento e cliente
    L_vars = {}
    for k in range(num_compartimentos):
        for c in lista_id_clientes:
            L_vars[k, c] = model.addVar(vtype=GRB.CONTINUOUS, name=f"L_{k}_{c}")

    model.update()

    # =========================================================================
    # 3. Função Objetivo Multicritério (Volume Máximo + Atração Física pelo Fundo)
    # =========================================================================
    # Objetivo Principal: Maximizar o volume de carga empacotada
    volume_expr = gp.quicksum(
        (tipos_caixas[i]["dims"][0] * tipos_caixas[i]["dims"][1] * tipos_caixas[i]["dims"][2]) * x[k, c, i, p, q, r]
        for (k, c, i, p, q, r) in x
    )
    
    # Objetivo Secundário (Desempate): Dar pequenos bônus para caixas encostadas no fundo
    fator_atracao = 0.00001
    posicao_expr = []
    
    for (k, c, i, p, q, r) in x:
        if k % 2 == 0:
            # Lado Esquerdo: Fundo está no X maior. Maximizar p.
            posicao_expr.append(p * fator_atracao * x[k, c, i, p, q, r])
        else:
            # Lado Direito: Fundo está no X menor. Minimizar p (invertendo sinal para o Maximize).
            posicao_expr.append(-p * fator_atracao * x[k, c, i, p, q, r])
            
    model.setObjective(volume_expr + gp.quicksum(posicao_expr), GRB.MAXIMIZE)

    # =========================================================================
    # 4. Restrições Fundamentais Geométricas e de Demanda
    # =========================================================================
    # 4.1. Não sobreposição Par a Par (Overlap tridimensional dentro do mesmo compartimento)
    chaves_x = list(x.keys())
    for idx_a in range(len(chaves_x)):
        k_a, c_a, i_a, p_a, q_a, r_a = chaves_x[idx_a]
        l_a, w_a, h_a = tipos_caixas[i_a]["dims"]
        
        for idx_b in range(idx_a + 1, len(chaves_x)):
            k_b, c_b, i_b, p_b, q_b, r_b = chaves_x[idx_b]
            if k_a != k_b:
                continue 
                
            l_b, w_b, h_b = tipos_caixas[i_b]["dims"]
            
            if (p_a < p_b + l_b and p_a + l_a > p_b and
                q_a < q_b + w_b and q_a + w_a > q_b and
                r_a < r_b + h_b and r_a + h_a > r_b):
                model.addConstr(x[k_a, c_a, i_a, p_a, q_a, r_a] + x[k_b, c_b, i_b, p_b, q_b, r_b] <= 1)

    # 4.2. Atendimento estrito ou parcial da Demanda por Cliente/Item
    for c in lista_id_clientes:
        for i in demanda[c].keys():
            demand_vars = [x[k, c_, i_, p, q, r] for (k, c_, i_, p, q, r) in x if c_ == c and i_ == i]
            if demand_vars:
                model.addConstr(gp.quicksum(demand_vars) <= demanda[c][i], name=f"Demanda_c{c}_i{i}")

    # =========================================================================
    # 5. Restrições de Multidrop Lateral Espelhado (Eixo X) - CORRIGIDO
    # =========================================================================
    for k, (L_k, W_k, H_k) in enumerate(compartimentos):
        is_even = (k % 2 == 0)
        
        # Big-M calibrado especificamente para o TAMANHO DESTE COMPARTIMENTO
        M_local = L_k + 5 
        
        for idx_c, c in enumerate(lista_id_clientes):
            model.addConstr(L_vars[k, c] >= O_X[k])
            model.addConstr(L_vars[k, c] <= O_X[k] + L_k)
            
            # Vinculação sequencial da rota de entrega (Precedência das barreiras)
            if idx_c > 0:
                c_anterior = lista_id_clientes[idx_c - 1]
                if is_even: 
                    model.addConstr(L_vars[k, c_anterior] <= L_vars[k, c])
                else:       
                    model.addConstr(L_vars[k, c_anterior] >= L_vars[k, c])
            
            for i in demanda[c].keys():
                li = tipos_caixas[i]["dims"][0]
                delta_val = deltas[c][i]
                
                vars_caixa = [(p, q, r) for (k_, c_, i_, p, q, r) in x if k_ == k and c_ == c and i_ == i]
                
                for (p, q, r) in vars_caixa:
                    var_x = x[k, c, i, p, q, r]
                    if is_even:
                        # Lado Esquerdo: Garante que a caixa fique ANTES da barreira do seu cliente
                        model.addConstr((p + li) <= L_vars[k, c] + M_local * (1 - var_x))
                        # Garante que ela fique DEPOIS da barreira do cliente anterior (com a folga delta)
                        if idx_c > 0:
                            c_anterior = lista_id_clientes[idx_c - 1]
                            model.addConstr(p >= L_vars[k, c_anterior] + delta_val - M_local * (1 - var_x))
                    else:
                        # Lado Direito: Espelhamento matemático invertido
                        model.addConstr(p >= L_vars[k, c] - M_local * (1 - var_x))
                        if idx_c > 0:
                            c_anterior = lista_id_clientes[idx_c - 1]
                            model.addConstr((p + li) <= L_vars[k, c_anterior] - delta_val + M_local * (1 - var_x))

    # =========================================================================
    # 6. Restrições Práticas e de Engenharia de Carga
    # =========================================================================
    # 6.1. Estabilidade Vertical Avançada (Suporte por Área de Contato Mínima)
    if stabv:
        # Defina a porcentagem de suporte necessária (ex: 0.75 = 75% da base precisa de apoio)
        # Se quiser apoio 100% perfeito (totalmente sólida embaixo), mude para 1.0
        alpha_suporte = 0.95 
        
        for (k, c, i, p, q, r) in x:
            if r > 0:  # Caixas acima do chão do caminhão
                li, wi, hi = tipos_caixas[i]["dims"]
                area_base_superior = li * wi
                
                # Lista de tuplas: (área_de_contato, variável_da_caixa_de_baixo)
                suportes_validos = []
                
                for (k_b, c_b, i_b, p_b, q_b, r_b), var_b in x.items():
                    # Verifica se a caixa B está no mesmo compartimento e exatamente no teto tocando a base da caixa atual
                    if k_b == k and r_b + tipos_caixas[i_b]["dims"][2] == r:
                        l_b, w_b, _ = tipos_caixas[i_b]["dims"]
                        
                        # Calcula a intersecção geométrica nos eixos X e Y
                        intersec_x = max(0, min(p + li, p_b + l_b) - max(p, p_b))
                        intersec_y = max(0, min(q + wi, q_b + w_b) - max(q, q_b))
                        area_contato = intersec_x * intersec_y
                        
                        if area_contato > 0:
                            suportes_validos.append((area_contato, var_b))
                
                if suportes_validos:
                    # Expressão linear: Soma das áreas das caixas que estão REALMENTE ATIVAS embaixo
                    soma_areas_ativas = gp.quicksum(area * var_b for area, var_b in suportes_validos)
                    
                    # Restrição: A área ativa embaixo precisa ser maior ou igual a alpha% da área de cima.
                    # Se a caixa atual for ligada (x[...] = 1), a restrição ativa. Se for 0, vira 0 <= 0 (neutra).
                    model.addConstr(
                        soma_areas_ativas >= alpha_suporte * area_base_superior * x[k, c, i, p, q, r],
                        name=f"Stabv_Area_{k}_{p}_{q}_{r}"
                    )
                else:
                    # Se não há absolutamente nenhuma caixa mapeada abaixo capaz de tocar, essa posição é proibida
                    model.addConstr(x[k, c, i, p, q, r] == 0, name=f"Stabh_Proibido_{k}_{p}_{q}_{r}")

    # 6.2. Estabilidade Horizontal Avançada (Foco no Fundo do Caminhão)
    if stabh:
        for (k, c, i, p, q, r) in x:
            li, wi, hi = tipos_caixas[i]["dims"]
            is_even = (k % 2 == 0)
            
            if is_even:
                # =============================================================
                # LADO ESQUERDO: O fundo está no limite máximo (X = O_X + L_k)
                # =============================================================
                # Se a caixa NÃO está tocando a parede do fundo (divisória central)...
                if p + li < O_X[k] + compartimentos[k][0]:
                    # ...ela PRECISA de uma caixa escorando-a exatamente à sua direita (X superior)
                    apoios_fundo_x = [
                        var_b for (k_b, c_b, i_b, p_b, q_b, r_b), var_b in x.items()
                        if k_b == k and p_b == p + li and  # Colada na quina direita
                           q_b < q + wi and q_b + tipos_caixas[i_b]["dims"][1] > q and
                           r_b < r + hi and r_b + tipos_caixas[i_b]["dims"][2] > r
                    ]
                    
                    if apoios_fundo_x:
                        model.addConstr(x[k, c, i, p, q, r] <= gp.quicksum(apoios_fundo_x), name=f"Stabh_X_Even_{k}_{p}_{q}_{r}")
                    else:
                        model.addConstr(x[k, c, i, p, q, r] == 0)
            else:
                # =============================================================
                # LADO DIREITO: O fundo está na origem local (X = O_X)
                # =============================================================
                # Se a caixa NÃO está tocando a parede do fundo (divisória central)...
                if p > O_X[k]:
                    # ...ela PRECISA de uma caixa escorando-a exatamente à sua esquerda (X inferior)
                    apoios_fundo_x = [
                        var_b for (k_b, c_b, i_b, p_b, q_b, r_b), var_b in x.items()
                        if k_b == k and p_b + tipos_caixas[i_b]["dims"][0] == p and  # Colada na quina esquerda
                           q_b < q + wi and q_b + tipos_caixas[i_b]["dims"][1] > q and
                           r_b < r + hi and r_b + tipos_caixas[i_b]["dims"][2] > r
                    ]
                    
                    if apoios_fundo_x:
                        model.addConstr(x[k, c, i, p, q, r] <= gp.quicksum(apoios_fundo_x), name=f"Stabh_X_Odd_{k}_{p}_{q}_{r}")
                    else:
                        model.addConstr(x[k, c, i, p, q, r] == 0)

    # 6.3. Limite de Resistência ao Esmagamento (Loadbearing com Escala Controlada de Big-M)
    if loadbearing:
        # M_peso calibrado dinamicamente com base estrita na soma de pesos da demanda atual
        M_peso = sum(cx["peso"] * sum(demanda[cli].get(cx["id"], 0) for cli in lista_id_clientes if cx["id"] in demanda[cli]) for cx in tipos_caixas) + 500
        for (k, c_b, i_b, p_b, q_b, r_b), var_b in x.items():
            sigma_b = tipos_caixas[i_b]["sigma"]
            l_b, w_b, h_b = tipos_caixas[i_b]["dims"]
            
            caixas_no_topo = []
            for (k_a, c_a, i_a, p_a, q_a, r_a), var_a in x.items():
                if k_a == k and r_a >= r_b + h_b:
                    l_a, w_a, _ = tipos_caixas[i_a]["dims"]
                    if p_a < p_b + l_b and p_a + l_a > p_b and q_a < q_b + w_b and q_a + w_a > q_b:
                        caixas_no_topo.append((tipos_caixas[i_a]["peso"], var_a))
            
            if caixas_no_topo:
                peso_acumulado = gp.quicksum(peso * v_a for peso, v_a in caixas_no_topo)
                model.addConstr(peso_acumulado <= sigma_b + M_peso * (1 - var_b), name=f"Load_{k}_{p_b}_{q_b}_{r_b}")

    # =========================================================================
    # 7. Parametrização e Otimização do Gurobi
    # =========================================================================
    model.Params.LogFile = arquivo_saida.replace(".txt", "_log.txt")
    model.Params.TimeLimit = tempo_limite
    model.optimize()

    # =========================================================================
    # 8. Escrita de Coordenadas Segura contra Timeouts/Infeasibility
    # =========================================================================
    with open(arquivo_saida, "w") as f:
        f.write(f"{num_compartimentos}\n")
        for (L_c, W_c, H_c) in compartimentos:
            f.write(f"{L_c} {W_c} {H_c}\n")
        
        # Só tenta ler o atributo .X se houver pelo menos uma solução inteira viável
        if model.SolCount > 0:
            for (k, c, i, p, q, r) in x:
                if x[k, c, i, p, q, r].X > 0.5:
                    li, wi, hi = tipos_caixas[i]["dims"]
                    f.write(f"{p} {q} {r} {li} {wi} {hi} {i} {c} {k}\n")
    
    # =========================================================================
    # 9. Geração de Relatório de Resumo Técnico
    # =========================================================================
    resumo_arquivo = arquivo_saida.replace(".txt", "_resumo.txt")
    volume_total = sum([l*w*h for (l,w,h) in compartimentos])
    
    with open(resumo_arquivo, "w") as f:
        f.write(f"Status da solucao: {model.Status}\n")
        if model.SolCount > 0:
            f.write(f"Objetivo final : {model.ObjVal/volume_total:.6f}\n")
            f.write(f"Gap de otimalidade: {model.MIPGap*100:.6f}%\n")
            f.write(f"Tempo de execucao: {model.Runtime:.6f}\n")
            f.write(f"Numero de nos explorados: {model.NodeCount}\n")
        else:
            f.write("Nenhuma solucao viavel encontrada dentro do tempo limite.\n")