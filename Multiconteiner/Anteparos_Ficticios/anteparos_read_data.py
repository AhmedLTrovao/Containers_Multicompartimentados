def read_data(arquivo):
    instancias = []
    with open(arquivo, "r") as f:
        # Filtra linhas vazias para evitar erros de leitura no final do arquivo
        linhas = [linha.strip() for linha in f if linha.strip()]
    
    i = 0
    while i < len(linhas):
        # 1. Cabeçalho: num_tipos (qtd de tipos de caixas), L, W, H
        parts = linhas[i].split()
        if not parts: break
        
        num_caixas = int(parts[0]) 
        L, W, H = map(int, parts[1:4])
        i += 1
        
        boxes = []
        # 2. Lê exatamente a quantidade de linhas de caixas definida no topo
        for _ in range(num_caixas):
            p_box = linhas[i].split()
            # vol, l, w, h, b, cliente
            # (Garante que a linha da caixa tenha pelo menos 6 colunas)
            if len(p_box) < 6:
                raise ValueError(f"Erro na linha {i+1}: Esperado 6 colunas para caixa, obtido {len(p_box)}")
            
            _, l_i, w_i, h_i, b_i, _ = map(float, p_box[:6])
            boxes.append((int(l_i), int(w_i), int(h_i), int(b_i)))
            i += 1
        
        # 3. A PRÓXIMA linha é obrigatoriamente a parede (Deve ter exatamente 7 colunas)
        p_wall = linhas[i].split()
        
        if len(p_wall) != 7:
            raise ValueError(
                f"ERRO DE INSTÂNCIA: A linha da parede (linha {i+1}) deve ter EXATAMENTE 7 colunas "
                f"(area, l, w, h, b, x, y). Encontrado: {len(p_wall)}"
            )
        
        valores_wall = list(map(float, p_wall))
        
        # Atribuição direta: se faltar algo, o Python levantará erro de índice aqui
        wall_data = {
            'l': int(valores_wall[1]),
            'w': int(valores_wall[2]),
            'h': int(valores_wall[3]),
            'b': int(valores_wall[4]),
            'x': int(valores_wall[5]),
            'y': int(valores_wall[6])
        }
        i += 1
        
        instancias.append({
            "L": L, "W": W, "H": H, 
            "boxes": boxes, 
            "wall": wall_data
        })
    
    return instancias