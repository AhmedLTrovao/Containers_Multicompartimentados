import gurobipy as gp
from gurobipy import GRB
import os

def resolver_instancia(L, W, H, boxes, walls_list, arquivo_saida):
    """
    Solver de Otimização 3D com Paredes de Espessura Zero.
    - Lógica de Lâmina: Impede que caixas atravessem planos X ou Y.
    - Exportação Dupla: Gera arquivo para MATLAB (.txt) e Resumo (.csv).
    """
    
    # 1. Inicializar Modelo
    model = gp.Model("Solver_Espessura_Zero")
    model.Params.OutputFlag = 1
    model.Params.TimeLimit = 300 # 5 minutos

    # 2. Gerar Grade de Coordenadas (Passo de 1 em 1 para precisão)
    X_coords = list(range(L + 1))
    Y_coords = list(range(W + 1))
    Z_coords = list(range(H + 1))

    # 3. Criar Variáveis de Decisão com Filtro de Parede
    # x_var[i, p, q, r] = 1 se a caixa i for alocada na coordenada (p, q, r)
    x_var = {}
    
    print("Filtrando posições válidas conforme anteparos...")
    for i, (li, wi, hi, bi) in enumerate(boxes):
        for p in [p for p in X_coords if p <= L - li]:
            for q in [q for q in Y_coords if q <= W - wi]:
                for r in [r for r in Z_coords if r <= H - hi]:
                    
                    atravessa = False
                    for w in walls_list:
                        # Bloqueio Transversal (Plano fixo em X)
                        if w['l'] == 0:
                            # Se a caixa começa antes e termina depois da coordenada X da parede
                            if p < w['x'] < p + li:
                                atravessa = True; break
                        
                        # Bloqueio Longitudinal (Plano fixo em Y)
                        elif w['w'] == 0:
                            # Se a caixa começa antes e termina depois da coordenada Y da parede
                            if q < w['y'] < q + wi:
                                atravessa = True; break
                    
                    if not atravessa:
                        x_var[i, p, q, r] = model.addVar(vtype=GRB.BINARY, name=f"x_{i}_{p}_{q}_{r}")

    model.update()

    # 4. Função Objetivo: Maximizar Volume Total Carregado
    vol_total_container = L * W * H
    obj = gp.quicksum(((boxes[i][0] * boxes[i][1] * boxes[i][2]) / vol_total_container) * x_var[i, p, q, r]
                     for (i, p, q, r) in x_var.keys())
    model.setObjective(obj, GRB.MAXIMIZE)

    # 5. Restrição de Não Sobreposição (Fórmula da Imagem)
    # Garante que cada unidade de volume (s, t, u) tenha no máximo 1 objeto
    print("Adicionando restrições de sobreposição...")
    for s in range(L):
        for t in range(W):
            for u in range(H):
                covering = [x_var[i, p, q, r] for (i, p, q, r) in x_var.keys()
                            if (p <= s < p + boxes[i][0] and 
                                q <= t < q + boxes[i][1] and 
                                r <= u < r + boxes[i][2])]
                if covering:
                    model.addConstr(gp.quicksum(covering) <= 1)

    # 6. Restrição de Quantidade de Caixas
    for i in range(len(boxes)):
        qtd_max = boxes[i][3]
        model.addConstr(gp.quicksum(x_var[idx, p, q, r] for (idx, p, q, r) in x_var.keys() if idx == i) <= qtd_max)

    # 7. Otimização
    model.optimize()

    # 8. Exportação de Resultados
    if model.SolCount > 0:
        # --- ARQUIVO PARA MATLAB ---
        try:
            with open(arquivo_saida, "w") as f:
                f.write(f"{L} {W} {H}\n") # Dimensões do container
                
                cont_caixas = 0
                for chave in x_var.keys():
                    if x_var[chave].X > 0.5:
                        i, p, q, r = chave
                        li, wi, hi, _ = boxes[i]
                        f.write(f"{p} {q} {r} {li} {wi} {hi} 0\n")
                        cont_caixas += 1
                
                # Paredes (Tipo 1)
                for w in walls_list:
                    lx_vis = 0.05 if w['l'] == 0 else w['l']
                    wy_vis = 0.05 if w['w'] == 0 else w['w']
                    f.write(f"{w['x']} {w['y']} 0 {lx_vis} {wy_vis} {H} 1\n")
            
            print(f"Arquivo MATLAB gerado com {cont_caixas} caixas.")
            
        except Exception as e:
            print(f"Erro ao salvar arquivo MATLAB: {e}")

        # --- ARQUIVO DE RESUMO PARA O COMPILE_RESULTS ---
        try:
            arquivo_resumo = arquivo_saida.replace(".txt", "_resumo.txt")
            with open(arquivo_resumo, "w", encoding="utf-8") as f_res:
                f_res.write(f"Status da solução: {model.Status}\n")
                f_res.write(f"Objetivo final : {model.ObjVal}\n")
                
                vol_real = sum(boxes[c[0]][0]*boxes[c[0]][1]*boxes[c[0]][2] 
                               for c, v in x_var.items() if v.X > 0.5)
                f_res.write(f"Volume total carregado: {vol_real}\n")
                
                total_caixas = sum(1 for v in x_var.values() if v.X > 0.5)
                f_res.write(f"Número total de caixas carregadas: {total_caixas}\n")
                
                f_res.write(f"Gap de otimalidade: {model.MIPGap * 100}%\n")
                f_res.write(f"Tempo de execução: {model.Runtime}\n")
                f_res.write(f"Número de nós explorados: {model.NodeCount}\n")
            
            print(f"Resumo salvo em: {arquivo_resumo}")

        except Exception as e:
            print(f"Erro ao salvar resumo: {e}")
            
    else:
        print("Nenhuma solução ótima ou viável foi encontrada pelo Gurobi.")